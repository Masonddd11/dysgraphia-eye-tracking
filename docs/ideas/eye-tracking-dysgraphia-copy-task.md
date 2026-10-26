# Eye Tracking for Dysgraphia — Copy-Task Protocol (Science-First FYP)

## Problem Statement

How might we use screen-based eye tracking during immediate and delayed copying tasks to quantify the visuomotor coordination and visual encoding differences between dysgraphic and neurotypical writers?

## Recommended Direction

A pre-registered pilot study (~10 diagnosed + ~10 controls, open to all ages with age-band matching or restriction, guardian consent supported by clinical professionals) running three screen-based conditions, with eye tracking as the primary instrument and a Wacom EMR tablet (paper on top) as the secondary pen-progress sensor:

1. **Immediate copy** (flagship): text on screen, write on paper — eye-hand span, monitor↔paper switching, re-inspections, gaze-to-resume latency. Requires research tracker + Wacom.
2. **Delayed copy**: stimulus shown briefly then cleared, write from memory — encoding gaze strategy (fixation count, dwell on difficult elements) vs. copy quality. Runs on webcam-grade tracking; output scored offline from scans.
3. **Visual search baseline**: letter/shape search task — controls for general visual-spatial ability; runs on any tracker.

Hardware is LSL-abstracted with capability profiles. Build order is webcam-first (all in-hand hardware); the stylus and research-tracker modules layer on without touching the pipeline. A week-10 decision gate + freeze guarantees uniform hardware across all participants: Tobii in before freeze → full protocol; not in → webcam protocol (delayed copy + search as primary conditions, immediate copy keeps only coarse switching metrics).

Sync rigor survives as instrument calibration: LED-flash + pen-tap events measure end-to-end tracker↔tablet latency, which becomes the error bar on every eye-hand span estimate.

Solo, ~4.5–5 months, Python (uv), OpenCV, LSL, scikit-learn/statsmodels. Report generated as markdown/PDF. All data local, PII-stripped at ingest.

## Key Assumptions to Validate

- [ ] Ethics approval clears by ~week 10 — submission must reach the committee in weeks 2–6 (ask supervisor NOW: form, committee, turnaround; check whether the clinical site needs its own approval)
- [ ] Clinical partner schedules ~10+10 within a ~5-week window — confirm with named numbers
- [ ] Tracker↔tablet sync error ≪ group differences — quantified by the LED/tap experiment in V3
- [ ] Copy tasks elicit group differences — BHK copying-task literature is prior support; finalize stimulus text with the partner

## MVP Scope

- V1 (wks 1–2): LSL skeleton + webcam adapters — screen-gaze estimates + head-pose monitor↔paper switching; stream-quality baseline
- V2 (wks 3–4): delayed-copy + search conditions end-to-end, webcam-only; encoding metrics; offline copy-quality scoring; pipeline validated on public handwriting data while ethics runs
- V3 (wks 5–6): Wacom stylus adapter (≥100Hz x/y/z/t); LED + pen-tap sync rig; tracker↔tablet latency characterization
- V4 (wks 6–9): Tobii integration + immediate-copy condition (eye-hand span, switching, re-inspections); re-run sync validation with the real tracker
- WK 10: decision gate + instrument freeze (Tobii or webcam protocol); dry-run sessions; version stamp; go/no-go
- V5 (wks 11–16): data collection, 2–3 sessions/week, redundant raw LSL recording
- V6 (wks 17–20): pre-registered analysis (nonparametric group tests, effect sizes, LOOCV demonstration), auto-generated report, thesis

## Not Doing (and Why)

- Desk camera, MediaPipe hand pose, ArUco paper homography — Wacom already reports the pen tip; the CV layer added fragility, not signal.
- Diagnostic-classifier claims — N≈20 supports group statistics and screening signals, not validated diagnosis.
- Deep learning — no data budget; RF/SVM + statistics is defensible.
- Gaze-contingent masking — named as future work.
- Web frontend, cloud, real-time processing — after the study, if ever.

## Open Questions

- Clinical site's own approval requirements (ask the professionals)
- Age distribution of the partner's pool → match or restrict to one band
- Exact thesis deadline (schedule assumes ~20 weeks)
- Handedness mix — record as covariate; keep setup ambidextrous (free paper placement)
