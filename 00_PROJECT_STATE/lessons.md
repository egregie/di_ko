# Lessons Learned — YM PROSKIN

## Misdiagnosis of EUtils Connectivity Failures (Phase 4.1)

### The Issue
During Phase 4, requests to NCBI's eutils endpoint (`eutils.ncbi.nlm.nih.gov`) failed with connection resolution errors. This was initially diagnosed as an environment-level network egress lock or DNS block, leading to the integration of a Google DNS-over-HTTPS (DoH) monkey-patch to bypass local hostname resolution.

### The Real Cause
Further investigation in Phase 4.2 revealed:
1. The local router/DNS server (`192.168.0.1`) has a bug or lookup failure when handling dual-stack DNS requests for `eutils.ncbi.nlm.nih.gov` (specifically AAAA / IPv6 queries).
2. The network interface has no routing path for IPv6 (`WinError 10051: A socket operation was attempted to an unreachable network`).
3. Python's default behavior tries to connect via IPv6 if DNS query returns dual-stack records, causing connections to hang and time out, throwing general socket errors.

### The Correct Fix
Instead of introducing external API-based DoH patches (which add external dependencies and fail if Google DNS is blocked), we rolled back the DoH monkey-patch and replaced it with a simple low-level standard override:
- Override `socket.getaddrinfo` to return *only* IPv4 addresses (`socket.AF_INET`) for `eutils.ncbi.nlm.nih.gov`.
- This completely avoids querying or connecting via IPv6, leading to instant connection success without mock seeding or DNS proxying.

### Prevention Rules
- Always test low-level TCP/IP connectivity (e.g. comparing IPv4 vs IPv6) before assuming an application-level DNS block.
- Do not introduce complex external workarounds (like DoH APIs) for issues that can be solved inside local socket configurations.
