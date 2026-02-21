## Google Ads Keyword & Bid Manager

Google Ads operations toolkit for keyword research, bid tuning, and campaign performance diagnostics.

- Status: active
- Updated: 2025-10-10
- Stack: Python, Google Ads API, OAuth2
- Impact: Improved speed and consistency of keyword/bid management decisions in Google Ads operations.
- Visibility: Core repository is private. This entry summarizes architecture and working approach without exposing proprietary source.
- Tags: ads-ops, google-ads, keyword-research, performance

### Problem

Campaign optimization required repetitive manual analysis and inconsistent bid decision workflows.

### Solution

Created CLI tools that unify keyword discovery, performance analysis, and guardrailed bid management actions.

### Highlights

- Supports keyword opportunity discovery with practical filters for volume, competition, and CPC.
- Implements bid-adjustment workflows with dry-run safety before live execution.
- Built around repeatable command-line routines for day-to-day campaign operations.
