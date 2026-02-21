## ALS Clarity

Clinical decision-support workflow that helps neurologists differentiate ALS from look-alike conditions.

- Status: active
- Updated: 2026-02-05
- Stack: React, TypeScript, Convex, AI APIs
- Impact: Improved diagnostic workflow consistency and reduced manual synthesis burden during ALS-vs-mimic evaluations.
- Visibility: Core repository is private. This entry summarizes architecture and working approach without exposing proprietary source.

### Problem

ALS workups require synthesizing many test streams and mimic conditions under high uncertainty and time pressure.

### Solution

Built a structured diagnostic system combining test interpretation, criteria scoring, and research-backed differential workflows.

### Highlights

- Implements El Escorial criteria scoring and differential analysis against multiple ALS mimics.
- Integrates clinical test workflows with evidence lookup and structured diagnostic reporting.
- Designed as a clinician-facing decision-support flow, not a black-box prediction widget.

