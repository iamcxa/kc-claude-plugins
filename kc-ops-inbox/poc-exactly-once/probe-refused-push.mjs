import { readFileSync } from "node:fs";
import { appJwt } from "./inbox-core.mjs";

// node probe-refused-push.mjs <pem-path> <app-id> <installation-id> <owner/repo>
// Mints the inbox's own Actions-only token, then tries to create a branch with it; expects 403.
const [pem, appId, installation, repo] = process.argv.slice(2);
const api = "https://api.github.com";
const h = (token) => ({ authorization: `Bearer ${token}`, accept: "application/vnd.github+json", "user-agent": "ops-inbox-poc" });
const jwt = appJwt({ appId, privateKeyPem: readFileSync(pem, "utf8"), nowS: Math.floor(Date.now() / 1000) });
const minted = await (await fetch(`${api}/app/installations/${installation}/access_tokens`, {
  method: "POST", headers: h(jwt), body: JSON.stringify({ repositories: [repo.split("/")[1]], permissions: { actions: "write" } }),
})).json();
const sha = (await (await fetch(`${api}/repos/${repo}/git/ref/heads/master`, { headers: h(minted.token) })).json()).object?.sha ?? "0".repeat(40);
const res = await fetch(`${api}/repos/${repo}/git/refs`, {
  method: "POST", headers: h(minted.token), body: JSON.stringify({ ref: "refs/heads/ops/refused-push-probe", sha }),
});
console.log(JSON.stringify({ permissions: minted.permissions, pushStatus: res.status, pushBody: (await res.json()).message }));
