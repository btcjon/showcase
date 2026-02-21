## 3D Particle Manipulator

Interactive 3D particle experience used to prototype motion, camera, and behavior ideas quickly.

- Status: active
- Updated: 2025-11-19
- Stack: JavaScript, TypeScript, WebGL
- Impact: Reduced concept-to-demo time for interactive 3D explorations and made visual interaction decisions easier to validate early.
- Visibility: Core repository is private. This entry summarizes architecture and working approach without exposing proprietary source.
- Tags: 3d, frontend, interaction, prototype, webgl

### Problem

3D concept testing is usually slowed down by heavy setup and long feedback cycles before ideas can be evaluated.

### Solution

Implemented a lean Vite/TypeScript app that emphasizes direct parameter control and fast AI-assisted iteration for scene behaviors.

### Highlights

- Built as a rapid 3D concept lab where interaction ideas can be tested in-browser in minutes.
- Uses AI-assisted iteration to tune scene behavior and interaction states without heavy engine setup.
- Structured as a lightweight local + AI Studio workflow for fast demo publishing and feedback.
