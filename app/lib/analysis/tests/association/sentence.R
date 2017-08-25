# Initialize Boilerplate ----
source("boilerplate.R")
source("data/sentence.R")

InitGlobals()

## Test: Continuous-valued Metrics ====
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
  SaveSplits(splits, granularity = "sentence", metric = metric)
  test.outcome <- GetAssociation(splits$x, splits$y, "useful", "notuseful")
  test.outcome <- data.frame("metric" = label, test.outcome)
  rownames(test.outcome) <- c()
  test.outcomes <- rbind(test.outcomes, test.outcome)
}
print(test.outcomes)

## Test: Boolean-valued Metrics ====
test.outcomes <- data.frame()
for (i in 1:length(SENTENCE.BV.METRICS)) {
  bv.metric <- SENTENCE.BV.METRICS[i]
  bv.label <- SENTENCE.METRIC.LABELS[bv.metric]
  cat(i, " ", bv.label, "\n", sep = "")

  bv.metric.variants <- unlist(SENTENCE.BV.METRIC.VARIANTS[[bv.metric]])

  dataset <- GetSentenceMetric(bv.metric, normalize = F)
  for (j in 1:length(SENTENCE.CV.METRICS)) {
    cv.metric <- SENTENCE.CV.METRICS[j]
    cv.label <- SENTENCE.METRIC.LABELS[cv.metric]
    cat("  ", j, " ", cv.label, "\n", sep = "")

    analysis.dataset <- GetSentenceMetric(cv.metric, normalize= F) %>%
      inner_join(., dataset, by = SENTENCE.KEYS) %>%
      select(-comment_id, -sentence_id)
    for (k in 1:length(bv.metric.variants)) {
      bv.metric.variant <- bv.metric.variants[k]
      bv.metric.variant.label <- SENTENCE.METRIC.LABELS[bv.metric.variant]

      cat("    ", k, " ", bv.metric.variant.label, "\n", sep = "")

      splits <- Split(analysis.dataset, bv.metric.variant, T, F, cv.metric)
      SaveSplits(splits, granularity = "sentence",
                 metric = paste(cv.metric, ".", bv.metric.variant, sep = ""))
      test.outcome <- GetAssociation(splits$x, splits$y, "yes", "no")
      test.outcome <- data.frame("metric" = paste(cv.label, "+",
                                                  bv.metric.variant.label),
                                 test.outcome)
      rownames(test.outcome) <- c()
      test.outcomes <- rbind(test.outcomes, test.outcome)
    }
  }
}
print(test.outcomes)
