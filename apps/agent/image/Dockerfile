# claudecodeui + Claude Code CLI image.
# Build/push (ghcr.io/leayeh/claudecodeui) is performed separately; not built here.
FROM node:22-bookworm-slim

# Tools the agent needs at runtime: git + ssh client for clone/push, plus the Claude Code CLI.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git openssh-client ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Claude Code CLI on PATH (used by claudecodeui to spawn sessions).
RUN npm install -g @anthropic-ai/claude-code

# Build claudecodeui from upstream.
WORKDIR /app
RUN git clone --depth 1 https://github.com/siteboon/claudecodeui . \
    && npm ci \
    && npm run build

ENV HOME=/data \
    PORT=3008
EXPOSE 3008

# NOTE: confirm the production start script in upstream package.json before building.
CMD ["npm", "run", "server"]
