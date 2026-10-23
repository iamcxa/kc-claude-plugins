import { appJwt } from "../../core/inbox-core.mjs";

export const apiBase = (env) => env.GITHUB_API_URL || "https://api.github.com";

export function client(env, token) {
  return async (method, path, body) => {
    const res = await fetch(`${apiBase(env)}${path}`, {
      method,
      signal: AbortSignal.timeout(30000),
      headers: {
        authorization: `Bearer ${token}`,
        accept: "application/vnd.github+json",
        "x-github-api-version": "2022-11-28",
        "content-type": "application/json",
        "user-agent": "kc-ops-inbox",
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    const text = await res.text();
    let json = null;
    try { json = text ? JSON.parse(text) : null; } catch { json = null; }
    return { status: res.status, json };
  };
}

// An installation token limited to one repository and the named permissions.
export async function mintToken(env, { clientId, privateKey, repo, permissions }) {
  const jwt = client(env, appJwt({ appId: clientId, privateKeyPem: privateKey, nowS: Math.floor(Date.now() / 1000) }));
  const inst = await jwt("GET", `/repos/${repo}/installation`);
  if (inst.status !== 200) throw new Error(`installation-lookup-${inst.status} from ${apiBase(env)}`);
  const res = await jwt("POST", `/app/installations/${inst.json.id}/access_tokens`, { repositories: [repo.split("/")[1]], permissions });
  if (res.status !== 201) throw new Error(`token-mint-${res.status} from ${apiBase(env)}`);
  return { token: res.json.token, permissions: res.json.permissions, repositories: (res.json.repositories ?? []).map((r) => r.full_name ?? r.name) };
}
