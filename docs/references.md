# Reference Library — FYP Report

> **Project:** Oculomotor biomarkers for objective dysgraphia screening: eye-tracking copy-task rig
> **Compiled:** 2026-09-08 by five parallel research agents; every entry was verified against publisher pages, PubMed/PMC, arXiv, or DOI records. No citation is reconstructed from memory.
> **Usage:** Sections map to likely report chapters (background → literature review → methods → discussion). Each entry carries a one-line "Cite for:" note. Re-format to your department's required style (APA 7 / IEEE / Harvard) at write-up time.

---

## 1. Dysgraphia — Definition, Prevalence & Diagnosis
*Background chapter: what dysgraphia is, how it is classified, why diagnosis is hard.*

1. American Psychiatric Association. (2013). *Diagnostic and statistical manual of mental disorders* (5th ed.). American Psychiatric Publishing. Official APA fact sheet: https://www.psychiatry.org/File%20Library/Psychiatrists/Practice/DSM/APA_DSM-5-Specific-Learning-Disorder.pdf
   **Cite for:** dysgraphia is subsumed under Specific Learning Disorder with impairment in written expression (specifier 315.2 / F81.81); it is not a standalone DSM-5 diagnosis.

2. World Health Organization. (2022). *ICD-11: International classification of diseases* (11th revision), 6A03.1 Developmental learning disorder with impairment in written expression. https://icd.who.int/
   **Cite for:** international classification; "dysgraphia" is listed as an inclusion term under 6A03.1.

3. Chung, P. J., Patel, D. R., & Nizami, I. (2020). Disorder of written expression and dysgraphia: Definition, diagnosis, and management. *Translational Pediatrics, 9*(Suppl 1), S46–S54. https://doi.org/10.21037/tp.2019.11.01
   **Cite for:** peer-reviewed review covering subtype theories, comorbidity, 10–30% prevalence range, and the absence of consensus diagnostic criteria.

4. Deuel, R. K. (1995). Developmental dysgraphia and motor skills disorders. *Journal of Child Neurology, 10*(Suppl.), S6–S8.
   **Cite for:** the seminal dyslexic / spatial / motor subtype taxonomy (details verified via the reference list of Asselborn et al., 2018).

5. Overvelde, A., & Hulstijn, W. (2011). Handwriting development in grade 2 and grade 3 primary school children with normal, at risk, or dysgraphic characteristics. *Research in Developmental Disabilities, 32*(5), 540–548. https://doi.org/10.1016/j.ridd.2010.12.027
   **Cite for:** the 5–33% prevalence range and evidence that early "dysgraphic" classification is often transient — motivating objective, repeated screening.

6. Karlsdóttir, R., & Stefánsson, T. (2002). Problems in developing functional handwriting. *Perceptual and Motor Skills, 94*(2), 623–662. https://doi.org/10.2466/pms.2002.94.2.623
   **Cite for:** 5-year longitudinal evidence of diagnostic instability (27% dysfunctional at Grade 1 vs 13% at Grade 5).

---

## 2. Handwriting Assessment Instruments
*Background/methods: the clinical gold standards your rig is positioned against.*

7. Hamstra-Bletz, L., De Bie, J., & den Brinker, B. P. O. L. (1987). *Beknopte Beoordelingsmethode voor Kinderhandschriften [Concise Evaluation Scale for Children's Handwriting, BHK]*. Swets & Zeitlinger.
   **Cite for:** the original BHK manual — 13 legibility items + copy speed; the clinical ground-truth instrument for dysgraphic vs. control grouping. *(Dutch book, no DOI; some bibliographies print den Brinker's initials as "B.P.L.M." — source lists conflict.)*

8. Hamstra-Bletz, L., & Blöte, A. W. (1990). Development of handwriting in primary school: A longitudinal study. *Perceptual and Motor Skills, 70*(3), 759–770. https://doi.org/10.2466/pms.1990.70.3.759
   **Cite for:** peer-reviewed longitudinal validation of the BHK scale (Grades 2–6).

9. Barnett, A., Henderson, S. E., Scheib, B., & Schulz, J. (2007). *The Detailed Assessment of Speed of Handwriting (DASH): Manual*. Pearson Education. https://uhra.herts.ac.uk/id/eprint/18380/
   **Cite for:** standardised UK handwriting-speed measure; benchmark for speed-based identification. *(Manual; DASH-2 now supersedes it.)*

10. Diekema, S. M., Deitz, J., & Amundson, S. J. C. (1998). Test–retest reliability of the Evaluation Tool of Children's Handwriting–Manuscript. *American Journal of Occupational Therapy, 52*(4), 248–255. https://doi.org/10.5014/ajot.52.4.248
    **Cite for:** moderate test–retest coefficients of the ETCH (.63–.77) — concrete evidence that static product-rating scales have limited reliability, motivating objective process measurement.

11. Beery, K. E., Buktenica, N. A., & Beery, N. A. (2010). *Beery-Buktenica Developmental Test of Visual-Motor Integration (BEERY VMI)* (6th ed.). Pearson. https://www.pearsonassessments.com/store/usassessments/en/p/beery-buktenica-developmental-test-of-visual-motor-integration-sixth-edition/100000663
    **Cite for:** standard visual–motor integration covariate for group matching (note: Overvelde & Hulstijn 2011 found VMI poor as a *screening* tool — cite together).

12. Rosenblum, S., Weiss, P. L., & Parush, S. (2003). Product and process evaluation of handwriting difficulties: A review. *Educational Psychology Review, 15*(1), 41–81. https://doi.org/10.1023/A:1021371425220
    **Cite for:** the canonical product-vs-process review — static scales miss the writing *process*; directly justifies capturing real-time signals (kinematics, gaze) during copying.

---

## 3. Computational & Kinematic Dysgraphia Screening
*Literature review: prior art for objective/automated dysgraphia analysis.*

13. Mekyska, J., Faúndez-Zanuy, M., Mzourek, Z., Galáž, Z., Smékal, Z., & Rosenblum, S. (2017). Identification and rating of developmental dysgraphia by handwriting analysis. *IEEE Transactions on Human-Machine Systems, 47*(2), 235–248. https://doi.org/10.1109/THMS.2016.2586605
    **Cite for:** digitizing-tablet kinematic/pressure/tilt parameterisation + random forest (96% sens/spec); template for your feature-extraction approach.

14. Asselborn, T., Gargot, T., Kidziński, Ł., Johal, W., Cohen, D., Jolly, C., … Dillenbourg, P. (2018). Automated human-level diagnosis of dysgraphia using a consumer tablet. *npj Digital Medicine, 1*, Article 42. https://doi.org/10.1038/s41746-018-0049-x
    **Cite for:** digitised BHK copy task in 298 children, 96.6% sensitivity / 99.2% specificity — the closest methodological precedent for a copy-task screening rig.

15. Drotár, P., & Dobeš, M. (2020). Dysgraphia detection through machine learning. *Scientific Reports, 10*, Article 21541. https://doi.org/10.1038/s41598-020-78611-9
    **Cite for:** Wacom-tablet kinematic features + ML (~80% accuracy); its open dataset and copy tasks (letters, pseudoword, sentence) are the standard digitizing-tablet paradigm.

---

## 4. Eye–Hand Coordination During Copying — Core Science
*Literature review: the scientific basis for eye-hand span, gaze switching, re-inspections, delayed-copy encoding.*

16. Inhoff, A. W., & Wang, J. (1992). Encoding of text, manual movement planning, and eye-hand coordination during copytyping. *Journal of Experimental Psychology: Human Perception and Performance, 18*(2), 437–448. https://doi.org/10.1037/0096-1523.18.2.437
    **Cite for:** the eye-hand span (~3 character spaces; 468–780 ms gaze-lead) — direct precedent for your immediate-copy gaze metrics.

17. Kandel, S., & Valdois, S. (2006). Syllables as functional units in a copying task. *Language and Cognitive Processes, 21*(4), 432–452. https://doi.org/10.1080/01690960400018378
    **Cite for:** "gaze lifts" during handwriting copying as the measure of visual-unit size — exactly the child-lifts-gaze-to-re-extract behaviour your switch detector quantifies.

18. Kandel, S., & Perret, C. (2015). How does the interaction between spelling and motor processes build up during writing acquisition? *Cognition, 136*, 325–336. https://doi.org/10.1016/j.cognition.2014.11.014
    **Cite for:** central (orthographic) processing cascades into motor production during copying — justifies latency/fluency metrics as processing-load indicators.

19. Maldarelli, J. E., Kahrs, B. A., Hunt, S. C., & Lockman, J. J. (2015). Development of early handwriting: Visual-motor control during letter copying. *Developmental Psychology, 51*(7), 879–888. https://doi.org/10.1037/a0039424
    **Cite for:** head-mounted eye tracking during letter copying; children re-fixate the model mid-writing while adults rarely do — age-sensitive re-inspection behaviour.

20. Lambert, R., Boutet, J., Labyt, É., & Jolly, C. (2023). Analysis of eye movements in children with developmental coordination disorder during a handwriting copy task. In A. Parziale et al. (Eds.), *IGS 2023, Lecture Notes in Computer Science* (Vol. 14285). Springer. https://doi.org/10.1007/978-3-031-45461-5_3
    **Cite for:** recent evidence that children with DCD/dysgraphia show distinct gaze allocation (more, shorter fixations in the writing area) during copying — supports gaze metrics as screening markers.

21. Alamargot, D., Chesnet, D., Dansac, C., & Ros, C. (2006). Eye and Pen: A new device for studying reading during writing. *Behavior Research Methods, 38*(2), 287–299. https://doi.org/10.3758/BF03192780
    **Cite for:** synchronous eye+pen recording as the established method for gaze alternation between source and paper — methodological basis for your monitor↔paper switching design.

22. Lau, D. K.-Y. (2020). Orthographic and phonological processing in Chinese character copying – A preliminary report. *Frontiers in Psychology, 11*, 2122. https://doi.org/10.3389/fpsyg.2020.02122
    **Cite for:** even "minimal" immediate copying engages orthographic/phonological processing in Chinese — relevant to character-copying stimuli for a Hong Kong sample.

23. Tchalenko, J., & Miall, R. C. (2009). Eye–hand strategies in copying complex lines. *Cortex, 45*(3), 368–376. https://doi.org/10.1016/j.cortex.2007.12.012
    **Cite for:** the Memory-copying condition — encoding fixations differ from execution, and accuracy depends on encoding strategy; direct support for your delayed-copy rationale.

24. Ballard, D. H., Hayhoe, M. M., & Pelz, J. B. (1995). Memory representations in natural tasks. *Journal of Cognitive Neuroscience, 7*(1), 66–80. https://doi.org/10.1162/jocn.1995.7.1.66
    **Cite for:** the "just-in-time" theory — people re-fixate sources rather than rely on fragile working memory; the theoretical frame for interpreting re-inspection metrics.

25. Bosse, M.-L., Kandel, S., Prado, C., & Valdois, S. (2014). Does visual attention span relate to eye movements during reading and copying? *International Journal of Behavioral Development, 38*(1), 81–85. https://doi.org/10.1177/0165025413509046
    **Cite for:** children with larger visual-attention span copy more letters per gaze lift — supports fixation/dwell during viewing as a visual-encoding-strategy index.

---

## 5. Working Memory, Transcription & Writing Models
*Rationale for the delayed-copy condition and copy-quality scoring.*

26. Hayes, J. R., & Flower, L. S. (1980). Identifying the organization of writing processes. In L. W. Gregg & E. R. Steinberg (Eds.), *Cognitive processes in writing* (pp. 3–30). Lawrence Erlbaum. (Reprint DOI: https://doi.org/10.4324/9781315630274-3)
    **Cite for:** the seminal planning–translating–reviewing writing model; frames transcription as a distinct measurable component.

27. McCutchen, D. (1996). A capacity theory of writing: Working memory in composition. *Educational Psychology Review, 8*(3), 299–325. https://doi.org/10.1007/BF01464076
    **Cite for:** transcription and text maintenance compete for limited working memory — why delayed copy taxes encoding capacity.

28. Berninger, V. W., Yates, C., Cartwright, A. C., Rutberg, J., Remy, E., & Abbott, R. (1992). Lower-level developmental skills in beginning writing. *Reading and Writing, 4*(3), 257–280. https://doi.org/10.1007/BF01027151
    **Cite for:** transcription (handwriting/spelling) as a separable sub-component that constrains composing — grounds the copy task as a transcription-level probe.

---

## 6. Visual Attention & Visuomotor Theory of Learning Disorders
*Positioning your hypotheses against the dominant theories.*

29. Bosse, M.-L., Tainturier, M.-J., & Valdois, S. (2007). Developmental dyslexia: The visual attention span deficit hypothesis. *Cognition, 104*(2), 198–230. https://doi.org/10.1016/j.cognition.2006.05.009
    **Cite for:** the seminal visual attention span paper — parallel visual processing predicts reading independently of phonology.

30. Vellutino, F. R., Fletcher, J. M., Snowling, M. J., & Scanlon, D. M. (2004). Specific reading disability (dyslexia): What have we learned in the past four decades? *Journal of Child Psychology and Psychiatry, 45*(1), 2–40. https://doi.org/10.1046/j.0021-9630.2003.00305.x
    **Cite for:** authoritative caution about visual-deficit claims vs the phonological account — keeps your visuomotor claims well-scoped.

---

## 7. Eye Tracking in Dyslexia & Neurodevelopmental Screening — Adjacent Evidence
*Literature review: the closest prior art for oculomotor screening (direct dysgraphia+ET work is sparse).*

31. Jainta, S., & Kapoula, Z. (2011). Dyslexic children are confronted with unstable binocular fixation while reading. *PLoS ONE, 6*(4), e18694. https://doi.org/10.1371/journal.pone.0018694
    **Cite for:** oculomotor instability (fixation-disparity variability) in dyslexic readers independent of phonological deficits.

32. Bucci, M. P., Brémond-Gignac, D., & Kapoula, Z. (2008). Poor binocular coordination of saccades in dyslexic children. *Graefe's Archive for Clinical and Experimental Ophthalmology, 246*(3), 417–428. https://doi.org/10.1007/s00417-007-0723-1
    **Cite for:** disconjugate saccades appear even in non-reading tasks — justifies oculomotor biomarkers that don't depend on reading skill.

33. De Luca, M., Borrelli, M., Judica, A., Spinelli, D., & Zoccolotti, P. (2002). Reading words and pseudowords: An eye movement study of developmental dyslexia. *Brain and Language, 80*(3), 617–626. https://doi.org/10.1006/brln.2001.2637
    **Cite for:** atypical eye movements reflect processing strategy, not just motor deficit — the interpretive logic for biomarker screening.

34. Rello, L., & Ballesteros, M. (2015). Detecting readers with dyslexia using machine learning with eye tracking measures. *Proceedings of the 12th Web for All Conference (W4A '15)*, Article 16. ACM. https://doi.org/10.1145/2745555.2746644
    **Cite for:** ML classification of dyslexia from eye tracking (80.18%) — precedent for your RF/SVM approach.

35. Nilsson Benfatto, M., Öqvist Seimyr, G., Ygge, J., Pansell, T., Rydberg, A., & Jacobson, C. (2016). Screening for dyslexia using eye tracking during reading. *PLoS ONE, 11*(12), e0165508. https://doi.org/10.1371/journal.pone.0165508
    **Cite for:** <1 minute of eye tracking + predictive modelling identified at-risk children (95.6%) — the core screening-feasibility citation.

36. Gran Ekstrand, A. C., Nilsson Benfatto, M., & Öqvist Seimyr, G. (2021). Screening for reading difficulties: Comparing eye tracking outcomes to neuropsychological assessments. *Frontiers in Education, 6*, 643232. https://doi.org/10.3389/feduc.2021.643232
    **Cite for:** eye-tracking screening flags correspond to independent neuropsychological assessment — validity evidence.

37. Park, S., Song, J., Eom, T.-H., & Kim, Y.-H. (2024). Reliability of a tablet computer-based dyslexia screening application using an eye-tracking system. *Annals of Child Neurology, 32*(2), 99–104. https://doi.org/10.26815/acn.2023.00360
    **Cite for:** consumer-hardware feasibility (RGB front camera on a tablet; ICC 0.72–0.83 across 200 schoolchildren) — strongest match to your webcam-first build.

38. Sumner, E., Hutton, S. B., Kuhn, G., & Hill, E. L. (2018). Oculomotor atypicalities in Developmental Coordination Disorder. *Developmental Science, 21*(1), e12501. https://doi.org/10.1111/desc.12501
    **Cite for:** DCD adjacency (dysgraphia overlaps DCD) — fixation instability and antisaccade errors distinguish children with motor impairment.

39. Yoo, J. H., Kang, C., Lim, J. S., Wang, B., Choi, C.-H., Hwang, H., et al. (2024). Development of an innovative approach using portable eye tracking to assist ADHD screening: A machine learning study. *Frontiers in Psychiatry, 15*, 1337595. https://doi.org/10.3389/fpsyt.2024.1337595
    **Cite for:** generalisation of portable eye tracking + ML screening to a second neurodevelopmental disorder.

40. Diotaiuti, P., Di Siena, F., Vitiello, S., Di Tore, P. A., & Mancone, S. (2026). Eye-tracking in school-age specific learning disorders: A practice-oriented narrative review of assessment and gaze-contingent interventions. *Frontiers in Education, 10*, 1759299. https://doi.org/10.3389/feduc.2025.1759299
    **Cite for:** the closest existing synthesis — reviews ET evidence across SLD *including dysgraphia* (reduced anticipatory gaze, fragmented scanpaths during copying); anchors your gap statement.

---

## 8. Instruments & Software — Tech Stack
*Methods chapter: cite your instruments.*

41. Lugaresi, C., Tang, J., Nash, H., McClanahan, C., Uboweja, E., Hays, M., Zhang, F., Chang, C.-L., Yong, M. G., Lee, J., Chang, W.-T., Hua, W., Georg, M., & Grundmann, M. (2019). MediaPipe: A framework for building perception pipelines. arXiv:1906.08172. https://arxiv.org/abs/1906.08172
    **Cite for:** the overall perception framework (CVPR 2019 workshop).

42. Kartynnik, Y., Ablavatski, A., Grishchenko, I., & Grundmann, M. (2019). Real-time facial surface geometry from monocular video on mobile GPUs. arXiv:1907.06724. https://arxiv.org/abs/1907.06724
    **Cite for:** the 468-landmark Face Mesh model used for face/eye-region localisation.

43. Ablavatski, A., Vakunov, A., Grishchenko, I., Raveendran, K., & Zhdanovich, M. (2020). Real-time pupil tracking from monocular video for digital puppetry. arXiv:2006.11341. https://arxiv.org/abs/2006.11341
    **Cite for:** the iris/pupil landmark model (MediaPipe Iris) extending Face Mesh to 478 vertices. **⚠ There is no paper titled "MediaPipe Iris: real-time iris tracking" — cite this arXiv paper; the "MediaPipe Iris" name only appears in the [Google Research blog](https://research.google/blog/mediapipe-iris-real-time-iris-tracking-depth-estimation/) and docs.**

44. Sewell, W., & Komogortsev, O. (2010). Real-time eye gaze tracking with an unmodified commodity webcam employing a neural network. *CHI '10 Extended Abstracts on Human Factors in Computing Systems* (pp. 3739–3744). ACM. https://doi.org/10.1145/1753846.1754048
    **Cite for:** foundational precedent for webcam-based gaze estimation.

45. Kaduk, T., Goeke, C., Finger, H., & König, P. (2024). Webcam eye tracking close to laboratory standards: Comparing a new webcam-based system and the EyeLink 1000. *Behavior Research Methods, 56*(5), 5002–5022. https://doi.org/10.3758/s13428-023-02237-8
    **Cite for:** modern validation of webcam gaze accuracy (~1.4°) vs research-grade hardware — benchmarks your consumer-camera approach. *(Published online 2023; volume year 2024.)*

46. Wisiecka, K., Krejtz, K., Krejtz, I., Sromek, D., Cellary, A., Lewandowska, B., & Duchowski, A. (2022). Comparison of webcam and remote eye tracking. *2022 Symposium on Eye Tracking Research and Applications (ETRA)* (pp. 1–7). ACM. https://doi.org/10.1145/3517031.3529615
    **Cite for:** direct webcam vs infrared-tracker comparison — justifies the optional Tobii upgrade path.

47. Kothe, C., Shirazi, S. Y., Stenner, T., Medine, D., Boulay, C., Grivich, M. I., Artoni, F., Mullen, T., Delorme, A., & Makeig, S. (2025). The Lab Streaming Layer for synchronized multimodal recording. *Imaging Neuroscience, 3*, IMAG.a.136. https://doi.org/10.1162/IMAG.a.136
    **Cite for:** canonical LSL citation — the repo's "Cite LSL" guidance now instructs citing this paper (supersedes the old GitHub-only citation). Docs: https://labstreaminglayer.readthedocs.io

48. Tobii AB. (2023). *Tobii Pro Spectrum product description* (technical specification). https://www.tobii.com/products/eye-trackers/screen-based/tobii-pro-spectrum
    **Cite for:** official specs for the optional research-grade tracker (up to 1200 Hz, median accuracy 0.3°); substitute your exact model's product-description PDF.

49. Tobii AB. (2026). *Data quality reports for Tobii eye trackers* (test methodology and metrics). https://www.tobii.com/resource-center/data-quality
    **Cite for:** vendor-published accuracy/precision test methodology for citing tracker performance numbers.

50. Wacom Co., Ltd. (n.d.). *Our key technologies — EMR (Electro-Magnetic Resonance)*. https://www.wacom.com/en-us/about-wacom/technologies
    **Cite for:** official description of the batteryless electromagnetic-resonance digitizer used to sense pen position beneath paper. *(Companion article: https://support.wacom.com/hc/en-us/articles/1500006270401 — no peer-reviewed "Wacom EMR" paper exists; vendor documentation is the accepted citation form for instruments.)*

51. Bradski, G. (2000). The OpenCV Library. *Dr. Dobb's Journal of Software Tools, 25*(11), 120–125.
    **Cite for:** canonical OpenCV citation (per OpenCV's official CiteOpenCV wiki); pair with https://docs.opencv.org for the version used.

---

## 9. Methodology & Statistics
*Methods chapter: preregistration, pilot design, tests, effect sizes, small-sample ML, software.*

52. Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The preregistration revolution. *Proceedings of the National Academy of Sciences, 115*(11), 2600–2606. https://doi.org/10.1073/pnas.1708274114
    **Cite for:** pre-specifying the analysis plan makes confirmatory tests diagnostic. *(AsPredicted has no citable paper — cite https://aspredicted.org as a URL in text.)*

53. Cohen, J. (1988). *Statistical power analysis for the behavioral sciences* (2nd ed.). Lawrence Erlbaum Associates. ISBN 978-0-8058-0283-2.
    **Cite for:** Cohen's d definition and conventional benchmarks.

54. Lakens, D. (2013). Calculating and reporting effect sizes to facilitate cumulative science: A practical primer for t-tests and ANOVAs. *Frontiers in Psychology, 4*, 863. https://doi.org/10.3389/fpsyg.2013.00863
    **Cite for:** which effect sizes to report and naming the standardiser used.

55. Fritz, C. O., Morris, P. E., & Richler, J. J. (2012). Effect size estimates: Current use, calculations, and interpretation. *Journal of Experimental Psychology: General, 141*(1), 2–18. https://doi.org/10.1037/a0024338
    **Cite for:** deriving/interpreting effect sizes incl. rank-based equivalents with CIs.

56. Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *The Annals of Mathematical Statistics, 18*(1), 50–60. https://doi.org/10.1214/aoms/1177730491
    **Cite for:** canonical source of the U statistic for group comparisons.

57. Ernst, M. D. (2004). Permutation methods: A basis for exact inference. *Statistical Science, 19*(4), 676–685. https://doi.org/10.1214/088342304000000396
    **Cite for:** exact/permutation p-values when asymptotic approximations are unreliable at ~10 per group.

58. Whitehead, A. L., Julious, S. A., Cooper, C. L., & Campbell, M. J. (2016). Estimating the sample size for a pilot randomised trial to minimise the overall trial sample size for the external pilot and main trial for a continuous outcome variable. *Statistical Methods in Medical Research, 25*(3), 1057–1073. https://doi.org/10.1177/0962280215588241
    **Cite for:** the explicit "~10 per arm when a large standardized effect (0.8) is anticipated" rule — matches your ~10+10 design.

59. Cocks, K., & Torgerson, D. J. (2013). Sample size calculations for pilot randomized trials: A confidence interval approach. *Journal of Clinical Epidemiology, 66*(2), 197–201. https://doi.org/10.1016/j.jclinepi.2012.09.002
    **Cite for:** justifying pilot n by precision (CI width) rather than power.

60. Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., … Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*(85), 2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html
    **Cite for:** the scikit-learn library (RF/SVM, LOOCV utilities).

61. Varoquaux, G. (2018). Cross-validation failure: Small sample sizes lead to large error bars. *NeuroImage, 180*, 68–77. https://doi.org/10.1016/j.neuroimage.2017.06.061
    **Cite for:** framing LOOCV results as a demonstration with wide uncertainty, not a deployable accuracy estimate. **⚠ Venue is NeuroImage — frequently miscited as Frontiers in Neuroscience.**

62. Bouthillier, X., Delaunay, P., Bronzi, M., Trofimov, A., Nichyporuk, B., Szeto, J., … Vincent, P. (2021). Accounting for variance in machine learning benchmarks. *Proceedings of Machine Learning and Systems, 3*. https://proceedings.mlsys.org/paper_files/paper/2021/file/0184b0cd3cfb185989f858a1d9f5c1eb-Paper.pdf (preprint: arXiv:2103.03098)
    **Cite for:** acknowledging data-split variance in single-run classifier comparisons. *(Published MLSys 2021, vol. 3 — the arXiv preprint's "MLSys 2020" date is superseded.)*

63. Seabold, S., & Perktold, J. (2010). Statsmodels: Econometric and statistical modeling with Python. *Proceedings of the 9th Python in Science Conference (SciPy 2010)*. https://doi.org/10.25080/Majora-92bf1922-011
    **Cite for:** the statsmodels package used for statistical reporting.

64. Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Weckesser, W., … SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods, 17*(3), 261–272. https://doi.org/10.1038/s41592-019-0686-2
    **Cite for:** SciPy routines (e.g., `mannwhitneyu` exact p-values) underlying reported statistics.

---

## 10. Research Ethics

65. World Medical Association. (2013). World Medical Association Declaration of Helsinki: Ethical principles for medical research involving human subjects. *JAMA, 310*(20), 2191–2194. https://doi.org/10.1001/jama.2013.281053
    **Cite for:** the ethics statement covering consent and guardian consent for minors. *(APA Ethics Code can be added in text as https://www.apa.org/ethics/code if your department expects it.)*

---

## Citation Corrections & Verification Notes

Commonly miscited items — use these corrected forms:

- **"MediaPipe Iris: real-time iris tracking"** — no such paper exists. Cite Ablavatski et al. (2020), arXiv:2006.11341 (ref. 43).
- **Varoquaux (2018)** is in *NeuroImage 180*, 68–77 — not Frontiers in Neuroscience (ref. 61).
- **Bouthillier et al.** is *Proceedings of Machine Learning and Systems*, vol. 3, **2021** — not "MLSys 2019" (ref. 62).
- **LSL** — cite Kothe et al. (2025) *Imaging Neuroscience* (ref. 47), not "Kothe (2014), software" or a bare GitHub URL; the repo's own citation guidance says so.
- **Kaduk et al.** — published online 2023 but belongs to *Behavior Research Methods* 56(5), **2024**; cite with the volume year.
- **"Jainta & Jainta, Atypical eye movements in dyslexia"** — not verifiable; the verified equivalent is Jainta & Kapoula (2011) (ref. 31).
- **"Rello & Ballesteros 2015, Screening dyslexia for English using HR measures"** — conflates two papers. The eye-tracking paper is Rello & Ballesteros (2015) *Detecting readers with dyslexia…* (ref. 34). The separate English/HCI-measures paper is Rello et al. (2018), *Screening dyslexia for English using HCI measures and machine learning*, W4A '18, https://doi.org/10.1145/3194658.3194675 — note it uses **HCI measures, not eye tracking**.
- **Drotár & Dobeš (2020)** — Sci Rep 10, Article **21541** (verified on nature.com; some secondary sources print 21760).
- **Tressoldi / Hayotte** as copying-eye-hand-span authors — could not be verified; excluded rather than guessed. The verified French copying literature is Kandel and colleagues.
- **Kandel & Valdois (2006)** — "Syllables as functional units in a copying task" is by **Kandel & Valdois** (not "Kandel 2009").
- **Asselborn et al. (2018)** — middle author(s) elided exactly as printed by the publisher (6 + ellipsis + last).
- **Lambert et al. (2023)** — page numbers omitted (Springer chapter header pagination ambiguous); the DOI resolves regardless.
- **Hamstra-Bletz et al. (1987)** — Dutch book, no DOI; den Brinker's initials appear as both "B.P.O.L." and "B.P.L.M." across sources — pick your citation style's form and be consistent.

**Optional swap:** Rayner, K. (1978). Eye movements in reading and information processing. *Psychological Bulletin, 85*(3), 618–660. https://doi.org/10.1037/0033-2909.85.3.618 — if you need a general reading-eye-movement framing reference.
