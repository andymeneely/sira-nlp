# Metrics

# Metrics ----

## Comment Level Metrics ====

### Boolean Valued
COMMENT.BV.METRICS <- c(
  "uncertainty"
)

COMMENT.UNCERTAINTY.VARIANTS <- c(
  "has_doxastic",
  "has_epistemic",
  "has_conditional",
  "has_investigative",
  "has_uncertainty"
)

COMMENT.BV.METRIC.VARIANTS <- list(
  "uncertainty" = COMMENT.UNCERTAINTY.VARIANTS
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
  "project_experience",
  "module_experience",
  "file_experience"
)

COMMENT.SENTIMENT.VARIANTS <- c(
  "pct_neg_tokens",
  "pct_pos_tokens",
)
COMMENT.POLITENESS.VARIANTS <- c(
  "min_politeness",
  "max_politeness"
)
COMMENT.FORMALITY.VARIANTS <- c(
  "min_formality",
  "max_formality"
)
PROJECT.EXPERIENCE.VARIANTS <- c(
  "uni_prj_experience",
  "prp_prj_experience"
)
MODULE.EXPERIENCE.VARIANTS <- c(
  "uni_mod_experience",
  "prp_mod_experience"
)
FILE.EXPERIENCE.VARIANTS <- c(
  "uni_fil_experience",
  "prp_fil_experience"
)

COMMENT.CV.METRIC.VARIANTS <- list(
  "sentiment" = COMMENT.SENTIMENT.VARIANTS,
  "politeness" = COMMENT.POLITENESS.VARIANTS,
  "formality" = COMMENT.FORMALITY.VARIANTS,
  "project_experience" = PROJECT.EXPERIENCE.VARIANTS,
  "module_experience" = MODULE.EXPERIENCE.VARIANTS,
  "file_experience" = FILE.EXPERIENCE.VARIANTS
)

## Sentence Level Metrics ====

### Boolean Valued
SENTENCE.BV.METRICS <- c(
  "sentiment",
  "uncertainty"
)

SENTENCE.SENTIMENT.VARIANTS <- c(
  "is_positive",
  "is_negative"
)

SENTENCE.UNCERTAINTY.VARIANTS <- c(
  "is_doxastic",
  "is_epistemic",
  "is_conditional",
  "is_investigative"
)

### Continuous Valued
SENTENCE.BV.METRIC.VARIANTS <- list(
  "sentiment" = SENTENCE.SENTIMENT.VARIANTS,
  "uncertainty" = SENTENCE.UNCERTAINTY.VARIANTS
)

SENTENCE.CV.METRICS <- c(
  "yngve",
  "frazier",
  "pdensity",
  "cdensity",
  "politeness",
  "formality"
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
  "sentiment" = "Sentiment",
  "pct_neg_tokens" = "Negativity",
  "pct_neu_tokens" = "Neutrality",
  "pct_pos_tokens" = "Positivity",
  "pct_nne_tokens" = "Non-neutrality",
  # Uncertainty
  "uncertainty" = "Uncertainty",
  "has_doxastic" = "Has Doxastic",
  "has_epistemic" = "Has Epistemic",
  "has_conditional" = "Has Conditional",
  "has_investigative" = "Has Investigative",
  "has_uncertainty" = "Has Uncertainty",
  # Politeness
  "politeness" = "Politeness",
  "min_politeness" = "Minimum Politeness",
  "max_politeness" = "Maximum Politeness",
  # Formality
  "formality" = "Formality",
  "min_formality" = "Minimum Formality",
  "max_formality" = "Maximum Formality",
  # Informativeness
  "informativeness" = "Informativeness",
  # Implicature
  "implicature" = "Implicature",
  # Experience
  "experience" = "Experience",
  # Experience: Project
  "project_experience" = "Project Experience",
  "uni_prj_experience" = "Unform Experience",
  "prp_prj_experience" = "Proportional Experience",
  # Experience: Module
  "module_experience" = "Module Experience",
  "uni_mod_experience" = "Unform Experience",
  "prp_mod_experience" = "Proportional Experience",
  # Experience: File
  "file_experience" = "File Experience",
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
  "uncertainty" = "Uncertainty",
  "is_doxastic" = "Is Doxastic",
  "is_epistemic" = "Is Epistemic",
  "is_conditional" = "Is Conditional",
  "is_investigative" = "Is Investigative",
  "is_uncertain" = "Is Uncertain",
  # Sentiment
  "sentiment" = "Sentiment",
  "is_negative" = "Is Negative",
  "is_neutral" = "Is Neutral",
  "is_positive" = "Is Positive",
  # Miscellaneous
  "num_tokens" = "# Tokens",
  "flesch_kincaid" = "Reading Ease"
)

# Miscellaneous ----

COMMENT.TYPE.LABELS <- c("useful" = "Acted Upon", "notuseful" = "Others")
