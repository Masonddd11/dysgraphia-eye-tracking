# FYP Project Plan: Eye Tracking for Dysgraphia Screening (Copy-Task Pilot Study)

STATUS: draft v1 · 2026-09-21 · Adapt section lengths to the official form's word limits.

---

## 1. Motivation & background information

### 1.1 The problem and why it matters

Dysgraphia is a specific learning disorder characterised by persistent handwriting difficulty disproportionate to a person's age, intelligence, and instruction. Estimated prevalence among school-aged children ranges from about 5% to 20% depending on definition and instrument. The consequences reach past untidy script. Handwriting is a core transcription skill, and slow, effortful transcription takes cognitive resources away from composition, note-taking, and exams, with costs that show up across subjects.

The central problem is that handwriting difficulty gets identified late, through subjective judgement. Mainstream assessment is overwhelmingly product-based: a specialist inspects the finished page (with the BHK fast-copy test, handwriting checklists, or clinical impressions) and scores visible outcomes such as legibility, letter formation, and spacing. Referral often comes only after years of struggle, when intervention is fighting entrenched avoidance and lowered self-efficacy. Screening that could run earlier, faster, and more objectively is needed.

Product-based scoring also sees only the consequence of writing and misses the process: how a writer looks at the source text, holds information in working memory, and coordinates gaze and hand while copying. Emerging evidence suggests these process-level visuomotor behaviours carry discriminative signal that the finished product alone cannot show.

### 1.2 Previous approaches and what needs improvement

| Approach | Representative work | Limitation |
|---|---|---|
| Product-based psychometric tests | BHK, DASH, teacher checklists | Subjective, specialist-dependent, late; blind to process |
| Tablet kinematic analysis | Pen position and pressure features on digitising tablets; public datasets such as Drotár's DCD data | Captures only the hand; ignores the visual intake loop; lab-bound |
| Research-grade eye tracking | Eye-hand span and pause studies in copying, on lab trackers | Hardware is expensive and immobile, so it stays in the lab; few dysgraphia-specific protocols |
| Consumer webcam eye tracking | WebGazer and follow-ups | Validated for reading and UI tasks, not for copy tasks with head movement between screen and page |

Three areas need improvement, and they define the gap this project addresses:

1. Process-first measurement: no integrated, low-cost rig jointly records gaze and pen progress during standardised copy tasks for dysgraphia screening.
2. Accessibility: research trackers such as Tobii cost orders of magnitude more than a webcam. A validated consumer-grade path to the process metrics that survive lower-grade tracking would put screening within reach of schools and clinics.
3. Rigour: much prior computational-handwriting work is exploratory, small-N, and post-hoc. This project pre-registers its hypotheses, analysis, and decision rules before data collection, and quantifies instrument error (cross-device latency) as an error bar on every eye-hand metric, a step rarely reported in screening studies.

## 2. Problem statement, project objectives & scope

### 2.1 Problem statement

Can screen-based eye tracking during immediate and delayed copying tasks quantify differences in visuomotor coordination and visual encoding between dysgraphic and neurotypical writers? And can those measures work as objective, low-cost screening signals outside the laboratory?

### 2.2 Objectives

The project has six objectives:

1. O1 (instrument): Build a Lab Streaming Layer (LSL)-abstracted multi-sensor recording rig that jointly captures webcam-based gaze, head pose, word-level stimulus state, and Wacom EMR pen data (≥100 Hz), with an optional research-grade tracker (Tobii) module behind a capability-profile abstraction.
2. O2 (protocol software): Implement the three-condition assessment protocol from start to finish: stimulus presentation (word-wrapped paragraph with gaze-to-word resolution), 9-point gaze calibration, and event streaming, plus an offline pipeline computing process metrics (eye-hand span, switching between screen and paper, re-inspections, gaze-to-resume latency, encoding fixations).
3. O3 (measurement validity): Characterise the instruments: 9-point calibration accuracy for webcam gaze, and tracker-to-tablet latency via an LED-flash and pen-tap sync experiment, reported as error bars on all timing metrics.
4. O4 (pre-registered pilot study): Recruit ≈10 diagnosed dysgraphic and ≈10 age-band-matched control participants (guardian consent supported by clinical partners) and collect data under the frozen, uniform protocol.
5. O5 (analysis): Test pre-registered hypotheses with nonparametric group statistics and effect sizes; explore metric separability with a leave-one-out cross-validation (LOOCV) demonstration using classical ML (RF/SVM). This is a screening-signal demonstration, not a diagnostic classifier.
6. O6 (reproducible reporting): Deliver the full pipeline, de-identified dataset, auto-generated study report, and thesis.

### 2.3 Scope

The study runs three screen-based conditions: (1) immediate copy, the flagship condition, with text on screen and writing on paper-on-tablet; (2) delayed copy, where the stimulus is shown briefly then cleared and the participant writes from memory; and (3) a visual search baseline that controls for general visual-spatial ability. The build order is webcam-first, with the research-tracker upgrade layered behind the same pipeline. All data stays local, with PII stripped at ingest.

Assumptions to validate early:

- Ethics approval clears by about week 10 (submission in weeks 2-6; the clinical site's own requirements get confirmed first).
- The clinical partner can schedule ≈10+10 participants within a roughly five-week collection window.
- Tracker-to-tablet sync error is much smaller than the expected group differences; the O3 sync experiment quantifies this.
- Copy tasks elicit group differences, on the prior support of the BHK copying-task literature; the stimulus text is finalised with the partner.

Constraints: the project is solo over about 20 weeks on a consumer-hardware budget. A week-10 decision gate and instrument freeze guarantee uniform hardware across all participants. If the Tobii unit is integrated before the freeze, the full protocol runs; otherwise the webcam protocol substitutes delayed copy and search as primary conditions, with immediate copy contributing only coarse switching metrics.

Cases not considered, with reasons:

- Diagnostic classification claims: with N≈20 the study supports group statistics and screening signals, not a validated diagnostic instrument.
- Deep learning: no data budget for it; classical statistics plus RF/SVM is the defensible choice.
- Gaze-contingent masking, real-time processing, and web or cloud deployment: future work, out of scope.
- Desk-camera hand pose and ArUco paper homography: the Wacom already reports the pen tip, and a CV layer would add fragility without adding signal.
- Comorbidity subgroup analyses (dyslexia and DCD overlap): recorded as covariates where available, not powered for.

## 3. Major technical components

### 3.1 System overview

```
            ┌─────────────────────────  Acquisition (online)  ─────────────────────────┐
 Webcam ──►  fyp.webcam : FaceMesh landmarks → gaze estimate / head pose / switch events │
 Tobii* ──►  fyp.tobii  : research tracker gaze (capability-profile LSL adapter)*        │
 Wacom  ──►  fyp.stylus : ≥100 Hz x/y/z/pen-tip stream                                    │
 Stimulus ►  fyp.webcam.stimulus : paragraph layout + gaze→word index                     │
            └──────────────  all sensors ⇒ LSL outlets ⇒ redundant XDF recording  ───────┘
                                              │
            ┌──────────────────────  Offline analysis pipeline  ────────────────────────┐
 XDF files ► event detection (fixations, switches, pen pauses) ► process metrics        │
          ► copy-quality scoring (scans, BHK-style) ► statistics + LOOCV ► report/thesis │
            └───────────────────────────────────────────────────────────────────────────┘
            * optional module activated at the week-10 gate
```

### 3.2 Components

| # | Component | Function | Tech | Status |
|---|---|---|---|---|
| 1 | Gaze estimation (`gaze.py`) | Maps FaceMesh iris landmarks to screen coordinates via 9-point calibration (affine/polynomial fit); pure-numpy, unit-tested | numpy | Done in V1 |
| 2 | Head-pose extraction (`landmarks.py`) | solvePnP over facial landmarks gives yaw/pitch/roll; the `pitch_down_deg` positive-when-down convention feeds the switch detector | OpenCV, MediaPipe | Done in V1 |
| 3 | Switch detector (`switching.py`) | Hysteresis and dwell-time state machine on head pitch produces monitor-to-paper transition events; pure, unit-tested | numpy | Done in V1 |
| 4 | Stimulus engine (`stimulus.py`, `cli.py`) | Word-wrapped paragraph layout, word-level bounding boxes, gaze-to-word resolution, fullscreen overlay with HUD and gaze dot | OpenCV | Done in V1 |
| 5 | LSL streaming layer (`lsl.py`) | Four outlets (`FYP_WebcamGaze`, `FYP_WebcamHeadPose`, `FYP_WordIndex`, `FYP_SwitchEvents`) time-aligned on one clock, with redundant XDF recording | pylsl | Done in V1 |
| 6 | Wacom EMR stylus adapter | Streams pen position, pressure, and contact at ≥100 Hz as another LSL stream; this is the pen-progress axis for eye-hand span | Python + device SDK | V3 (wks 5-6) |
| 7 | Sync rig (LED + pen-tap) | Camera-detected LED flash and pen-tap events measure end-to-end tracker-to-tablet latency; the result becomes the error bar on every eye-hand span estimate | hardware + script | V3 (wks 5-6) |
| 8 | Tobii adapter | Research-grade gaze behind the same LSL capability profile, so the pipeline is hardware-agnostic; sync validation re-run on it | tobii SDK | V4 (wks 6-9) |
| 9 | Offline analysis pipeline | Fixation and saccade detection, switch and pause segmentation; metrics: eye-hand span, switch rate, re-inspections, gaze-to-resume latency, encoding fixation counts and dwell; BHK-style copy-quality scoring from scans; nonparametric tests, effect sizes, LOOCV (RF/SVM) | statsmodels, scikit-learn | V2+ (builds from wk 3) |
| 10 | Study management | Pre-registration document, PII stripping at ingest, local-only storage, version-stamped instruments | docs + scripts | ongoing |

Design rule: all signal-processing math (components 1, 3, 4) stays in pure, numpy-only, unit-tested modules; hardware paths are exercised by live smoke runs. This separation is what makes the pipeline portable across webcam and Tobii hardware at the week-10 gate.

## 4. Expected results & deliverables

### 4.1 How the system will be tested

- Unit tests (continuous, TDD): the pure modules (calibration math, switch detector, head pose, stimulus layout and word lookup) are numpy-only and covered by the offline suite, with 17 tests currently passing (`uv run pytest -q`); every new pure-math feature lands test-first.
- Hardware smoke runs: a headless stats-only run and live-preview runs with HUD and gaze dot for each sensor module, before and after every integration step.
- Instrument characterisation (O3): 9-point calibration accuracy per session, plus the LED-flash and pen-tap latency experiment that quantifies sync error as the error bar on all eye-hand timing metrics.
- Pipeline validation on public data: copy-quality scoring is validated on public handwriting datasets while ethics approval is pending (weeks 3-6).
- Dry-run sessions: full-protocol rehearsals with pilot participants at the week-10 gate, before the instrument freeze and data collection.

### 4.2 Expected results

- Instrumental: a rig with measured cross-device latency; webcam head-pose switching metrics that hold up at consumer-grade frame rates; and region-level (word and line) gaze resolution sufficient for switching and encoding metrics.
- Scientific (pre-registered hypotheses): relative to controls, the dysgraphic group is expected to show (a) larger and more variable eye-hand spans during immediate copy, (b) more frequent switching and re-inspections between screen and paper, (c) altered encoding strategy in delayed copy (fewer and shorter fixations on orthographically difficult elements), associated with (d) lower copy-quality scores. All results are reported with nonparametric tests and effect sizes.
- Screening signal: a LOOCV demonstration of metric separability, presented as evidence of screening potential, not diagnostic accuracy.
- Contingency: if the Tobii unit is not integrated by the week-10 freeze, the webcam protocol runs unchanged (delayed copy and visual search as primary conditions, immediate copy reduced to coarse switching metrics), so the study completes with either instrument.

### 4.3 Deliverables

1. The `fyp` Python package: sensor and analysis pipeline (webcam gaze, head pose, switch detection, stimulus, LSL streaming, Wacom and Tobii adapters, offline metrics and statistics), open-source-ready with tests and docs.
2. The pre-registered study protocol and ethics documentation.
3. The sync and rig characterisation report (calibration accuracy and tracker-to-tablet latency).
4. The de-identified pilot dataset (about 20 participants, XDF plus scans), with PII stripped at ingest.
5. Reproducible analysis: scripts and an auto-generated study report (markdown/PDF).
6. The final thesis (APA 7) and presentation materials.

## 5. Project schedule

The plan assumes 20 weeks, with week 1 on 7 September 2026; adjust to the department's thesis deadline. As of 21 September (week 3), V1 is complete with 17 tests passing and V2 is underway.

### 5.1 Milestones

| Milestone | Week | Criterion |
|---|---|---|
| M1: Webcam rig V1 | 2 | Done: gaze, head pose, and switch events streaming over LSL |
| M2: Webcam protocol end-to-end | 4 | Delayed-copy and search conditions run on webcam; encoding metrics computed offline |
| M3: Wacom + sync rig | 6 | ≥100 Hz stylus stream; LED/tap latency characterised |
| M4: Tobii + immediate copy | 9 | Research tracker behind capability profile; immediate-copy metrics; sync re-validated |
| M5: Decision gate and instrument freeze | 10 | Uniform hardware chosen, version-stamped, dry-run sessions passed; go/no-go |
| M6: Data collection complete | 16 | ≈10+10 participants recorded with redundant raw XDF |
| M7: Pre-registered analysis and report | 18 | Group statistics, effect sizes, LOOCV; auto-generated report |
| M8: Thesis submission | 20+ | Full thesis (APA 7) and defence materials |

### 5.2 Gantt chart

```
Activity                       1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
-----------------------------------------------------------------------------------------
V1 Webcam gaze rig (done)     ██ ██                                                      
V2 Webcam protocol end-to-end       ██ ██                                                
    + pipeline validation*          ░░ ░░ ░░ ░░                                          
Ethics submission & approval     ▒▒ ▒▒ ▒▒ ▒▒ ▒▒                                          
V3 Wacom stylus + sync rig                ██ ██                                          
V4 Tobii + immediate copy                    ██ ██ ██ ██                                 
Wk-10 gate: freeze + dry-runs                            ◆◆                              
V5 Data collection (10+10)                                  ██ ██ ██ ██ ██ ██            
V6 Analysis + report                                                          ██ ██ ██ ██
Thesis writing                                           ░░ ░░ ░░ ░░ ░░ ░░ ░░ ██ ██ ██ ██
```

Legend: `██` full effort, `░░` background or partial, `▒▒` external dependency, `◆` gate. The starred row validates copy-quality scoring on public handwriting data while ethics is pending.

Ethics is the critical external dependency, so the submission runs in parallel from week 2 and is chased before the hardware work completes. The week-10 freeze removes instrument variance across participants. Data collection (weeks 11-16, two to three sessions per week) leaves four weeks for analysis and writing, with thesis drafting running in the background from week 10.

## 6. AI Usage Plan & Considerations

### 6.1 How AI tools will be used

AI appears in three distinct roles in this project, kept separate in the plan and in the disclosure:

1. Development assistant (generative AI in the workflow), accelerating implementation of the rig and pipeline as a solo developer.
2. ML as system components (AI inside the instrument): MediaPipe FaceMesh for landmark and iris detection, and classical ML (RF/SVM) for the LOOCV demonstration. These are research components under evaluation, not workflow tools; their accuracy and limitations are part of what the project measures.
3. Study-support tasks: literature discovery and writing polish, under the verification rules below.

### 6.2 Proposed tools and intended purposes

| Tool | Intended purpose | Allowed use | Not allowed |
|---|---|---|---|
| AI coding agents (e.g., OpenCode with LLM models) | Module scaffolding, refactoring, test generation, debugging | Code reviewed line by line, understood, and unit tested by the student before inclusion | Unreviewed generated code; generated test assertions accepted without checking they can fail |
| MediaPipe FaceMesh | Iris and face landmarks for gaze and head pose (pinned `<0.10.15` for API stability) | Instrument component; accuracy characterised (O3) | Silent upgrades mid-study (frozen at wk 10) |
| scikit-learn / statsmodels | LOOCV demonstration (RF/SVM), statistical tests | Reproducible scripted analysis | Any result not reproducible from committed code |
| AI literature tools (e.g., search assistants, library AI) | Locating primary sources, surveying related work | Finding leads; every citation checked against the primary paper before use | Citing AI-summarised content directly; AI-generated references |
| AI writing assistants | Grammar, clarity, formatting of thesis drafts | Sentence-level polish of student-authored text | Generating scientific claims, analysis text, or results interpretation |

### 6.3 Expected benefits and potential limitations

Benefits: higher velocity for a solo project (scaffolding, edge-case handling in tests); broader literature coverage early; consistent code style; and ML components (FaceMesh) that provide state-of-the-art landmark detection without any training data.

Limitations and risks: hallucinated references; plausible but subtly wrong code, especially in numeric and signal-processing edge cases; over-reliance that could weaken the student's own command of methods defended at the viva; API instability of model-mediated dependencies (mitigated by version pinning); and privacy exposure if participant data ever reached a cloud service.

### 6.4 Review, validation, and acknowledgement measures

- Code: nothing merges unreviewed. Pure-math modules are TDD-covered (`uv run pytest -q`, 17 tests at present) and must stay numpy-only; hardware paths are verified by live smoke runs. AI-assisted code is understood well enough to be defended and debugged line by line.
- Statistics: every reported number comes from committed, reproducible scripts run on the de-identified dataset, never from an AI response.
- Literature: citations verified against primary sources; APA 7 entries only for papers actually read.
- Privacy: participant data, recordings, and PII never enter any cloud AI service; PII is stripped at ingest and all processing is local.
- Academic integrity: an AI usage log records the tool, purpose, and extent of assistance; the thesis carries an AI-use disclosure statement in accordance with the University's generative-AI policy; the supervisor reviews the usage log at milestones; all scientific claims, study design, and interpretations are authored by the student.
