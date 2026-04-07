# Dungeon of Echoes — Game Status & TODOs

## Current State

The game flow (`dungeon-of-echoes`) is a 14-node text adventure playable over WhatsApp. It runs on Groq's `llama-3.3-70b-versatile` and executes correctly: branching, variable tracking, condition evaluation all work.

### What Works

- **Flow structure**: start → message → agentic → message → agentic → condition → end. Validates cleanly (0 errors).
- **Game logic**: 6 agentic nodes narrate scenes, extract variables (`health`, `has_torch`, `has_key`), and route based on player choices.
- **Routing**: `complete`, `respond`, `inspect`, `crystal_cave`, `dark_descent` routes all work via edge sourceHandles.
- **Condition node**: `@health > 0` gates victory vs. game over path.
- **WhatsApp message delivery**: Text messages sent and received. Agentic responses arrive on WhatsApp.
- **Multi-message per turn**: Timestamp-based extraction sends ALL new assistant messages per turn (e.g., intro message + agentic response).

### What Does NOT Work

#### 1. WhatsApp Buttons — FIXED

`FlowExecutor` was prematurely clearing the action queue in its `turn.complete` finally block before `processFlowRequest` could read them. Removed `clearActions()` from all executor entry points — the caller now clears after reading. `ChannelService.extractOutboundMessages` merges message action data (buttons, media) with conversation text to build rich `OutboundMessage`s.

**Status**: Pipeline complete. Needs end-to-end testing.

#### 2. WhatsApp Images — needs scene assets

The pipeline works: `mediaUrl` on message nodes → `MessageAction` with media → `ChannelService` enriches `OutboundMessage` → `WhatsAppAdapter.buildMediaPayload()` sends via Meta Cloud API.

**Remaining blocker**: No actual images uploaded yet. Need scene images for: dungeon entrance, corridor fork, crystal cave, dark descent, treasure room, game over.

#### 3. `interactiveReplyId` Not Passed to Flow

WhatsApp button taps return a structured `id` (e.g., `"enter"`, `"crystal_path"`). The `WhatsAppAdapter.parseWebhook()` extracts this as `interactiveReplyId` on the `InboundMessage`. But `ChannelService.handleInbound()` doesn't pass it to `processFlowRequest` — only `text` is passed. The agentic node receives the button title text, not the structured ID.

**Fix**: Pass `interactiveReplyId` as `messageMetadata` to `processFlowRequest`, so the agentic node can route deterministically based on button ID instead of fuzzy text matching.

## Assets Needed

Scene images for each game location (can be AI-generated once offline, then uploaded via `POST /api/assets`):

| Scene | Description | Used in |
|-------|-------------|---------|
| `dungeon-entrance` | Crumbling stone dungeon entrance, blue glow, vines, ancient runes | `msg_intro` |
| `corridor-fork` | Stone corridor splitting into crystal-lit left path and dark stairs right | `msg_corridor` |
| `wall-discovery` | Tally marks scratched in stone, loose brick, rusty key | `msg_inspect_result` |
| `crystal-cave` | Shimmering blue crystals, crystal golem, distorted reflections | After `scene_crystal` |
| `dark-descent` | Pitch-black spiral staircase, shadow tendrils, iron door | After `scene_dark` |
| `treasure-room` | Ornate chest overflowing with gold, glowing amulet, crystal chamber | After `scene_treasure` |
| `game-over` | Fallen adventurer on dungeon floor, ethereal blue whispers | `msg_death` |
| `victory` | Triumphant adventurer holding glowing amulet, light breaking through | `msg_victory` |

## Infrastructure Built (Phases 1-5)

All platform-level work is complete and compiles cleanly:

| Component | Status | Files |
|-----------|--------|-------|
| Rich message types | Done | `backend/src/core/types/richMessage.ts` |
| OutboundMessage extension | Done | `backend/src/services/channels/types.ts` |
| MessageAction extension | Done | `backend/src/core/flow-executor/types/actions.ts` |
| WhatsApp adapter (buttons/images/lists) | Done | `backend/src/services/channels/adapters/WhatsAppAdapter.ts` |
| Message node schema (mediaUrl, buttons) | Done | `backend/flow-schema/src/schemas/message.ts` |
| MessageNodeExecutor (rich actions) | Done | `backend/src/core/flow-executor/executors/MessageNodeExecutor.ts` |
| NodeResultBuilder.addAction() | Done | `backend/src/core/flow-executor/utils/NodeResultBuilder.ts` |
| Asset storage API | Done | `backend/src/routes/assets.ts` |
| Image generation tool (seed) | Done | `backend/src/seeds/data/tools/image_generation.json` |
| ChannelService multi-message extraction | Done | `backend/src/services/channels/ChannelService.ts` |

## Unblocking Sequence

1. **Fix action clearing** — Stop clearing actions in `FlowExecutor` finally block. Let `processFlowRequest` read them, then clear. This unblocks buttons AND images for all text channels.
2. **Merge actions into outbound messages** — In `ChannelService.extractOutboundMessages`, merge `MessageAction` data (buttons, media) with conversation text to build rich `OutboundMessage`s.
3. **Upload scene images** — Generate offline, upload via asset API, reference URLs in flow message nodes' `mediaUrl` fields.
4. **Pass interactiveReplyId** — Forward button tap IDs from `ChannelService` to `processFlowRequest` as metadata for deterministic routing.
5. **Test full loop** — WhatsApp: intro with image + buttons → tap button → agentic scene → next message with image + buttons → etc.
