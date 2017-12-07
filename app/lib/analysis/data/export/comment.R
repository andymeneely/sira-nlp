# Initialize Boilerplate ----
source("boilerplate.R")
source("data/comment.R")

InitGlobals()

# Query Data ----

## Fields: yngve, frazier, cdensity, pdensity, pct_neg_tokens, pct_neu_tokens,
##         pct_pos_tokens, pct_nne_tokens, min_formality, max_formality,
##         min_politeness, max_politeness
dataset <- GetCommentContinuousMetrics()

## Fields: has_doxastic, has_epistemic, has_conditional, has_investigative
##         has_uncertainty
dataset <- dataset %>%
  inner_join(., GetCommentUncertainty(), by = COMMENT.KEYS)

## Fields: num_sentences, num_tokens
dataset <- dataset %>%
  inner_join(., GetCommentLength(), by = COMMENT.KEYS)

# Associate with Comment Type ----
export.dataset <- dataset %>%
  inner_join(., COMMENT.TYPE, by = COMMENT.KEYS)

# Export to File ----
write.csv(export.dataset, file = "data/export.csv", row.names = F)
