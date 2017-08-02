# Initialize Boilerplate ----
source("boilerplate.R")
source("data/sentence.R")

## Continuous Valued Metrics ====

### Query Data ####
dataset <- GetContinuousMetrics()

analysis.dataset <- dataset %>%
  select(-comment_id, -sentence_id)

### Test: Spearman's ####
metrics <- colnames(analysis.dataset)

done <- 0
total <- length(metrics) * (length(metrics) - 1) / 2

test.outcomes <- data.frame()
for (i in 1:(length(metrics) - 1)) {
  for (j in (i + 1):length(metrics)) {
    done <- done + 1

    column.one <- metrics[i]
    label.one <- SENTENCE.METRIC.LABELS[column.one]
    column.two <- metrics[j]
    label.two <- SENTENCE.METRIC.LABELS[column.two]

    cat("[", done, "/", total, "] ", label.one, " and ", label.two, "\n",
        sep = "")

    test.outcome <- GetSpearmansRho(analysis.dataset, column.one, column.two)
    test.outcome <- data.frame("X" = label.one, "Y" = label.two, test.outcome)
    rownames(test.outcome) <- c()

    test.outcomes <- rbind(test.outcomes, test.outcome)
  }
}

### Test: Variable Clustering ####
test.outcome <- varclus(as.matrix(analysis.dataset))

