## SAI Canvas

Terminal UI toolkit that gives Claude Code a dedicated canvas for interactive operations.

- Status: active
- Updated: 2026-01-10
- Stack: JavaScript, Bun, tmux, Terminal UI
- Impact: Improved operator visibility and interaction speed when running multi-step agent tasks in terminal-heavy workflows.
- Visibility: Core repository is private. This entry summarizes architecture and working approach without exposing proprietary source.
- Tags: agent-ui, claude-code, terminal, tui

### Problem

CLI-first agent work can become opaque and hard to monitor when many operations run concurrently.

### Solution

Built a pane-based TUI approach that overlays structured interaction surfaces on top of existing terminal workflows.

### Highlights

- Introduces a terminal-native UI layer so agent workflows can be monitored in structured panes.
- Uses tmux-based composition to keep interaction fast, scriptable, and operationally lightweight.
- Focuses on making AI-assisted operations visible and controllable in real time.
