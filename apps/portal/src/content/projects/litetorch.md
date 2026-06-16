---
title: "litetorch + litetune + sklite — AI Framework Toolkit"
date: 2025-03-01
summary: "A trio of educational ML infrastructure projects built from scratch: a neural network framework (inspired by PyTorch), a hyperparameter tuner (inspired by Ray Tune), and an ML preprocessing toolkit (inspired by scikit-learn)."
tags: ["Python", "Machine Learning", "PyTorch", "Deep Learning", "Systems Design"]
---

## Overview

Three educational ML infrastructure projects, each reimplementing a core part of the modern ML stack from first principles.

## The three components

**litetorch** — Neural network framework built from scratch inspired by PyTorch
- Implemented forward/backpropagation, autograd, and layer abstractions from scratch
- The goal: understand what PyTorch actually does, not just how to call it

**litetune** — Hyperparameter search and experiment tracking, inspired by Ray Tune
- Built trial management, search space definition, and result aggregation
- Mirrors Ray Tune's experiment lifecycle model

**sklite** — ML preprocessing toolkit inspired by scikit-learn
- Designed preprocessing pipelines and utility functions for educational clarity and extensibility

## Why build ML frameworks from scratch?

In the AI era, knowing how to call an API is table stakes. Understanding what's happening inside — the gradient flow, the trial scheduling, the data transformation pipeline — is what lets you debug, optimize, and architect ML systems that actually work in production.

## Links

- [GitHub](https://github.com/42-CC-RNCP)
