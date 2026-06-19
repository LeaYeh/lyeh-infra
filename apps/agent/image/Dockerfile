# claudecodeui + Claude Code CLI image.
# Build/push (ghcr.io/leayeh/claudecodeui) is performed separately; not built here.
FROM node:22-bookworm-slim

# Tools the agent needs at runtime: git + ssh client for clone/push, zsh as the
# interactive shell, less/vim/tree for editing & browsing, plus the Claude Code CLI.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git openssh-client ca-certificates curl zsh less vim tree \
    && rm -rf /var/lib/apt/lists/*

# Claude Code CLI on PATH (used by claudecodeui to spawn sessions).
RUN npm install -g @anthropic-ai/claude-code

# Build claudecodeui from upstream.
WORKDIR /app
RUN git clone --depth 1 https://github.com/siteboon/claudecodeui . \
    && npm ci \
    && npm run build

ENV HOME=/data \
    SERVER_PORT=3001 \
    HOST=0.0.0.0 \
    SHELL=/usr/bin/zsh
EXPOSE 3001

# Production start script (confirmed from upstream package.json): serves built client + API.
CMD ["npm", "run", "server"]
