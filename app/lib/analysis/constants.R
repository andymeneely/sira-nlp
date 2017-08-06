# Metrics

# Metrics ----

## Comment Level Metrics ====

### Boolean Valued
COMMENT.BV.METRICS <- c(
  "uncertainty"
)

UNCERTAINTY.VARIANTS <- c(
  "has_doxastic",
  "has_epistemic",
  "has_conditional",
  "has_investigative",
  "has_uncertainty"
)

COMMENT.BV.METRICS.VARIANTS <- c(
  "uncertainty" = UNCERTAINTY.VARIANTS
)

### Continuous Valued
COMMENT.CV.METRICS <- c(
  "yngve",
  "frazier",
  "pdensity",
  "cdensity",
  "sentiment",
  "politeness",
  "formality",
  "informativeness",
  "implicature",
  "experience"
)

SENTIMENT.VARIANTS <- c(
  "pct_neg_tokens",
  "pct_neu_tokens",
  "pct_pos_tokens",
  "pct_nne_tokens"
)
POLITENESS.VARIANTS <- c(
  "min_politeness",
  "max_politeness"
)
FORMALITY.VARIANTS <- c(
  "min_formality",
  "max_formality"
)
EXPERIENCE.VARIANTS <- c(
  "prj_uni_experience",
  "prj_prp_experience",
  "mod_uni_experience",
  "mod_prp_experience",
  "fil_uni_experience",
  "fil_prp_experience"
)

COMMENT.CV.METRIC.VARIANTS <- c(
  "sentiment" = SENTIMENT.VARIANTS,
  "politeness" = POLITENESS.VARIANTS,
  "formality" = FORMALITY.VARIANTS,
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
  # Complexity
  "yngve" = "Yngve",
  "frazier" = "Frazier",
  "pdensity" = "p-density",
  "cdensity" = "c-density",
  # Sentiment
  "pct_neg_tokens" = "Negativity",
  "pct_neu_tokens" = "Neutrality",
  "pct_pos_tokens" = "Positivity",
  "pct_nne_tokens" = "Non-neutrality",
  # Uncertainty
  "has_doxastic" = "Has Doxastic",
  "has_epistemic" = "Has Epistemic",
  "has_conditional" = "Has Conditional",
  "has_investigative" = "Has Investigative",
  "has_uncertainty" = "Has Uncertainty",
  # Politeness
  "min_politeness" = "Minimum Politeness",
  "max_politeness" = "Maximum Politeness",
  # Formality
  "min_formality" = "Minimum Formality",
  "max_formality" = "Maximum Formality",
  # Informativeness
  "informativeness" = "Informativeness",
  # Implicature
  "implicature" = "Implicature",
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
  "num_sentences" = "# Sentences"
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
  "num_tokens" = "# Tokens"
)

# Miscellaneous ----

COMMENT.TYPE.LABELS <- c("useful" = "Acted Upon", "notuseful" = "Others")
