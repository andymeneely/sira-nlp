# Initialize Boilerplate ----
source("boilerplate.R")
source("data/sentence.R")

## Yngve ====

### Query Data
dataset <- GetSentenceYngve(normalize = F)

### Test
TestNormality(dataset$yngve, label = "Yngve")

## Frazier ====

### Query Data
dataset <- GetSentenceFrazier(normalize = F)

### Test
TestNormality(dataset$frazier, label = "Frazier")

## Propositional Density ====

### Query Data
dataset <- GetSentencePdensity(normalize = F)

### Test
TestNormality(dataset$pdensity, label = "Propositional Density")

## Content Density ====

### Query Data
dataset <- GetSentenceCdensity(normalize = F)

### Test
TestNormality(dataset$cdensity, label = "Content Density")

## Politeness ====

### Query Data
dataset <- GetSentencePoliteness(normalize = F)

### Test
TestNormality(dataset$politeness, label = "Politeness")

## Formality ====

### Query Data
dataset <- GetSentenceFormality(normalize = F)

### Test
TestNormality(dataset$formality, label = "Formality")

## Informativeness ====

### Query Data
dataset <- GetSentenceInformativeness(normalize = F)

### Test
TestNormality(dataset$informativeness, label = "Informativeness")

## Implicature ====

### Query Data
dataset <- GetSentenceImplicature(normalize = F)

### Test
TestNormality(dataset$implicature, label = "Implicature")
