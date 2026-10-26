# Literature Review

STATUS: draft v2 · 2026-09-22 · restructured to the numbered-section format; all citations drawn from the verified library in `docs/references.md`.

## 2.1. Review of Dysgraphia Screening Approaches

### 2.1.1. Dysgraphia and Product-based Assessment

Dysgraphia is a specific learning disorder with impairment in written expression, characterised by persistent handwriting difficulty disproportionate to age, intelligence, and instruction (American Psychiatric Association, 2013). Prevalence estimates range from below 10% to above 30% of school-aged children, reflecting the absence of consensus diagnostic criteria and the instability of early classification (Chung et al., 2020; Overvelde & Hulstijn, 2011). Mainstream identification relies on product-based instruments, in which a specialist inspects the finished page. Hamstra-Bletz et al. (1987) developed the BHK fast-copy test, and Barnett et al. (2007) published the Detailed Assessment of Speed of Handwriting; both score visible outcomes such as legibility, letter formation, and speed. These scales show only moderate test-retest reliability (Diekema et al., 1998) and cannot observe the writing process that produced the page (Rosenblum et al., 2003). Referral therefore tends to arrive late and to depend on specialist judgement (Chung et al., 2020).

### 2.1.2. Sensor-based Kinematic Screening

Digitising tablets stream the pen's position, pressure, and tilt at high sampling rates, which makes the writing process itself measurable. Mekyska et al. (2017) classified dysgraphic handwriting with random-forest models reaching 96% sensitivity and specificity. Asselborn et al. (2018) administered a digitised BHK copy task on a consumer tablet to 298 children and achieved 96.6% sensitivity and 99.2% specificity. Drotár and Dobeš (2020) obtained about 80% accuracy with Wacom tablet features and released their dataset publicly. This line of work validates copying as a screening paradigm on consumer hardware. Nonetheless, the tablet records only the hand; how the writer encodes the source text and moves gaze between screen and page goes unmeasured, so the visual half of the copying loop is absent from these features.

### 2.1.3. Eye Movements During Copying

Experimental work has characterised that visual half in detail. Inhoff and Wang (1992) found that in copytyping the eyes lead the hand by about three characters, roughly half a second. Kandel and Valdois (2006) showed that children lift gaze from the page to re-inspect the model and carry orthographic units such as syllables in batches. Maldarelli et al. (2015) found that children, unlike adults, re-fixate the model partway through writing a letter. Tchalenko and Miall (2009) demonstrated that encoding fixations under memory demands predict copying accuracy. Relevant to screening, Lambert et al. (2023) found that children with developmental coordination disorder, which overlaps dysgraphia, distribute more and shorter fixations over the writing area than controls.

### 2.1.4. Eye Tracking in Neurodevelopmental Screening

• Research-grade eye tracking

Research-grade trackers sample gaze at high rates with high timing precision. Nilsson Benfatto et al. (2016) identified children at risk of dyslexia with 95.6% accuracy from under one minute of tracked reading, and Rello and Ballesteros (2015) classified readers with dyslexia at about 80% accuracy from eye-movement features alone. Nonetheless, research trackers cost orders of magnitude more than a webcam and remain fixed to the laboratory, so this approach cannot scale to schools and clinics.

• Webcam-based eye tracking

Webcam gaze estimation has narrowed the accuracy gap. Kaduk et al. (2024) validated a webcam system against the EyeLink 1000 and reported about 1.4 degrees of error, and Park et al. (2024) demonstrated acceptable test-retest reliability for a tablet front camera across 200 schoolchildren. Diotaiuti et al. (2026) reviewed eye tracking across specific learning disorders and report fragmented scanpaths and reduced anticipatory gaze during copying in dysgraphia. However, webcam gaze has been validated for reading and interface tasks, not for copy tasks with head movement between screen and page, and no published protocol jointly records gaze and pen on consumer hardware. The present project addresses that gap.

## References

American Psychiatric Association. (2013). *Diagnostic and statistical manual of mental disorders* (5th ed.). American Psychiatric Publishing.

Asselborn, T., Gargot, T., Kidziński, Ł., Johal, W., Cohen, D., Jolly, C., … Dillenbourg, P. (2018). Automated human-level diagnosis of dysgraphia using a consumer tablet. *npj Digital Medicine, 1*, Article 42. https://doi.org/10.1038/s41746-018-0049-x

Barnett, A., Henderson, S. E., Scheib, B., & Schulz, J. (2007). *The Detailed Assessment of Speed of Handwriting (DASH): Manual*. Pearson Education.

Chung, P. J., Patel, D. R., & Nizami, I. (2020). Disorder of written expression and dysgraphia: Definition, diagnosis, and management. *Translational Pediatrics, 9*(Suppl. 1), S46–S54. https://doi.org/10.21037/tp.2019.11.01

Diekema, S. M., Deitz, J., & Amundson, S. J. C. (1998). Test–retest reliability of the Evaluation Tool of Children's Handwriting–Manuscript. *American Journal of Occupational Therapy, 52*(4), 248–255. https://doi.org/10.5014/ajot.52.4.248

Diotaiuti, P., Di Siena, F., Vitiello, S., Di Tore, P. A., & Mancone, S. (2026). Eye-tracking in school-age specific learning disorders: A practice-oriented narrative review of assessment and gaze-contingent interventions. *Frontiers in Education, 10*, 1759299. https://doi.org/10.3389/feduc.2025.1759299

Drotár, P., & Dobeš, M. (2020). Dysgraphia detection through machine learning. *Scientific Reports, 10*, Article 21541. https://doi.org/10.1038/s41598-020-78611-9

Hamstra-Bletz, L., De Bie, J., & den Brinker, B. P. O. L. (1987). *Beknopte Beoordelingsmethode voor Kinderhandschriften* [Concise Evaluation Scale for Children's Handwriting, BHK]. Swets & Zeitlinger.

Inhoff, A. W., & Wang, J. (1992). Encoding of text, manual movement planning, and eye-hand coordination during copytyping. *Journal of Experimental Psychology: Human Perception and Performance, 18*(2), 437–448. https://doi.org/10.1037/0096-1523.18.2.437

Kaduk, T., Goeke, C., Finger, H., & König, P. (2024). Webcam eye tracking close to laboratory standards: Comparing a new webcam-based system and the EyeLink 1000. *Behavior Research Methods, 56*(5), 5002–5022. https://doi.org/10.3758/s13428-023-02237-8

Kandel, S., & Valdois, S. (2006). Syllables as functional units in a copying task. *Language and Cognitive Processes, 21*(4), 432–452. https://doi.org/10.1080/01690960400018378

Lambert, R., Boutet, J., Labyt, É., & Jolly, C. (2023). Analysis of eye movements in children with developmental coordination disorder during a handwriting copy task. In A. Parziale et al. (Eds.), *IGS 2023, Lecture Notes in Computer Science* (Vol. 14285). Springer. https://doi.org/10.1007/978-3-031-45461-5_3

Maldarelli, J. E., Kahrs, B. A., Hunt, S. C., & Lockman, J. J. (2015). Development of early handwriting: Visual-motor control during letter copying. *Developmental Psychology, 51*(7), 879–888. https://doi.org/10.1037/a0039424

Mekyska, J., Faúndez-Zanuy, M., Mzourek, Z., Galáž, Z., Smékal, Z., & Rosenblum, S. (2017). Identification and rating of developmental dysgraphia by handwriting analysis. *IEEE Transactions on Human-Machine Systems, 47*(2), 235–248. https://doi.org/10.1109/THMS.2016.2586605

Nilsson Benfatto, M., Öqvist Seimyr, G., Ygge, J., Pansell, T., Rydberg, A., & Jacobson, C. (2016). Screening for dyslexia using eye tracking during reading. *PLOS ONE, 11*(12), e0165508. https://doi.org/10.1371/journal.pone.0165508

Overvelde, A., & Hulstijn, W. (2011). Handwriting development in grade 2 and grade 3 primary school children with normal, at risk, or dysgraphic characteristics. *Research in Developmental Disabilities, 32*(5), 540–548. https://doi.org/10.1016/j.ridd.2010.12.027

Park, S., Song, J., Eom, T.-H., & Kim, Y.-H. (2024). Reliability of a tablet computer-based dyslexia screening application using an eye-tracking system. *Annals of Child Neurology, 32*(2), 99–104. https://doi.org/10.26815/acn.2023.00360

Rello, L., & Ballesteros, M. (2015). Detecting readers with dyslexia using machine learning with eye tracking measures. In *Proceedings of the 12th Web for All Conference (W4A '15)*, Article 16. ACM. https://doi.org/10.1145/2745555.2746644

Rosenblum, S., Weiss, P. L., & Parush, S. (2003). Product and process evaluation of handwriting difficulties: A review. *Educational Psychology Review, 15*(1), 41–81. https://doi.org/10.1023/A:1021371425220

Tchalenko, J., & Miall, R. C. (2009). Eye–hand strategies in copying complex lines. *Cortex, 45*(3), 368–376. https://doi.org/10.1016/j.cortex.2007.12.012
