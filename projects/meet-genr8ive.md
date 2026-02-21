## Genr8ive Meet

Meetings that don't suck: frictionless branded meeting flows with instant secure join links.

- Status: active
- Updated: 2026-02-21
- Stack: Cloudflare Workers, TypeScript, JaaS (Jitsi as a Service), JWT, Webhook Automation
- Impact: Reduced meeting setup friction and made recurring calls faster to launch, easier to share, and simpler to manage.
- Demo: https://meet.genr8ive.ai/
- Visibility: Core repository is private. This entry summarizes architecture and working approach without exposing proprietary source.

### Problem

Typical meeting flows break momentum with redirects, inconsistent links, and setup friction before people can actually talk.

### Solution

Implemented a meeting launcher and permanent-room architecture on meet.genr8ive.ai with signed URLs and embedded sessions.

### Highlights

- Built branded permanent room URLs on meet.genr8ive.ai so invites are frictionless and consistent.
- Embedded JaaS meetings directly in a custom domain experience to avoid redirect-heavy UX.
- Added signed join links, recording controls, and webhook hooks for production meeting operations.

