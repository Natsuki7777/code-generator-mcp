# MCP

## setup

1.env

```bash
cp .env.local .env
```

2.Docker Compose

```bash
docker-compose up -d
```

## cloude desktop での使用

```json
{
  "mcpServers": {
    "Code structure": {
      "command": "/Users/natsuki/.volta/bin/npx",
      "args": ["mcp-remote", "http://localhost:8081/sse"]
    },
    "File Reader": {
      "command": "/Users/natsuki/.volta/bin/npx",
      "args": ["mcp-remote", "http://localhost:8080/sse"]
    }
  }
}
```

## エラー時の対応

mcp-remote のエラー
[reference](https://www.npmjs.com/package/mcp-remote#:~:text=Wait%20%2DTail%2020-,Debugging,-If%20you%20encounter)

```bash
rm -rf ~/.mcp-auth
```
