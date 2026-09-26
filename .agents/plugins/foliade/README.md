# Foliade for Codex and Claude Code

Connect your Foliade account, send selected PDFs as private drafts, publish
catalogues on request, and read their statistics. **MCP is free, with or without an account.** Statistics, REST bulk uploads and
webhooks require Pro or higher.
No Python, uv, API key, or local MCP server is required for normal installation.

Version 1.2.0 exposes **34 hosted MCP tools**, including reader colours and
controls, brand themes, chapters, lead capture, all 13 interactive element types,
publication history, tracking links and digital shelves. Configuration uses
strict partial patches, preview mode and revision checks. Guest uploads retain
their existing limits; account features follow the effective plan.

Ask: “Read this catalogue's settings and match its reader to the cover colours.”
The assistant first calls `foliade_capabilities`, then reads the target settings,
applies the requested patch and verifies the result. Account-wide branding is a
separate operation. Interactive drafts have a separate publication step.

See the [configuration reference](https://foliade.gekkode.com/fr/developpeurs/mcp-foliade#configuration-mcp)
and the bundled skill for the tools and boundaries. Media imports, PDF
replacement, product-feed synchronization, API keys, REST webhooks, team and
billing management remain in the web application or REST API as applicable.

If only the original eight tools appear, refresh the host's MCP tools or restart
the session. The remote tools update on the server; an OAuth account connection
does not need to be replaced merely because the host cached an old tool list.

## Codex

### 1. Install the plugin

Run these commands in your computer's terminal, outside a Codex conversation:

```sh
codex plugin marketplace add https://gitlab.com/gekkode-public/foliade-connectors.git
codex plugin add foliade@foliade
```

### 2. Connect your Foliade account (optional for guests)

For a guest upload explicitly requested without an account, skip sign-in and
ask the assistant to check `foliade_account` in guest mode. Never use guest mode
as a fallback for a failed or expired account connection.

Installing the plugin does **not** sign you in. After installation, run this
command in the same terminal:

```sh
codex mcp login foliade
```

This opens Foliade in your browser. Sign in on `foliade.gekkode.com`, check that
the account email is correct, and authorize access. If the browser does not open,
open the link printed in the terminal yourself; do not share this sign-in link.
Wait for the terminal to confirm that login succeeded before continuing.
There is no API key to copy.

In the Codex app, **Connect** in Foliade's plugin details or MCP settings can
start the same authorization. UI labels vary by version.

### 3. Check the connection

Open a new Codex task. Inside the Codex conversation, enter:

```text
/mcp
```

This displays server status; it does **not** replace `codex mcp login foliade`.
Then follow [Verify before transferring](#verify-before-transferring) below to
check the connected account before sending a PDF.

If authentication is required, expired, or revoked, run `codex mcp login foliade`
again and authorize access in your browser. If Codex cannot find the `foliade`
server, complete step 1 first; do not add a duplicate server over the plugin.

[Guide en français](https://foliade.gekkode.com/fr/connecter-codex-flipbook)
· [English guide](https://foliade.gekkode.com/en/connecter-codex-flipbook)

### Alternative: direct MCP without the plugin

Without the plugin, the remote MCP can also be configured directly:

```sh
codex mcp add foliade --url https://foliade.gekkode.com/mcp
codex mcp login foliade
```

Choose one method to avoid duplicate servers. The plugin includes local PDF
transfer instructions; the direct MCP describes the same transfer protocol.
Run the add command first, then the login command, and approve the browser
authorization as in step 2. Start a new Codex task and verify the account.

## Claude Code

Run in Claude Code:

```text
/plugin marketplace add https://gitlab.com/gekkode-public/foliade-connectors.git
/plugin install foliade@foliade
```

Restart Claude Code, open `/mcp`, choose the Foliade server (possibly named
`plugin:foliade:foliade`), and choose **Authenticate**. Sign in to Foliade and approve
access. Terminal equivalents: `claude plugin marketplace add ...`, then
`claude plugin install foliade@foliade`.

Without the plugin:

```sh
claude mcp add --transport http --scope user foliade https://foliade.gekkode.com/mcp
```

Then authenticate from `/mcp`. User scope works across projects; project and
enterprise policies may restrict access. Do not install both methods.

## Verify before transferring

Ask: “Check my connected Foliade account, then list my catalogues. Do not modify anything.”
The assistant must use `foliade_account` and `foliade_list_catalogues` and report
the correct email. If Foliade is missing, reconnect it and start a new task. Never
substitute another service such as pCloud.

Then ask: “Create a PDF named test and send it to my Foliade account as a private draft.”
The plugin computes size/hash, transfers the selected file over HTTPS with a
short-lived upload ticket, finalizes it, and checks conversion status. The host
must allow local file access and outbound HTTPS. Approve only the intended PDF.

## Replacing an existing plugin installation

For an installation made before 1.1.0, remove the plugin and its marketplace
cache, then follow the installation instructions above. This does not delete
your Foliade catalogues. Do not merge an old Git clone into this repository.

Codex (terminal):

```sh
codex plugin remove foliade@foliade
codex plugin marketplace remove foliade
```

Claude Code:

```text
/plugin uninstall foliade@foliade
/plugin marketplace remove foliade
```

## Free limits and guest privacy

Before sending, the assistant must explain the notice returned by
`foliade_account`: 50 MB and 100 pages per PDF, one operation at a time,
10 upload attempts per rolling 24 hours for a free account (including replacements,
failed attempts and reservations). Website, MCP and REST share these safeguards.
Guest uploads share the website's 3 PDFs per IP per 24 hours; failed guest requests
are also limited to 10 attempts. Free processing is capped at 120 seconds,
512 MB per result, 2 GB stored per account; global capacity is finite and paid
work has priority. No automatic upload retry loops on quota/capacity errors.

Guest results remain private until explicit publication. Publications last
30 days, private management 30 minutes. Keep the private `manage_url` to attach
the catalogue to an account within those 30 days. Never share it publicly.
Free accounts keep 5 publications with a watermark, guaranteed for 12 months
then maintained by eligible reader activity or a manual 90-day confirmation.
REST discovery also retains 5 successful conversions per 30 days and 250 MB
of stored API packages. Account inventory and statistics are never public.

## Server and permissions

- Endpoint: `https://foliade.gekkode.com/mcp` (Streamable HTTP).
- OAuth authorization code + PKCE S256, rotating refresh tokens, no copied API key.
- Scopes: `foliade:read`, `foliade:write`, `foliade:publish`.
- Eight tools: account, list, prepare upload, finalize upload, status, publish,
  statistics, unpublish. [Technical reference](https://foliade.gekkode.com/en/developpeurs/mcp-foliade).
- Uploads start as private drafts. Publication is a separate action.
- Access tokens last one hour; the connection lasts up to 30 days. Reconnect when
  it expires. Revoke in Foliade → API → Connected assistants.
- This repository contains the connector only, no backend code, password or token.

## Distribution status

This is Foliade's own public marketplace. It is **not a claim of listing or
endorsement in the OpenAI or Anthropic official directories**, which require
separate review. These instructions target **Codex and Claude Code with local
file/shell tools**; they do not promise identical PDF attachment support in
ChatGPT, Claude web, Claude Desktop or Cowork.

## Migrating from 0.2.0

Remove the old manually configured `foliade` server, install this plugin, and
connect with OAuth. Revoke the old REST API key if unused elsewhere.
The Python script in `scripts/foliade_mcp.py` remains an advanced STDIO fallback
with its original five tools and API-key authentication. Neither current plugin
manifest launches it.

## Licence

The contents of this repository are released under the Apache License 2.0; see
`LICENSE` and `NOTICE`. The licence covers the connector only — manifests, MCP
configuration, skill, fallback script and documentation.

The Foliade service, its conversion engine, its API implementation and its data
are proprietary and are not distributed here. Using the service is governed by
its own [terms](https://foliade.gekkode.com/en/cgu). Section 6 of the licence
grants no trademark rights: a modified connector may not be published under the
Foliade or Gekkode names.

[Privacy](https://foliade.gekkode.com/en/confidentialite) ·
[Terms](https://foliade.gekkode.com/en/cgu) ·
[Support](mailto:contact@gekkode.com)
