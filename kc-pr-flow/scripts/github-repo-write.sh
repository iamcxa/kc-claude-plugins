#!/usr/bin/env bash
set -uo pipefail

github_repo_write_usage() {
  cat >&2 <<'EOF'
Usage:
  github-repo-write.sh preflight --repo OWNER/REPO [--worktree DIR]
  github-repo-write.sh preflight [--worktree DIR] [--remote NAME]
  github-repo-write.sh push --branch BRANCH [--set-upstream] [--force-with-lease]
                            [--worktree DIR] [--remote NAME]
  github-repo-write.sh push --tracked [--force-with-lease]
                            [--worktree DIR] [--remote NAME]
  github-repo-write.sh merge --repo OWNER/REPO --pr NUMBER --head SHA
                             [--method squash|merge|rebase] [--worktree DIR]
EOF
}

github_repo_write_die() {
  printf 'github-repo-write: %s\n' "$1" >&2
  exit "${2:-64}"
}

github_repo_identity_valid() {
  printf '%s' "$1" | grep -Eq '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$'
}

github_repo_identity_from_url() {
  local url="$1" path
  case "$url" in
    git@github.com:*) path=${url#git@github.com:} ;;
    ssh://git@github.com/*) path=${url#ssh://git@github.com/} ;;
    https://github.com/*) path=${url#https://github.com/} ;;
    http://github.com/*) path=${url#http://github.com/} ;;
    git://github.com/*) path=${url#git://github.com/} ;;
    *) return 1 ;;
  esac
  path=${path%/}
  path=${path%.git}
  github_repo_identity_valid "$path" || return 1
  printf '%s\n' "$path"
}

github_repo_repair_url() {
  local url="$1" canonical="$2"
  case "$url" in
    git@github.com:*) printf 'git@github.com:%s.git\n' "$canonical" ;;
    ssh://git@github.com/*) printf 'ssh://git@github.com/%s.git\n' "$canonical" ;;
    https://github.com/*) printf 'https://github.com/%s.git\n' "$canonical" ;;
    http://github.com/*) printf 'http://github.com/%s.git\n' "$canonical" ;;
    git://github.com/*) printf 'git://github.com/%s.git\n' "$canonical" ;;
    *) return 1 ;;
  esac
}

github_repo_canonical() {
  local requested="$1" worktree="$2" canonical
  github_repo_identity_valid "$requested" ||
    github_repo_write_die "invalid GitHub repository identity: $requested" 65
  canonical=$(cd "$worktree" && gh repo view "$requested" --json nameWithOwner --jq '.nameWithOwner') ||
    github_repo_write_die "cannot resolve the canonical GitHub identity for $requested" 69
  canonical=$(printf '%s' "$canonical" | tr -d '\r\n')
  github_repo_identity_valid "$canonical" ||
    github_repo_write_die "GitHub returned an invalid canonical identity for $requested: $canonical" 65
  printf '%s\n' "$canonical"
}

github_repo_push_preflight() {
  local worktree="$1" remote="$2" push_urls explicit_pushurl=false
  local remote_url configured canonical repair_url first_canonical='' label='' repair_command=''

  printf '%s' "$remote" | grep -Eq '^[A-Za-z0-9._-]+$' ||
    github_repo_write_die "invalid remote name" 65

  push_urls=$(git -C "$worktree" remote get-url --push --all "$remote" 2>/dev/null) ||
    github_repo_write_die "cannot read push URL for remote '$remote' from $worktree" 69
  [ -n "$push_urls" ] || github_repo_write_die "remote '$remote' has no push URL" 69
  if git -C "$worktree" config --get-all "remote.$remote.pushurl" >/dev/null 2>&1; then
    explicit_pushurl=true
  fi

  while IFS= read -r remote_url; do
    [ -n "$remote_url" ] || continue
    configured=$(github_repo_identity_from_url "$remote_url") ||
      github_repo_write_die "push URL for remote '$remote' is not a supported credential-free github.com URL" 65
    canonical=$(github_repo_canonical "$configured" "$worktree") || exit $?
    if [ "$(printf '%s' "$configured" | tr '[:upper:]' '[:lower:]')" != \
         "$(printf '%s' "$canonical" | tr '[:upper:]' '[:lower:]')" ]; then
      repair_url=$(github_repo_repair_url "$remote_url" "$canonical") ||
        github_repo_write_die "cannot construct a repair URL for remote '$remote'" 65
      if [ "$explicit_pushurl" = true ]; then
        label="configured push identity"
        repair_command="git remote set-url --push $remote '$repair_url' '$remote_url'"
      else
        label="configured remote identity"
        repair_command="git remote set-url $remote '$repair_url' '$remote_url'"
      fi
      printf '%s\n' \
        "github-repo-write: refusing push because the configured destination is stale" \
        "  $label: $configured" \
        "  canonical GitHub identity: $canonical" \
        "Repair the remote explicitly, inspect the change, then retry:" \
        "  $repair_command" >&2
      return 78
    fi
    if [ -n "$first_canonical" ] &&
       [ "$(printf '%s' "$first_canonical" | tr '[:upper:]' '[:lower:]')" != \
         "$(printf '%s' "$canonical" | tr '[:upper:]' '[:lower:]')" ]; then
      github_repo_write_die "remote '$remote' has multiple distinct GitHub push destinations; split the write explicitly" 78
    fi
    first_canonical=$canonical
  done <<EOF
$push_urls
EOF

  [ -n "$first_canonical" ] || github_repo_write_die "remote '$remote' has no usable push URL" 69
  printf '%s\n' "$first_canonical"
}

github_repo_tracked_refspec() {
  local worktree="$1" remote="$2" upstream prefix remote_branch
  upstream=$(git -C "$worktree" rev-parse --symbolic-full-name '@{upstream}' 2>/dev/null) ||
    github_repo_write_die "tracked push requires the checked-out branch to have an upstream" 65
  prefix="refs/remotes/$remote/"
  case "$upstream" in
    "$prefix"*) remote_branch=${upstream#"$prefix"} ;;
    *)
      github_repo_write_die "tracked upstream '$upstream' does not belong to remote '$remote'" 65
      ;;
  esac
  git -C "$worktree" check-ref-format "refs/heads/$remote_branch" >/dev/null 2>&1 ||
    github_repo_write_die "tracked upstream has an invalid remote branch: $upstream" 65
  printf 'HEAD:refs/heads/%s\n' "$remote_branch"
}

command=${1:-}
[ -n "$command" ] || {
  github_repo_write_usage
  exit 64
}
shift

worktree=.
remote=origin
repo=
branch=
pr=
head=
method=squash
set_upstream=false
force_with_lease=false
tracked=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --worktree)
      [ "$#" -ge 2 ] || github_repo_write_die "--worktree requires a value"
      worktree=$2
      shift 2
      ;;
    --remote)
      [ "$#" -ge 2 ] || github_repo_write_die "--remote requires a value"
      remote=$2
      shift 2
      ;;
    --repo)
      [ "$#" -ge 2 ] || github_repo_write_die "--repo requires a value"
      repo=$2
      shift 2
      ;;
    --branch)
      [ "$#" -ge 2 ] || github_repo_write_die "--branch requires a value"
      branch=$2
      shift 2
      ;;
    --pr)
      [ "$#" -ge 2 ] || github_repo_write_die "--pr requires a value"
      pr=$2
      shift 2
      ;;
    --head)
      [ "$#" -ge 2 ] || github_repo_write_die "--head requires a value"
      head=$2
      shift 2
      ;;
    --method)
      [ "$#" -ge 2 ] || github_repo_write_die "--method requires a value"
      method=$2
      shift 2
      ;;
    --set-upstream)
      set_upstream=true
      shift
      ;;
    --force-with-lease)
      force_with_lease=true
      shift
      ;;
    --tracked)
      tracked=true
      shift
      ;;
    --delete-branch)
      github_repo_write_die "--delete-branch is intentionally unsupported; clean up remote and local branches separately"
      ;;
    *) github_repo_write_die "unknown argument: $1" ;;
  esac
done

case "$command" in
  preflight)
    if [ -n "$branch" ] || [ -n "$pr" ] || [ -n "$head" ] ||
       [ "$set_upstream" = true ] || [ "$force_with_lease" = true ] || [ "$tracked" = true ]; then
      github_repo_write_die "preflight accepts only repository-selection arguments"
    fi
    if [ -n "$repo" ]; then
      github_repo_canonical "$repo" "$worktree"
    else
      github_repo_push_preflight "$worktree" "$remote"
    fi
    ;;
  push)
    tracked_refspec=
    [ -z "$repo" ] || github_repo_write_die "push selects its destination with --remote, not --repo"
    if [ -n "$pr" ] || [ -n "$head" ]; then
      github_repo_write_die "push does not accept --pr or --head"
    fi
    if [ "$tracked" = true ]; then
      [ -z "$branch" ] || github_repo_write_die "tracked push does not accept --branch"
      [ "$set_upstream" = false ] || github_repo_write_die "tracked push does not accept --set-upstream"
      tracked_refspec=$(github_repo_tracked_refspec "$worktree" "$remote") || exit $?
    else
      [ -n "$branch" ] || github_repo_write_die "push requires --branch or --tracked"
      git -C "$worktree" check-ref-format --branch "$branch" >/dev/null 2>&1 ||
        github_repo_write_die "invalid branch name: $branch"
    fi
    github_repo_push_preflight "$worktree" "$remote" >/dev/null || exit $?
    if [ "$tracked" = true ] && [ "$force_with_lease" = true ]; then
      git -C "$worktree" push --force-with-lease "$remote" "$tracked_refspec"
    elif [ "$tracked" = true ]; then
      git -C "$worktree" push "$remote" "$tracked_refspec"
    elif [ "$set_upstream" = true ] && [ "$force_with_lease" = true ]; then
      git -C "$worktree" push -u --force-with-lease "$remote" "$branch"
    elif [ "$set_upstream" = true ]; then
      git -C "$worktree" push -u "$remote" "$branch"
    elif [ "$force_with_lease" = true ]; then
      git -C "$worktree" push --force-with-lease "$remote" "$branch"
    else
      git -C "$worktree" push "$remote" "$branch"
    fi
    ;;
  merge)
    [ -n "$repo" ] || github_repo_write_die "merge requires --repo with the PR target repository"
    [ -z "$branch" ] || github_repo_write_die "merge does not accept --branch"
    if [ "$set_upstream" = true ] || [ "$force_with_lease" = true ] || [ "$tracked" = true ]; then
      github_repo_write_die "merge does not accept push flags"
    fi
    case "$pr" in
      '' | *[!0-9]*) github_repo_write_die "merge requires --pr with a positive integer" ;;
    esac
    [ "$pr" -gt 0 ] 2>/dev/null || github_repo_write_die "merge requires --pr with a positive integer"
    printf '%s' "$head" | grep -Eq '^[0-9a-fA-F]{40}([0-9a-fA-F]{24})?$' ||
      github_repo_write_die "merge requires --head with a full 40- or 64-character commit SHA"
    case "$method" in
      squash | merge | rebase) ;;
      *) github_repo_write_die "unsupported merge method: $method" ;;
    esac
    canonical=$(github_repo_canonical "$repo" "$worktree") || exit $?
    gh pr merge "$pr" --repo "$canonical" --match-head-commit "$head" "--$method"
    ;;
  *)
    github_repo_write_usage
    github_repo_write_die "unknown command: $command"
    ;;
esac
