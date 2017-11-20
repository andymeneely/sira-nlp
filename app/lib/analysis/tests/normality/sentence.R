# Initialize Boilerplate ----
source("boilerplate.R")
source("data/sentence.R")

## Test: Continuous Valued Metrics ====
test.outcomes <- data.frame()
for (i in 1:length(SENTENCE.CV.METRICS)) {
  metric <- SENTENCE.CV.METRICS[i]
  label <- SENTENCE.METRIC.LABELS[metric]
  cat("[", i, "/", length(SENTENCE.CV.METRICS), "] ", label, "\n", sep = "")

  dataset <- GetSentenceMetric(metric, normalize = TRUE)

  test.outcome <- GetNormality(dataset[[metric]])
  test.outcome <- data.frame("metric" = label, test.outcome)
  rownames(test.outcome) <- c()
  test.outcomes <- rbind(test.outcomes, test.outcome)
}
print(test.outcomes)
