# Initialize Boilerplate ----
source("boilerplate.R")
source("data/sentence.R")

InitGlobals()

## Test: Continuous-values Metrics ====
test.outcomes <- data.frame()
for (i in 1:length(SENTENCE.CV.METRICS)) {
  metric <- SENTENCE.CV.METRICS[i]
  label <- SENTENCE.METRIC.LABELS[metric]
  cat("[", i, "/", length(SENTENCE.CV.METRICS), "] ", label, "\n", sep = "")

  dataset <- GetSentenceMetric(metric, normalize = TRUE)
  analysis.dataset <- dataset %>%
    inner_join(., COMMENT.TYPE, by = "comment_id") %>%
    select(-comment_id, -sentence_id)

  splits <- SplitByCommentType(analysis.dataset, metric = metric)
  test.outcome <- GetAssociation(splits$x, splits$y, "useful", "notuseful")
  test.outcome <- data.frame("metric" = label, test.outcome)
  rownames(test.outcome) <- c()
  test.outcomes <- rbind(test.outcomes, test.outcome)
}
print(test.outcomes)
