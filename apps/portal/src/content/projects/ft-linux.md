---
title: "ft_linux — Linux From Scratch"
date: 2025-09-01
summary: "Built a fully bootable Linux system from scratch — cross-compilation toolchain, kernel compilation, filesystem hierarchy, init system, and bootloader. Automated across 14 build stages."
tags: ["Linux", "Systems Programming", "C", "Kernel", "DevOps"]
---

## Overview

Built a fully bootable Linux system from scratch, covering every layer from cross-compilation toolchain to kernel configuration, filesystem hierarchy, init system, and bootloader. Follows LFS/BLFS/ALFS methodology with a custom automation layer.

## What I built

- Compiled a custom Linux kernel with hand-selected driver and filesystem configuration
- Built a two-phase cross-compilation toolchain (temporary + final) to produce a host-independent, self-contained Linux system
- Automated the full build pipeline (14 stages) via an ALFS-style bootstrap script with environment isolation and error recovery
- Designed partition layout, configured GRUB bootloader, SysV init, and udev for dynamic device management

## Why it matters

Building Linux from scratch forces you to understand every assumption modern systems make. It's the most direct way to learn what's actually happening beneath the abstractions — and to develop the judgment needed to reason about system-level architecture decisions.

## Links

- [GitHub](https://github.com/42-CC-RNCP/ft_linux)
