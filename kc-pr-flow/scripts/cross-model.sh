#!/usr/bin/env bash
# cross-model.sh — deterministic helpers for kc-pr-review cross-model
# reconciliation (Step 5.5) + Gemini arbitration (Step 5.6).
#
# Designed to be `source`d by the skill at runtime so the tested path and the
# runtime path are the same code (no doc/behavior drift). Defines functions
# only; sets no shell options so it is safe to source. Unit tests live in
# cross-model.test.sh.
#
# Functions:
#   cross_model_tool_available <codex|gemini>   -> exit 0 if usable, 1 otherwise
#   cross_model_conflict_filter                 -> stdin TSV findings -> stdout dispute set
#   cross_model_arb_parse "<known-ids-csv>"     -> stdin Gemini output -> stdout id<TAB>verdict
#
# The semantic fingerprint *assignment* (deciding two findings describe the same
# issue) is agent work, NOT done here. These functions take fingerprints as
# given and perform only deterministic set algebra + output parsing.

# --- availability ----------------------------------------------------------
# Multi-signal: binary on PATH AND some auth signal. Uses only shell builtins so
# it is testable by overriding PATH / HOME / env in a subshell.
cross_model_tool_available() {
  local tool="${1:-}"
  command -v "$tool" >/dev/null 2>&1 || return 1
  case "$tool" in
    codex)
      [ -n "${CODEX_API_KEY:-}" ] && return 0
      [ -n "${OPENAI_API_KEY:-}" ] && return 0
      [ -f "${CODEX_HOME:-$HOME/.codex}/auth.json" ] && return 0
      return 1
      ;;
    gemini)
      [ -n "${GEMINI_API_KEY:-}" ] && return 0
      [ -n "${GOOGLE_API_KEY:-}" ] && return 0
      [ -n "${GOOGLE_GENAI_USE_VERTEXAI:-}" ] && return 0
      [ -f "$HOME/.gemini/oauth_creds.json" ] && return 0
      return 1
      ;;
    *)
      return 1
      ;;
  esac
}

# --- reconciliation conflict filter ----------------------------------------
# stdin  TSV: side  stance  fingerprint  file:line  severity  root  summary
#   side   in {claude, codex}   (Claude-side findings are collapsed to "claude")
#   stance in {flag, ok}        (flag = "this is a problem"; ok = "this is fine")
# stdout TSV: id  bucket  arbitrate  side  fingerprint  file:line  severity  root  summary
#   bucket    in {contradiction, claude-only, codex-only}  (agreement is suppressed)
#   arbitrate in {yes, no-overcap}                         (over-cap items are LISTED, not dropped)
# Rules (spec §9 R3/R4): materiality = contradiction OR severity>=MEDIUM OR root==CODE.
# Cap (CROSS_MODEL_ARB_CAP, default 10) bounds ONLY exclusive arbitration; contradictions exempt.
cross_model_conflict_filter() {
  local cap="${CROSS_MODEL_ARB_CAP:-10}"
  awk -F'\t' '
    function rank(s){
      if(s=="CRITICAL")return 5; if(s=="HIGH")return 4; if(s=="MEDIUM")return 3;
      if(s=="LOW")return 2; if(s=="NIT")return 1;
      printf("cross-model: unknown severity %s -> MEDIUM\n", s) > "/dev/stderr";
      return 3;
    }
    {
      if(NF!=7){ printf("cross-model: skip malformed row (NF=%d)\n",NF) > "/dev/stderr"; next }
      side=$1; stance=$2; fp=$3; fl=$4; sev=$5; root=$6; sum=$7;
      if(side!="claude" && side!="codex"){ printf("cross-model: skip bad side %s\n",side) > "/dev/stderr"; next }
      if(stance!="flag" && stance!="ok"){ printf("cross-model: skip bad stance %s\n",stance) > "/dev/stderr"; next }
      r=rank(sev);
      if(!(fp in seenfp)){ seenfp[fp]=1; order[++ng]=fp; minidx[fp]=NR; maxrank[fp]=0 }
      if(r>maxrank[fp]) maxrank[fp]=r;
      if(stance=="flag"){
        hasflag[fp]=1;
        if(side=="claude") cflag[fp]=1; else xflag[fp]=1;
        if(!(fp in rep)){ rep[fp]=1; rside[fp]=side; rfl[fp]=fl; rsev[fp]=sev; rroot[fp]=root; rsum[fp]=sum }
      } else { hasok[fp]=1 }
    }
    END{
      for(i=1;i<=ng;i++){
        fp=order[i];
        if(hasflag[fp] && hasok[fp]) bucket="contradiction";
        else if(hasflag[fp]){
          if(cflag[fp] && xflag[fp]) continue;          # agreement -> suppress (high confidence, not a dispute)
          else if(cflag[fp]) bucket="claude-only";
          else bucket="codex-only";
        } else continue;                                # only "ok", no flag -> nothing to arbitrate
        material = (bucket=="contradiction") || (maxrank[fp]>=3) || (rroot[fp]=="CODE");
        if(!material) continue;
        pri = (bucket=="contradiction")?0:1;
        printf("%d\t%d\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n",
               pri, maxrank[fp], minidx[fp], bucket, rside[fp], fp, rfl[fp], rsev[fp], rroot[fp], rsum[fp]);
      }
    }
  ' | sort -t$'\t' -k1,1n -k2,2nr -k3,3n | awk -F'\t' -v cap="$cap" '
    {
      id="D" (++i);
      bucket=$4;
      if(bucket=="contradiction") arb="yes";
      else { ne++; arb=(ne<=cap)?"yes":"no-overcap" }
      printf("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n", id, bucket, arb, $5, $6, $7, $8, $9, $10);
    }
  '
}

# --- arbitration output parser ---------------------------------------------
# arg1   comma-separated known dispute ids (opaque tokens generated per run)
# stdin  Gemini raw output (may contain noise / injected lines)
# stdout TSV: id  verdict   (verdict in REAL_BUG|FALSE_POSITIVE|UNCERTAIN|UNCHANGED)
# exit 0 normally; exit 3 ("arbitration failed") when fewer than half the known
# ids parse to a valid verdict — caller then skips arbitration, conflicts stay
# unresolved (fail-open to no-change, never to suppression). Only known ids are
# accepted (injected fake ARB lines with unknown ids are ignored); duplicate id
# -> first wins; missing or invalid -> UNCHANGED.
cross_model_arb_parse() {
  awk -v ids="${1:-}" '
    BEGIN{
      n=split(ids, a, ",");
      m=0;
      for(i=1;i<=n;i++){ if(a[i]!=""){ m++; kept[m]=a[i]; known[a[i]]=1 } }
      vv["REAL_BUG"]=1; vv["FALSE_POSITIVE"]=1; vv["UNCERTAIN"]=1;
    }
    $1=="ARB" {
      id=$2; verd=$3;
      if(!(id in known)) next;       # unknown id -> ignore (injection-safe)
      if(id in seen) next;           # duplicate -> first wins
      seen[id]=1;
      if(verd in vv){ result[id]=verd; parsed++ } else { result[id]="UNCHANGED" }
    }
    END{
      for(i=1;i<=m;i++){
        id=kept[i];
        v=(id in result)?result[id]:"UNCHANGED";
        print id "\t" v;
      }
      if(m>0 && parsed*2 < m) exit 3;
      exit 0;
    }
  '
}
