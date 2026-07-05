# Recent Changes

Running log of hand-driven changes to the NSE7 EF 7.6 site — the kind of stuff that doesn't fit in a commit message and would otherwise get lost between rebuilds. Newest on top.

---

## 2026-07-05

### Sort workflow — audio-podcast prompt awareness

Codified an existing-but-implicit behavior into the sort workflow in [CLAUDE.md](CLAUDE.md).

- The build already discovers audio-podcast prompts automatically: `discover_audio_prompts()` in [build.py](build.py) scans every `sessions/session-NN-*/completed-session/summary.txt` for a heading that starts with `AUDIO PODCAST PROMPT` and renders `audio-podcasts/index.html` from what it finds.
- Sort now explicitly greps each newly-moved summary for that section and reports the result in the sort table:
  - **Found** → `+ audio podcast prompt detected in session NN summary → audio-podcasts/index.html#panel-NN`
  - **Missing** → `- session NN summary has no AUDIO PODCAST PROMPT section — hub will show "coming soon"`
- No code change to `build.py` was needed — the discovery pipeline was already in place. The change is purely to the sort workflow docs in [CLAUDE.md](CLAUDE.md), adding a new step 10 (audio-podcast check) and renumbering the rebuild/report steps to 11 and 12.

### Session 21 nibble — lightbox on comic panels

Added click-to-expand behavior for the 7 comic-strip panels on [ospf-neighbor-states.html](sessions/session-21-ospf-areas-lsas-neighbors/nibbles/ospf-neighbor-states.html).

- Panel image hover → subtle 1.01× scale + `cursor: zoom-in` (discoverable without instructions).
- Click any panel → fullscreen `.lightbox-backdrop` fades up, image scales in from 0.96 → 1.0.
- Click the backdrop, click the enlarged image, or press `Esc` → smooth fade out (180 ms), overlay is removed from the DOM (no leftover listeners).
- One delegated click listener on `document` reads `.panel-art-img` targets — automatically covers panels added later without wiring.
- Implementation is contained: 6 new CSS rules (`.lightbox-backdrop`, `.lightbox-hint`, hover transform) + a `closeLightbox()` + `lightboxKey()` + one delegated listener appended to the existing `<script>` at the bottom of the file. No new library, no external dependency.

### Session 21 nibble — `<img>` references injected into panel placeholders

The nibble arrived using the "Style 2" pattern from the CLAUDE.md image-handling rules: `.panel-art` blocks with a `.panel-art-filename` marker and a `.panel-art-desc` line but **no actual `<img>`** — so the panels showed only the dashed placeholder card with a filename hint, even after the PNGs were generated.

Injected 7 `<img class="panel-art-img" src="images/s21-comic-NN-*.png">` tags (one per panel) with graceful degradation:

- **Image present** — `onload` adds `.has-image` to the parent `.panel-art`, which:
  - Removes the dashed border and background of the placeholder
  - Hides the filename hint and description text (they were meta-info for the missing state)
  - Leaves the "Show image prompt" toggle visible and left-aligned below the rendered comic
- **Image missing** — `onerror` removes the `<img>` entirely; the existing dashed placeholder card stays as-is (filename hint + description + prompt toggle), unchanged from before.

Injection was done via a one-shot Python script (regex over `<div class="panel-art">…<div class="panel-art-filename">images/([^<]+)</div>…<div class="panel-art-desc">([^<]+)</div>`) rather than 7 sequential Edits — per the CLAUDE.md multi-placeholder guidance.

### Session 21 nibble sorted

Moved from `sorting-hat/session-21-nibble-ospf-neighbor-states.html` → [sessions/session-21-ospf-areas-lsas-neighbors/nibbles/ospf-neighbor-states.html](sessions/session-21-ospf-areas-lsas-neighbors/nibbles/ospf-neighbor-states.html).

- File already used the correct "Style 3" prompt structure (`.prompt-content` hidden divs with a `.prompt-toggle` button), so no HTML rewrite was needed for the prompt content itself.
- Created [sessions/session-21-.../nibbles/images/](sessions/session-21-ospf-areas-lsas-neighbors/nibbles/images/) and extracted all 7 comic-panel prompts into `images/prompts.txt` (session 21 didn't have a nibble folder before).
- Session 21 itself has no `complete.html` yet — this nibble is standalone reference material until the full session is completed.
- Rebuild picked it up on the next `python3 build.py` (nibble count on [extras.html](extras.html) updates automatically).

---

## 2026-07-04

### `completed-sessions.html` grouped by phase

Rewrote `render_completed_hub()` in [build.py](build.py) so the completed study guides page groups cards by the eight PHASES rather than emitting one flat grid.

- Top intro block still shows the overall progress (`Completed Study Guides · X of Y`).
- Below it, one `<div class="anchor-section" id="phase-NN">` per phase that has at least one completed session:
  - `<h2>Phase N — <em>{title}</em> <span class="section-count">X of Y</span></h2>`
  - `<p class="section-lede">{phase.tagline}</p>`
  - `<div class="card-grid">` with only the phase's completed session cards, in session-number order.
- Phases with zero completed sessions are omitted entirely — no empty-state noise.
- Small inline `<style>` block reuses the existing `.section-count` chip pattern from `all-resources.html` so no theme drift.
- Cards themselves are unchanged (`.hub-card` → `sessions/{slug}/completed-session/index.html`, `chip-complete` badge, "Recap available" hint when the summary is present).

Rendered result after the 2026-07-05 sort: 11 completed sessions across 4 phases (Foundations 3/5, HA 5/5, Dynamic Routing 1/7, Fabric & Acceleration 2/4).
