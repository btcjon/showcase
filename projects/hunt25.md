## Hunt25 Voice-First Quest App

Voice-first interactive treasure hunt app with AI narration, personalized clues, and progression-driven gameplay.

- Status: active
- Updated: 2026-02-21
- Stack: Next.js 15, TypeScript, Anthropic / LLM Proxy, ElevenLabs TTS, Netlify
- Impact: Turned a one-off family activity into a reusable AI-powered event format with high engagement and repeat play value.
- Demo: https://hunt25.genr8ive.ai/
- Visibility: Core repository is private. This entry summarizes architecture and working approach without exposing proprietary source.

### Problem

Traditional scavenger hunts feel static and labor-intensive to run, with little personalization once play starts.

### Solution

Designed and shipped a live AI game master experience that adapts clue delivery, dialog, and pacing in real time.

### Highlights

- Built a voice-first game loop where an AI "Granddaddy" guides players through story-led clue progression.
- Combined real-time chat orchestration with ElevenLabs voice playback to create a cinematic, personalized experience.
- Implemented resilient deployment and API routing patterns so the app stays usable under provider quota and infra pressure.
