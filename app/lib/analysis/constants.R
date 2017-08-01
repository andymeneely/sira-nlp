# Metric Labels ----

## Comment Level Metrics ====

### Complexity ####

COMMENT.YNGVE.LABELS <- c(
  "min_yngve" = "Minimum Yngve",
  "med_yngve" = "Median Yngve",
  "mean_yngve" = "Mean Yngve",
  "var_yngve" = "Variance in Yngve",
  "max_yngve" = "Maximum Yngve"
)
COMMENT.FRAZIER.LABELS <- c(
  "min_frazier" = "Minimum Frazier",
  "med_frazier" = "Median Frazier",
  "mean_frazier" = "Mean Frazier",
  "var_frazier" = "Variance in Frazier",
  "max_frazier" = "Maximum Frazier"
)
COMMENT.PDENSITY.LABELS <- c(
  "min_pdensity" = "Minimum p-density",
  "med_pdensity" = "Median p-density",
  "mean_pdensity" = "Mean p-density",
  "var_pdensity" = "Variance in p-density",
  "max_pdensity" = "Maximum p-density"
)
COMMENT.CDENSITY.LABELS <- c(
  "min_cdensity" = "Minimum c-density",
  "med_cdensity" = "Median c-density",
  "mean_cdensity" = "Mean c-density",
  "var_cdensity" = "Variance in c-density",
  "max_cdensity" = "Maximum c-density"
)

### Sentiment ####

COMMENT.SENTIMENT.LABELS <- c(
  "pct_neg_sentences" = "% Negative",
  "pct_neu_sentences" = "% Neutral",
  "pct_pos_sentences" = "% Positive",
  "pct_nne_sentences" = "% Non-neutral"
)

### Uncertainty ####

COMMENT.UNCERTAINTY.LABELS <- c(
  "pct_dox_sentences" = "% Doxastic",
  "pct_epi_sentences" = "% Epistemic",
  "pct_con_sentences" = "% Conditional",
  "pct_inv_sentences" = "% Investigative",
  "pct_unc_sentences" = "% Uncertain"
)

### Politeness ####

COMMENT.POLITENESS.LABELS <- c(
  "min_politeness" = "Minimum Politeness",
  "med_politeness" = "Median Politeness",
  "mean_politeness" = "Mean Politeness",
  "var_politeness" = "Variance in Politeness",
  "max_politeness" = "Maximum Politeness"
)

### Formality ####

COMMENT.FORMALITY.LABELS <- c(
  "min_formality" = "Minimum Formality",
  "med_formality" = "Median Formality",
  "mean_formality" = "Mean Formality",
  "var_formality" = "Variance in Formality",
  "max_formality" = "Maximum Formality"
)

### Informativeness ####

COMMENT.INFORMATIVENESS.LABELS <- c(
  "min_informativeness" = "Minimum Informativeness",
  "med_informativeness" = "Median Informativeness",
  "mean_informativeness" = "Mean Informativeness",
  "var_informativeness" = "Variance in Informativeness",
  "max_informativeness" = "Maximum Informativeness"
)

### Implicature ####

COMMENT.IMPLICATURE.LABELS <- c(
  "min_implicature" = "Minimum Implicature",
  "med_implicature" = "Median Implicature",
  "mean_implicature" = "Mean Implicature",
  "var_implicature" = "Variance in Implicature",
  "max_implicature" = "Maximum Implicature"
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
  "slength" = "Sentence Length"
)

# Miscellaneous ----

COMMENT.TYPE.LABELS <- c("useful" = "Acted Upon", "notuseful" = "Others")
