## Browser TUI

Browser-native terminal IDE shell with persistent tmux sessions and integrated file/edit workflows.

- Status: active
- Updated: 2026-02-18
- Stack: JavaScript, Node.js, tmux, Monaco
- Impact: Improved remote development ergonomics by reducing context switching across terminal, editor, and filesystem operations.
- Visibility: Core repository is private. This entry summarizes architecture and working approach without exposing proprietary source.

### Problem

Remote CLI work is fragmented across separate tools, making iterative operational tasks slower and more error-prone.

### Solution

Built a web workspace that unifies terminal panes, editing, and filesystem APIs behind one low-friction operational interface.

### Highlights

- Combines file explorer, Monaco editor, and multiple terminals in a single browser workspace.
- Uses hidden tmux-backed terminal persistence so sessions survive browser refreshes.
- Adds practical bridges like drag-drop uploads that immediately pipe usable paths into terminal flow.

