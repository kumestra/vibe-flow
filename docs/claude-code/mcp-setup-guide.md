# MCP Setup Guide for Claude Code

How to add, manage, and use MCP (Model Context Protocol) servers with Claude Code.

## What is MCP?

MCP servers are local processes that give Claude Code access to external tools and data sources (databases, APIs, design tools, etc.). They run on your machine and communicate with Claude Code over stdio.

```
Claude Code  →  local MCP process  →  external service (GitHub, PostgreSQL, etc.)
```

## Managing MCP Servers

```bash
claude mcp add <name> -- <command> [args]   # add a server
claude mcp list                              # list all servers
claude mcp get <name>                        # show server config
claude mcp remove <name>                     # remove a server
```

Options go before the server name, the command goes after `--`.

Restart Claude Code after adding or removing a server.

## PostgreSQL

### Start a PostgreSQL instance (Docker)

```bash
docker run --name my-postgres \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=123 \
  -p 5432:5432 \
  postgres
```

### Start pgAdmin (optional, web UI at http://localhost:5050)

```bash
docker run --name my-pgadmin \
  -p 5050:80 \
  -e 'PGADMIN_DEFAULT_EMAIL=user@domain.com' \
  -e 'PGADMIN_DEFAULT_PASSWORD=1234' \
  --link my-postgres:postgres \
  dpage/pgadmin4
```

When adding a server in pgAdmin, use hostname `postgres` (the link alias), port `5432`, username `test`, password `123`.

### Add the MCP server

```bash
claude mcp add postgres \
  -- npx -y @modelcontextprotocol/server-postgres postgresql://test:123@localhost:5432/test
```

Optional: create a read-only user for safer Claude access.

```sql
CREATE ROLE claude_ro WITH LOGIN PASSWORD 'readonly123';
GRANT CONNECT ON DATABASE test TO claude_ro;
GRANT USAGE ON SCHEMA public TO claude_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO claude_ro;
```

Then use it instead:

```bash
claude mcp add postgres \
  -- npx -y @modelcontextprotocol/server-postgres postgresql://claude_ro:readonly123@localhost:5432/test
```

## GitHub

```bash
claude mcp add github \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_yourTokenHere \
  -- npx -y @modelcontextprotocol/server-github@latest
```

Create a token at https://github.com/settings/tokens with `repo` and `read:org` scopes.

Note: Claude Code already has built-in GitHub support via the `gh` CLI (PRs, issues, CI checks). The MCP adds richer schema introspection but is optional for most workflows.

## Other Popular MCP Servers

| Server | Install command |
|---|---|
| Playwright (browser testing) | `claude mcp add playwright -- npx -y @anthropic-ai/mcp-playwright` |
| Brave Search | `claude mcp add brave -- npx -y @anthropic-ai/mcp-brave-search` |
| File System | `claude mcp add filesystem -- npx -y @anthropic-ai/mcp-filesystem /path/to/allowed/dir` |

Browse more at https://github.com/modelcontextprotocol/servers.

## Scopes

```bash
claude mcp add --scope user postgres -- ...     # personal, all projects (default)
claude mcp add --scope project postgres -- ...   # shared with team via .mcp.json
```

## Environment Variables

Pass secrets via `-e` to avoid hardcoding them:

```bash
claude mcp add postgres \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/mydb \
  -- npx -y @modelcontextprotocol/server-postgres
```

## Troubleshooting

- **Can't connect**: verify the underlying service is running first (e.g., `psql` for PostgreSQL, `gh auth status` for GitHub)
- **Config not taking effect**: restart Claude Code after changes
- **Server crashes**: run the MCP command manually in a terminal to see error output
