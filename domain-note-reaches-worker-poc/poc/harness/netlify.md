# Netlify

**Applicability:** A change or its tests compare two requests that should come from the same computer, or tie a browser session to a CLI or API request, while running through Netlify dev on `localhost`.

**Practice:** `localhost` can resolve to IPv4 (`127.0.0.1`) for one client and IPv6 (`[::1]`) for another, and the two requests can reach Netlify dev through different proxy hops. Run each browser case twice, with `localhost` explicitly resolved once to `127.0.0.1` and once to `[::1]`, independently of what the request client picks. Default resolution, or forcing both clients onto one family, does not cover the mixed case.

**Evidence:** In subspace-relay's same-computer pairing task, local validation passed three times with default address selection; the first CI run failed four same-computer browser cases. Forcing IPv4 reproduced all four; the explicit two-family runs then passed.
