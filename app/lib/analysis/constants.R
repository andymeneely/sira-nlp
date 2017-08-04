# Metrics

# Metrics ----

## Comment Level Metrics ====

### Continuous Valued
COMMENT.CV.METRICS <- c(
  "yngve",
  "frazier",
  "pdensity",
  "cdensity",
  "sentiment",
  "uncertainty",
  "politeness",
  "formality",
  "informativeness",
  "implicature",
  "experience"
)

YNGVE.VARIANTS <- list(
  "min_yngve",
  "mean_yngve",
  "med_yngve",
  "var_yngve",
  "max_yngve"
)
FRAZIER.VARIANTS <- list(
  "min_frazier",
  "mean_frazier",
  "med_frazier",
  "var_frazier",
  "max_frazier"
)
PDENSITY.VARIANTS <- list(
  "min_pdensity",
  "mean_pdensity",
  "med_pdensity",
  "var_pdensity",
  "max_pdensity"
)
CDENSITY.VARIANTS <- list(
  "min_cdensity",
  "mean_cdensity",
  "med_cdensity",
  "var_cdensity",
  "max_cdensity"
)
SENTIMENT.VARIANTS <- list(
  "pct_neg_sentences",
  "pct_neu_sentences",
   "pct_pos_sentences",
   "pct_nne_sentences"
)
UNCERTAINTY.VARIANTS <-list(
  "pct_dox_sentences",
  "pct_epi_sentences",
  "pct_con_sentences",
  "pct_inv_sentences",
  "pct_unc_sentences"
)
POLITENESS.VARIANTS <- list(
  "min_politeness",
  "mean_politeness",
  "med_politeness",
  "var_politeness",
  "max_politeness"
)
FORMALITY.VARIANTS <-list(
  "min_formality",
  "mean_formality",
  "med_formality",
  "var_formality",
  "max_formality"
)
INFORMATIVENESS.VARIANTS <-list(
  "min_informativeness",
  "mean_informativeness",
  "med_informativeness",
  "var_informativeness",
  "max_informativeness"
)
IMPLICATURE.VARIANTS <-list(
  "min_implicature",
  "mean_implicature",
  "med_implicature",
  "var_implicature",
  "max_implicature"
)
EXPERIENCE.VARIANTS <- list(
  "prj_uni_experience",
  "prj_prp_experience",
  "mod_uni_experience",
  "mod_prp_experience",
  "fil_uni_experience",
  "fil_prp_experience"
)
COMMENT.CV.METRIC.VARIANTS <- list(
  "yngve" = YNGVE.VARIANTS,
  "frazier" = FRAZIER.VARIANTS,
  "pdensity" = PDENSITY.VARIANTS,
  "cdensity" = CDENSITY.VARIANTS,
  "sentiment" = SENTIMENT.VARIANTS,
  "uncertainty" = UNCERTAINTY.VARIANTS,
  "politeness" = POLITENESS.VARIANTS,
  "formality" = FORMALITY.VARIANTS,
  "informativeness" = INFORMATIVENESS.VARIANTS,
  "implicature" = IMPLICATURE.VARIANTS,
  "experience" = EXPERIENCE.VARIANTS
)

## Sentence Level Metrics ====
SENTENCE.CV.METRICS <- c(
  "yngve",
  "frazier",
  "pdensity",
  "cdensity",
  "politeness",
  "formality",
  "informativeness",
  "implicature"
)
# Metric Labels ----

## Comment Level Metrics ====

COMMENT.METRIC.LABELS <- c(
  # Complexity: Yngve
  "yngve" = "Yngve",
  "min_yngve" = "Minimum Yngve",
  "med_yngve" = "Median Yngve",
  "mean_yngve" = "Mean Yngve",
  "var_yngve" = "Variance in Yngve",
  "max_yngve" = "Maximum Yngve",
  # Complexity: Frazier
  "frazier" = "Frazier",
  "min_frazier" = "Minimum Frazier",
  "med_frazier" = "Median Frazier",
  "mean_frazier" = "Mean Frazier",
  "var_frazier" = "Variance in Frazier",
  "max_frazier" = "Maximum Frazier",
  # Complexity: Propositional Density
  "pdensity" = "Propositional Density",
  "min_pdensity" = "Minimum p-density",
  "med_pdensity" = "Median p-density",
  "mean_pdensity" = "Mean p-density",
  "var_pdensity" = "Variance in p-density",
  "max_pdensity" = "Maximum p-density",
  # Complexity: Content Density
  "cdensity" = "Content Density",
  "min_cdensity" = "Minimum c-density",
  "med_cdensity" = "Median c-density",
  "mean_cdensity" = "Mean c-density",
  "var_cdensity" = "Variance in c-density",
  "max_cdensity" = "Maximum c-density",
  # Sentiment
  "sentiment" = "Sentiment",
  "pct_neg_sentences" = "% Negative",
  "pct_neu_sentences" = "% Neutral",
  "pct_pos_sentences" = "% Positive",
  "pct_nne_sentences" = "% Non-neutral",
  # Uncertainty
  "uncertainty" = "Uncertainty",
  "pct_dox_sentences" = "% Doxastic",
  "pct_epi_sentences" = "% Epistemic",
  "pct_con_sentences" = "% Conditional",
  "pct_inv_sentences" = "% Investigative",
  "pct_unc_sentences" = "% Uncertain",
  # Politeness
  "politeness" = "Politeness",
  "min_politeness" = "Minimum Politeness",
  "med_politeness" = "Median Politeness",
  "mean_politeness" = "Mean Politeness",
  "var_politeness" = "Variance in Politeness",
  "max_politeness" = "Maximum Politeness",
  # Formality
  "formality" = "Formality",
  "min_formality" = "Minimum Formality",
  "med_formality" = "Median Formality",
  "mean_formality" = "Mean Formality",
  "var_formality" = "Variance in Formality",
  "max_formality" = "Maximum Formality",
  # Informativeness
  "informativeness" = "Informativeness",
  "min_informativeness" = "Minimum Informativeness",
  "med_informativeness" = "Median Informativeness",
  "mean_informativeness" = "Mean Informativeness",
  "var_informativeness" = "Variance in Informativeness",
  "max_informativeness" = "Maximum Informativeness",
  # Implicature
  "implicature" = "Implicature",
  "min_implicature" = "Minimum Implicature",
  "med_implicature" = "Median Implicature",
  "mean_implicature" = "Mean Implicature",
  "var_implicature" = "Variance in Implicature",
  "max_implicature" = "Maximum Implicature",
  # Experience
  "experience" = "Experience",
  # Experience: Project
  "uni_prj_experience" = "Unform Experience",
  "prp_prj_experience" = "Proportional Experience",
  # Experience: Module
  "uni_mod_experience" = "Unform Experience",
  "prp_mod_experience" = "Proportional Experience",
  # Experience: File
  "uni_fil_experience" = "Unform Experience",
  "prp_fil_experience" = "Proportional Experience",
  # Bug Familiarity
  "is_bugfamiliar" = "Familiar with Bug",
  # Miscellaneous
  "TRUE" = "Yes",
  "FALSE" = "No",
  "num_sentences" = "Number of Sentences"
)

## Sentence Level Metrics ====

SENTENCE.METRIC.LABELS <- c(
  # Complexity
  "yngve" = "Yngve",
  "frazier" = "Frazier",
  "pdensity" = "Propositional Density",
  "cdensity" = "Content Density",
  # Politeness
  "politeness" = "Politeness",
  # Formality
  "formality" = "Formality",
  # Informativeness
  "informativeness" = "Informativeness",
  # Implicature
  "implicature" = "Implicature",
  # Uncertainty
  "D" = "Doxastic",
  "E" = "Epistemic",
  "N" = "Conditional",
  "I" = "Investigative",
  "C" = "Certain",
  # Sentiment
  "positive" = "Positive",
  "neutral" = "Neutral",
  "negative" = "Negative",
  # Miscellaneous
  "sentence_length" = "Sentence Length"
)

# Miscellaneous ----

COMMENT.TYPE.LABELS <- c("useful" = "Acted Upon", "notuseful" = "Others")
