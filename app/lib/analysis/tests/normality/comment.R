# Initialize Boilerplate ----
source("boilerplate.R")
source("data/comment.R")

## Yngve ====

### Query Data
dataset <- GetCommentYngve(normalize = F)

### Test
TestNormality(dataset$min_yngve, label = "Minimum Yngve")
TestNormality(dataset$mean_yngve, label = "Mean Yngve")
TestNormality(dataset$med_yngve, label = "Median Yngve")
TestNormality(dataset$var_yngve, label = "Variance in Yngve")
TestNormality(dataset$max_yngve, label = "Maximum Yngve")

## Frazier ====

### Query Data
dataset <- GetCommentFrazier(normalize = F)

### Test
TestNormality(dataset$min_frazier, label = "Minimum Frazier")
TestNormality(dataset$mean_frazier, label = "Mean Frazier")
TestNormality(dataset$med_frazier, label = "Median Frazier")
TestNormality(dataset$var_frazier, label = "Variance in Frazier")
TestNormality(dataset$max_frazier, label = "Maximum Frazier")

## Propositional Density ====

### Query Data
dataset <- GetCommentPdensity(normalize = F)

### Test
TestNormality(dataset$min_pdensity, label = "Minimum Propositional Density")
TestNormality(dataset$mean_pdensity, label = "Mean Propositional Density")
TestNormality(dataset$med_pdensity, label = "Median Propositional Density")
TestNormality(dataset$var_pdensity, label = "Variance in Propositional Density")
TestNormality(dataset$max_pdensity, label = "Maximum Propositional Density")

## Content Density ====

### Query Data
dataset <- GetCommentCdensity(normalize = F)

### Test
TestNormality(dataset$min_cdensity, label = "Minimum Content Density")
TestNormality(dataset$mean_cdensity, label = "Mean Content Density")
TestNormality(dataset$med_cdensity, label = "Median Content Density")
TestNormality(dataset$var_cdensity, label = "Variance in Content Density")
TestNormality(dataset$max_cdensity, label = "Maximum Content Density")

## Sentiment ====

### Query Data
dataset <- GetCommentSentiment(normalize = F)

### Test
TestNormality(dataset$pct_neg_sentences, label = "% Negative Sentences")
TestNormality(dataset$pct_neu_sentences, label = "% Neutral Sentences")
TestNormality(dataset$pct_pos_sentences, label = "% Positive Sentences")
TestNormality(dataset$pct_nne_sentences, label = "% Non-neutral Sentences")

## Uncertainty ====

### Query Data
dataset <- GetCommentUncertainty(normalize = F)

### Test
TestNormality(dataset$pct_dox_sentences, label = "% Doxastic Sentences")
TestNormality(dataset$pct_epi_sentences, label = "% Epistemic Sentences")
TestNormality(dataset$pct_con_sentences, label = "% Conditional Sentences")
TestNormality(dataset$pct_inv_sentences, label = "% Investigative Sentences")
TestNormality(dataset$pct_unc_sentences, label = "% Uncertain Sentences")


## Politeness ====

### Query Data
dataset <- GetCommentPoliteness(normalize = F)

### Test
TestNormality(dataset$min_politeness, label = "Minimum Politeness")
TestNormality(dataset$mean_politeness, label = "Mean Politeness")
TestNormality(dataset$med_politeness, label = "Median Politeness")
TestNormality(dataset$var_politeness, label = "Variance in Politeness")
TestNormality(dataset$max_politeness, label = "Maximum Politeness")

## Formality ====

### Query Data
dataset <- GetCommentFormality(normalize = F)

### Test
TestNormality(dataset$min_formality, label = "Minimum Formality")
TestNormality(dataset$mean_formality, label = "Mean Formality")
TestNormality(dataset$med_formality, label = "Median Formality")
TestNormality(dataset$var_formality, label = "Variance in Formality")
TestNormality(dataset$max_formality, label = "Maximum Formality")

## Informativeness ====

### Query Data
dataset <- GetCommentInformativeness(normalize = F)

### Test
TestNormality(dataset$min_informativeness, label = "Minimum Informativeness")
TestNormality(dataset$mean_informativeness, label = "Mean Informativeness")
TestNormality(dataset$med_informativeness, label = "Median Informativeness")
TestNormality(dataset$var_informativeness,
              label = "Variance in Informativeness")
TestNormality(dataset$max_informativeness, label = "Maximum Informativeness")

## Implicature ====

### Query Data
dataset <- GetCommentImplicature(normalize = F)

### Test
TestNormality(dataset$min_implicature, label = "Minimum Implicature")
TestNormality(dataset$mean_implicature, label = "Mean Implicature")
TestNormality(dataset$med_implicature, label = "Median Implicature")
TestNormality(dataset$var_implicature, label = "Variance in Implicature")
TestNormality(dataset$max_implicature, label = "Maximum Implicature")
