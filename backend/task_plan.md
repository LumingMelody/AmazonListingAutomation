# Task Plan: P3 Task 2 BU2Ama Core Engine Integration (Service Adapter Layer)

## Goal
Implement a BU2Ama adapter layer with interface + factory, integrate Excel/FollowSell endpoints to use adapters, and deliver passing unit/integration tests following TDD.

## Current Phase
Phase 5

## Phases
### Phase 1: Requirements & Discovery
- [x] Understand user intent
- [x] Identify constraints and requirements
- [x] Document findings in findings.md
- **Status:** complete

### Phase 2: Test Design (TDD Red)
- [x] Identify adapter contracts and expected API behavior
- [x] Add failing unit tests for interface/factory/adapters
- [x] Add failing integration tests for Excel/FollowSell endpoint adapter usage
- **Status:** complete

### Phase 3: Adapter Implementation (TDD Green)
- [x] Create `EngineAdapter` interface
- [x] Implement `BU2AmaAdapter`
- [x] Implement `LocalFallbackAdapter`
- [x] Implement factory pattern for adapter selection
- **Status:** complete

### Phase 4: Endpoint Integration
- [x] Update Excel endpoint to use adapter abstraction
- [x] Update FollowSell endpoint to use adapter abstraction
- [x] Wire adapter configuration via app config
- **Status:** complete

### Phase 5: Verification & Delivery
- [x] Run relevant test suites
- [x] Fix regressions until all tests pass
- [x] Summarize changes and outcomes
- **Status:** complete

## Key Questions
1. What existing BU2Ama interaction points already exist in this codebase?
2. What adapter methods are minimally required by Excel and FollowSell workflows?
3. How should factory selection be configured and overridden in tests?

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Use strict TDD ordering (tests first) | Explicit user requirement and safer integration path |
| Start from plan + priority files before broader edits | User-specified priority and minimal-risk discovery |
| Implement external engine integration through HTTP API boundary | Avoid `app.*` namespace conflicts with BU2Ama project internals |
| In `auto` mode, require both path presence and external API health | Prevent regressions when path exists but service is offline |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| `503` in clean workflow tests due `auto` selecting unavailable external engine | 1 | Added external health probe in factory and fallback to local |

## Notes
- Do not alter unrelated existing changes.
- Reference BU2Ama implementation under `/Users/melodylu/PycharmProjects/BU2Ama/backend` for parity.
