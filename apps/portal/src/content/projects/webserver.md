---
title: "webserver — HTTP/1.1 Server in C++"
date: 2024-06-01
summary: "Standards-compliant HTTP/1.1 web server implemented in C++ from scratch — non-blocking I/O event loop, request parsing, CGI execution, and virtual host support."
tags: ["C++", "Systems Programming", "HTTP", "Networking", "Linux"]
---

## Overview

Implemented a standards-compliant HTTP/1.1 web server in C++ from scratch, handling concurrent connections, request parsing, and static/dynamic content serving.

## What I built

- Built non-blocking I/O event loop handling concurrent HTTP connections using `poll`/`select`
- Implemented HTTP/1.1 request parsing, routing, and response generation
- Supported CGI execution, static file serving, and configurable virtual hosts

## What this taught me

Writing an HTTP server forces you to read RFCs carefully and handle edge cases that higher-level frameworks silently paper over: partial reads, connection timeouts, chunked transfer encoding, CRLF handling. It also makes you think carefully about I/O multiplexing — how to serve hundreds of connections efficiently with a single thread.

## Links

- [GitHub](https://github.com/LeaYeh/webserver)
