source("data/sentence.R")

COMMENT.KEYS <- c("comment_id")

# Natural Language Metrics ----

GetCommentYngve <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      max((s.metrics #>> '{complexity,yngve}')::numeric) AS yngve
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true AND
      s.metrics #>> '{complexity,yngve}' <> 'null'
    GROUP BY cs.comment_id;
  "
  if (normalize)
    query <- "
      SELECT i.comment_id AS comment_id,
        max(i.yngve) AS yngve
      FROM (
        SELECT cs.comment_id AS comment_id,
          (
            (s.metrics #>> '{complexity,yngve}')::numeric /
            (SELECT COUNT(*) FROM token t WHERE t.sentence_id = s.id)
          ) AS yngve
        FROM comment c
          JOIN comment_sentences cs ON cs.comment_id = c.id
          JOIN sentence s ON s.id = cs.sentence_id
        WHERE c.by_reviewer IS true AND
          s.metrics #>> '{complexity,yngve}' <> 'null'
      ) AS i
      GROUP BY i.comment_id;
    "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetCommentFrazier <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      max((s.metrics #>> '{complexity,frazier}')::numeric) AS frazier
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true AND
      s.metrics #>> '{complexity,frazier}' <> 'null'
    GROUP BY cs.comment_id;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetCommentPdensity <- function(normalize = TRUE) {
  dataset <- GetSentencePdensity(normalize) %>%
    inner_join(., GetSentenceWeight(normalize), by = SENTENCE.KEYS) %>%
    mutate(pdensity = pdensity * weight) %>%
    group_by(comment_id) %>%
    summarise(pdensity = sum(pdensity))
  return(dataset)
}

GetCommentCdensity <- function(normalize = TRUE) {
  query <- "
    SELECT c.id AS comment_id,
      (c.metrics #>> '{complexity,cdensity}')::numeric AS cdensity
    FROM comment c
    WHERE c.by_reviewer IS true AND
      c.metrics #>> '{complexity,cdensity}' <> 'null';
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetCommentSentiment <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      (
        (s.metrics #>> '{sentiment,vneg}')::int +
        (s.metrics #>> '{sentiment,neg}')::int
      ) AS is_negative,
      (s.metrics #>> '{sentiment,vneg}')::int AS is_neutral,
      (
        (s.metrics #>> '{sentiment,pos}')::int +
        (s.metrics #>> '{sentiment,vpos}')::int
      ) AS is_positive,
      (
        (s.metrics #>> '{sentiment,vneg}')::int +
        (s.metrics #>> '{sentiment,neg}')::int +
        (s.metrics #>> '{sentiment,pos}')::int +
        (s.metrics #>> '{sentiment,vpos}')::int
      ) AS is_nonneutral
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true AND
      s.metrics #>> '{sentiment,vneg}' <> 'null' AND
      s.metrics #>> '{sentiment,neg}' <> 'null' AND
      s.metrics #>> '{sentiment,neut}' <> 'null' AND
      s.metrics #>> '{sentiment,pos}' <> 'null' AND
      s.metrics #>> '{sentiment,vpos}' <> 'null';
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)

  dataset <- dataset %>%
    inner_join(., GetSentenceLength(normalize), by = SENTENCE.KEYS) %>%
    mutate(num_neg_tokens = is_negative * num_tokens) %>%
    mutate(num_neu_tokens = is_neutral * num_tokens) %>%
    mutate(num_pos_tokens = is_positive * num_tokens) %>%
    mutate(num_nne_tokens = is_nonneutral * num_tokens) %>%
    group_by(comment_id) %>%
    summarize(num_neg_tokens = sum(num_neg_tokens),
              num_neu_tokens = sum(num_neu_tokens),
              num_pos_tokens = sum(num_pos_tokens),
              num_nne_tokens = sum(num_nne_tokens),
              num_tokens = sum(num_tokens)) %>%
    mutate(pct_neg_tokens = num_neg_tokens / num_tokens) %>%
    mutate(pct_neu_tokens = num_neu_tokens / num_tokens) %>%
    mutate(pct_pos_tokens = num_pos_tokens / num_tokens) %>%
    mutate(pct_nne_tokens = num_nne_tokens / num_tokens) %>%
    select(comment_id, pct_neg_tokens, pct_neu_tokens, pct_pos_tokens,
           pct_nne_tokens)

  return(dataset)
}

GetCommentUncertainty <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      EXISTS(
        SELECT *
        FROM token t
        WHERE t.sentence_id = cs.sentence_id AND t.uncertainty = 'D'
      ) AS is_doxastic,
      EXISTS(
        SELECT *
        FROM token t
        WHERE t.sentence_id = cs.sentence_id AND t.uncertainty = 'E'
      ) AS is_epistemic,
      EXISTS(
        SELECT *
        FROM token t
        WHERE t.sentence_id = cs.sentence_id AND t.uncertainty = 'N'
      ) AS is_conditional,
      EXISTS(
        SELECT *
        FROM token t
        WHERE t.sentence_id = cs.sentence_id AND t.uncertainty = 'I'
      ) AS is_investigative,
      EXISTS(
        SELECT *
        FROM token t
        WHERE t.sentence_id = cs.sentence_id AND t.uncertainty <> 'C'
      ) AS is_uncertain
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)

  dataset <- dataset %>%
    group_by(comment_id) %>%
    summarise(has_doxastic = sum(is_doxastic) > 0,
              has_epistemic = sum(is_epistemic) > 0,
              has_conditional = sum(is_conditional) > 0,
              has_investigative = sum(is_investigative) > 0,
              has_uncertainty = sum(is_uncertain) > 0) %>%
    select(comment_id, has_doxastic, has_epistemic, has_conditional,
           has_investigative, has_uncertainty)
  return(dataset)
}

GetCommentPoliteness <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      min((s.metrics #>> '{politeness,polite}')::numeric)
        AS min_politeness,
      max((s.metrics #>> '{politeness,polite}')::numeric)
        AS max_politeness
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true
    GROUP BY cs.comment_id;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetCommentFormality <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      min((s.metrics #>> '{formality,formal}')::numeric)
        AS min_formality,
      max((s.metrics #>> '{formality,formal}')::numeric)
        AS max_formality
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true
    GROUP BY cs.comment_id;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetCommentInformativeness <- function(normalize = TRUE) {
  stop("Not implemented")
  query <- "
    SELECT cs.comment_id AS comment_id,
      min((s.metrics #>> '{informativeness,informative}')::numeric)
        AS min_informativeness,
      median((s.metrics #>> '{informativeness,informative}')::numeric)
        AS med_informativeness,
      avg((s.metrics #>> '{informativeness,informative}')::numeric)
        AS mean_informativeness,
      variance((s.metrics #>> '{informativeness,informative}')::numeric)
        AS var_informativeness,
      max((s.metrics #>> '{informativeness,informative}')::numeric)
        AS max_informativeness
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true
    GROUP BY cs.comment_id;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetCommentImplicature <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      max((s.metrics #>> '{implicature,implicative}')::numeric)
        AS implicature
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true
    GROUP BY cs.comment_id;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

# Experience Metrics ----

GetProjectExperience <- function(normalize = TRUE) {
  query <- "
    SELECT c.id AS comment_id,
      (c.metrics #>> '{experience,project,uniform}')::numeric
        AS uni_prj_experience,
      (c.metrics #>> '{experience,project,proportional}')::numeric
        AS prp_prj_experience
    FROM comment c
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(na.omit(dataset))
}

GetModuleExperience <- function(normalize = TRUE) {
  query <- "
    SELECT c.id AS comment_id,
      (c.metrics #>> '{experience,module,uniform}')::numeric
        AS uni_mod_experience,
      (c.metrics #>> '{experience,module,proportional}')::numeric
        AS prp_mod_experience
    FROM comment c
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(na.omit(dataset))
}

GetFileExperience <- function(normalize = TRUE) {
  query <- "
    SELECT c.id AS comment_id,
      (c.metrics #>> '{experience,file,uniform}')::numeric
        AS uni_fil_experience,
      (c.metrics #>> '{experience,file,proportional}')::numeric
        AS prp_fil_experience
    FROM comment c
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(na.omit(dataset))
}

GetBugFamiliarity <- function(normalize = TRUE) {
  query <- "
    SELECT c.id AS comment_id,
      (c.metrics #>> '{experience,bug}')::boolean AS is_bugfamiliar
    FROM comment c
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(na.omit(dataset))
}

# Miscellaneous ----

GetCommentContinuousMetrics <- function(normalize = TRUE) {
  dataset <- NA

  interim.dataset <- GetCommentYngve(normalize = normalize)
  dataset <- interim.dataset

  interim.dataset <- GetCommentFrazier(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = COMMENT.KEYS)

  interim.dataset <- GetCommentPdensity(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = COMMENT.KEYS)

  interim.dataset <- GetCommentCdensity(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = COMMENT.KEYS)

  interim.dataset <- GetCommentSentiment(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = COMMENT.KEYS)

  interim.dataset <- GetCommentPoliteness(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = COMMENT.KEYS)

  interim.dataset <- GetCommentFormality(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = COMMENT.KEYS)

  return(dataset)
}

GetCommentMetric <- function(metric, normalize = TRUE) {
  dataset = switch(metric,
                   yngve = GetCommentYngve(normalize),
                   frazier = GetCommentFrazier(normalize),
                   pdensity = GetCommentPdensity(normalize),
                   cdensity = GetCommentCdensity(normalize),
                   sentiment = GetCommentSentiment(normalize),
                   uncertainty = GetCommentUncertainty(normalize),
                   politeness = GetCommentPoliteness(normalize),
                   formality = GetCommentFormality(normalize),
                   informativeness = GetCommentInformativeness(normalize),
                   implicature = GetCommentImplicature(normalize),
                   project_experience = GetProjectExperience(normalize),
                   module_experience = GetModuleExperience(normalize),
                   file_experience = GetFileExperience(normalize))
  return(dataset)
}

GetCommentLength <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id, COUNT(*) AS num_sentences
    FROM comment_sentences cs
      JOIN comment c ON c.id = cs.comment_id
    WHERE c.by_reviewer IS true
    GROUP BY cs.comment_id;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(na.omit(dataset))
}

GetSentenceWeight <- function(normalize = TRUE) {
  connection <- GetDbConnection(db.settings)
  query <- "
    SELECT cs.comment_id AS comment_id,
      COUNT(*) AS num_tokens_in_comment
    FROM comment_sentences cs
      JOIN comment c ON c.id = cs.comment_id
      JOIN token t ON t.sentence_id = cs.sentence_id
    WHERE c.by_reviewer IS true
    GROUP BY cs.comment_id;
  "
  interim.dataset <- GetData(connection, query)

  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      COUNT(*) AS num_tokens_in_sentence
    FROM comment_sentences cs
      JOIN comment c ON c.id = cs.comment_id
      JOIN token t ON t.sentence_id = cs.sentence_id
    WHERE c.by_reviewer IS true
    GROUP BY cs.comment_id, cs.sentence_id;
  "
  dataset <- GetData(connection, query)
  Disconnect(connection)

  dataset <- inner_join(dataset, interim.dataset, by = COMMENT.KEYS) %>%
    mutate(weight = num_tokens_in_sentence / num_tokens_in_comment) %>%
    select(comment_id, sentence_id, weight)
  return(na.omit(dataset))
}
