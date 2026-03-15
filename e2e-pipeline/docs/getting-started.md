# Getting Started

## Install

Via the [kc-claude-plugins](https://github.com/iamcxa/kc-claude-plugins) marketplace:

```bash
/plugin marketplace add iamcxa/kc-claude-plugins
/plugin install e2e-pipeline@kc-claude-plugins
```

## Prerequisites

- [agent-browser](https://github.com/nicobrinkkemper/agent-browser) CLI installed globally
- Node.js 20+ (required for the compiler and quarantine CLI)

## Quick Start

### 1. Map your app's UI

```
/e2e-map
```

Creates a YAML mapping of pages, elements, and selectors in `.claude/e2e/mappings/<app>.yaml`.

### 2. Run a test flow

```
/e2e-test <flow-name>
```

Executes a flow file from `.claude/e2e/flows/` against the mapped UI.

### 3. Walk through interactively

```
/e2e-walkthrough
```

Human-guided browser exploration with trace recording and auto-generated flow output.

### 4. Compile for CI

```
/e2e-compile --all
```

Compiles all flow YAML files to standalone bash scripts in `.claude/e2e/compiled/`, ready for headless CI execution without Claude Code.
