# Initialize Boilerplate ----
source("boilerplate.R")
source("data/sentence.R")

## Yngve ====

### Query Data
dataset <- GetYngve(normalize = F)

### Test
TestNormality(dataset$yngve, label = "Yngve")

## Frazier ====

### Query Data
dataset <- GetFrazier(normalize = F)

### Test
TestNormality(dataset$frazier, label = "Frazier")

## Propositional Density ====

### Query Data
dataset <- GetPdensity(normalize = F)

### Test
TestNormality(dataset$pdensity, label = "Propositional Density")

## Content Density ====

### Query Data
dataset <- GetCdensity(normalize = F)

### Test
TestNormality(dataset$cdensity, label = "Content Density")

## Politeness ====

### Query Data
dataset <- GetPoliteness(normalize = F)

### Test
TestNormality(dataset$politeness, label = "Politeness")

## Formality ====

### Query Data
dataset <- GetFormality(normalize = F)

### Test
TestNormality(dataset$formality, label = "Formality")

## Informativeness ====

### Query Data
dataset <- GetInformativeness(normalize = F)

### Test
TestNormality(dataset$informativeness, label = "Informativeness")

## Implicature ====

### Query Data
dataset <- GetImplicature(normalize = F)

### Test
TestNormality(dataset$implicature, label = "Implicature")
