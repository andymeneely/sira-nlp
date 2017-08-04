# Initialize Boilerplate ----
source("boilerplate.R")
source("data/comment.R")

## Test: Continuous-values Metrics ====
metrics <- names(COMMENT.CV.METRIC.VARIANTS)

test.outcomes <- data.frame()
for (i in 1:length(metrics)) {
  metric <- metrics[i]
  metric.label <- COMMENT.METRIC.LABELS[[metric]]
  cat("[", i, "/", length(metrics), "] ", metric.label, "\n", sep = "")

  dataset <- GetCommentMetric(metric)

  variants <- unlist(COMMENT.CV.METRIC.VARIANTS[[metric]])
  for (j in 1:length(variants)) {
    metric.variant <- variants[j]
    variant.label <- COMMENT.METRIC.LABELS[[metric.variant]]
    cat(" [", j, "/", length(variants), "] ", variant.label, "\n", sep = "")

    test.outcome <- GetNormality(dataset[[metric.variant]])
    test.outcome <- data.frame("metric" = variant.label, test.outcome)
    rownames(test.outcome) <- c()
    test.outcomes <- rbind(test.outcomes, test.outcome)
  }
}
print(test.outcomes)
