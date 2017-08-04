KEYS <- c("comment_id")

# Natural Language Metrics ----

GetCommentYngve <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      min((s.metrics #>> '{complexity,yngve}')::numeric)
        AS min_yngve,
      median((s.metrics #>> '{complexity,yngve}')::numeric)
        AS med_yngve,
      avg((s.metrics #>> '{complexity,yngve}')::numeric)
        AS mean_yngve,
      variance((s.metrics #>> '{complexity,yngve}')::numeric)
        AS var_yngve,
      max((s.metrics #>> '{complexity,yngve}')::numeric)
        AS max_yngve
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
        min(i.yngve) AS min_yngve,
        median(i.yngve) AS med_yngve,
        avg(i.yngve) AS mean_yngve,
        variance(i.yngve) AS var_yngve,
        max(i.yngve) AS max_yngve
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
      min((s.metrics #>> '{complexity,frazier}')::numeric)
        AS min_frazier,
      median((s.metrics #>> '{complexity,frazier}')::numeric)
        AS med_frazier,
      avg((s.metrics #>> '{complexity,frazier}')::numeric)
        AS mean_frazier,
      variance((s.metrics #>> '{complexity,frazier}')::numeric)
        AS var_frazier,
      max((s.metrics #>> '{complexity,frazier}')::numeric)
        AS max_frazier
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
  query <- "
    SELECT cs.comment_id AS comment_id,
      min((s.metrics #>> '{complexity,pdensity}')::numeric)
        AS min_pdensity,
      median((s.metrics #>> '{complexity,pdensity}')::numeric)
        AS med_pdensity,
      avg((s.metrics #>> '{complexity,pdensity}')::numeric)
        AS mean_pdensity,
      variance((s.metrics #>> '{complexity,pdensity}')::numeric)
        AS var_pdensity,
      max((s.metrics #>> '{complexity,pdensity}')::numeric)
        AS max_pdensity
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true AND
      s.metrics #>> '{complexity,pdensity}' <> 'null'
    GROUP BY cs.comment_id;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetCommentCdensity <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      min((s.metrics #>> '{complexity,cdensity}')::numeric)
        AS min_cdensity,
      median((s.metrics #>> '{complexity,cdensity}')::numeric)
        AS med_cdensity,
      avg((s.metrics #>> '{complexity,cdensity}')::numeric)
        AS mean_cdensity,
      variance((s.metrics #>> '{complexity,cdensity}')::numeric)
        AS var_cdensity,
      max((s.metrics #>> '{complexity,cdensity}')::numeric)
        AS max_cdensity
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true AND
      s.metrics #>> '{complexity,cdensity}' <> 'null'
    GROUP BY cs.comment_id;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetCommentSentiment <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      SUM(
        (s.metrics #>> '{sentiment,vneg}')::int +
        (s.metrics #>> '{sentiment,neg}')::int
      ) AS num_neg_sentences,
      SUM((s.metrics #>> '{sentiment,neut}')::int) AS num_neu_sentences,
      SUM(
        (s.metrics #>> '{sentiment,pos}')::int +
        (s.metrics #>> '{sentiment,vpos}')::int
      ) AS num_pos_sentences,
      SUM(
        (s.metrics #>> '{sentiment,vneg}')::int +
        (s.metrics #>> '{sentiment,neg}')::int +
        (s.metrics #>> '{sentiment,pos}')::int +
        (s.metrics #>> '{sentiment,vpos}')::int
      ) AS num_nne_sentences,
      COUNT(*) AS num_sentences
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true AND
      s.metrics #>> '{sentiment,vneg}' <> 'null' AND
      s.metrics #>> '{sentiment,neg}' <> 'null' AND
      s.metrics #>> '{sentiment,neut}' <> 'null' AND
      s.metrics #>> '{sentiment,pos}' <> 'null' AND
      s.metrics #>> '{sentiment,vpos}' <> 'null'
    GROUP BY cs.comment_id;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)

  dataset <- dataset %>%
    mutate(pct_neg_sentences = num_neg_sentences / num_sentences) %>%
    mutate(pct_neu_sentences = num_neu_sentences / num_sentences) %>%
    mutate(pct_pos_sentences = num_pos_sentences / num_sentences) %>%
    mutate(pct_nne_sentences = num_nne_sentences / num_sentences) %>%
    select(comment_id, pct_neg_sentences, pct_neu_sentences, pct_pos_sentences,
           pct_nne_sentences)
  return(dataset)
}

GetCommentUncertainty <- function(normalize = TRUE) {
  query <- "
    SELECT c.id AS comment_id,
      (
        SELECT COUNT(*)
        FROM sentence s
          JOIN comment_sentences cs ON cs.sentence_id = s.id
        WHERE cs.comment_id = c.id
          AND EXISTS(
            SELECT *
            FROM token t
            WHERE t.sentence_id = s.id AND t.uncertainty = 'D'
          )
      ) AS num_dox_sentences,
      (
        SELECT COUNT(*)
        FROM sentence s
          JOIN comment_sentences cs ON cs.sentence_id = s.id
        WHERE cs.comment_id = c.id
          AND EXISTS(
            SELECT *
            FROM token t
            WHERE t.sentence_id = s.id AND t.uncertainty = 'E'
          )
      ) AS num_epi_sentences,
      (
        SELECT COUNT(*)
        FROM sentence s
          JOIN comment_sentences cs ON cs.sentence_id = s.id
        WHERE cs.comment_id = c.id
          AND EXISTS(
            SELECT *
            FROM token t
            WHERE t.sentence_id = s.id AND t.uncertainty = 'N'
          )
      ) AS num_con_sentences,
      (
        SELECT COUNT(*)
        FROM sentence s
          JOIN comment_sentences cs ON cs.sentence_id = s.id
        WHERE cs.comment_id = c.id
          AND EXISTS(
            SELECT *
            FROM token t
            WHERE t.sentence_id = s.id AND t.uncertainty = 'I'
          )
      ) AS num_inv_sentences,
      (
        SELECT COUNT(*)
        FROM sentence s
          JOIN comment_sentences cs ON cs.sentence_id = s.id
        WHERE cs.comment_id = c.id
          AND EXISTS(
            SELECT *
            FROM token t
            WHERE t.sentence_id = s.id AND t.uncertainty <> 'C'
          )
      ) AS num_unc_sentences,
      (
        SELECT COUNT(*)
        FROM comment_sentences cs
        WHERE cs.comment_id = c.id
      ) AS num_sentences
    FROM comment c
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)

  dataset <- dataset %>%
    mutate(pct_dox_sentences = num_dox_sentences / num_sentences) %>%
    mutate(pct_epi_sentences = num_epi_sentences / num_sentences) %>%
    mutate(pct_con_sentences = num_con_sentences / num_sentences) %>%
    mutate(pct_inv_sentences = num_inv_sentences / num_sentences) %>%
    mutate(pct_unc_sentences = num_unc_sentences / num_sentences) %>%
    select(comment_id, pct_dox_sentences, pct_epi_sentences, pct_con_sentences,
           pct_inv_sentences, pct_unc_sentences)
  return(dataset)
}

GetCommentPoliteness <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      min((s.metrics #>> '{politeness,polite}')::numeric)
        AS min_politeness,
      median((s.metrics #>> '{politeness,polite}')::numeric)
        AS med_politeness,
      avg((s.metrics #>> '{politeness,polite}')::numeric)
        AS mean_politeness,
      variance((s.metrics #>> '{politeness,polite}')::numeric)
        AS var_politeness,
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
      median((s.metrics #>> '{formality,formal}')::numeric)
        AS med_formality,
      avg((s.metrics #>> '{formality,formal}')::numeric)
        AS mean_formality,
      variance((s.metrics #>> '{formality,formal}')::numeric)
        AS var_formality,
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
      min((s.metrics #>> '{implicature,implicative}')::numeric)
        AS min_implicature,
      median((s.metrics #>> '{implicature,implicative}')::numeric)
        AS med_implicature,
      avg((s.metrics #>> '{implicature,implicative}')::numeric)
        AS mean_implicature,
      variance((s.metrics #>> '{implicature,implicative}')::numeric)
        AS var_implicature,
      max((s.metrics #>> '{implicature,implicative}')::numeric)
        AS max_implicature
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
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetCommentPdensity(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetCommentCdensity(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetCommentSentiment(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetCommentUncertainty(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetCommentPoliteness(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetCommentFormality(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetCommentInformativeness(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetCommentImplicature(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  return(dataset)
}

GetCommentMetric <- function(metric, normalize = TRUE) {
  dataset = switch(metric,
                   yngve = GetCommentYngve(),
                   frazier = GetCommentFrazier(),
                   pdensity = GetCommentPdensity(),
                   cdensity = GetCommentCdensity(),
                   sentiment = GetCommentSentiment(),
                   uncertainty = GetCommentUncertainty(),
                   politeness = GetCommentPoliteness(),
                   formality = GetCommentFormality(),
                   informativeness = GetCommentInformativeness(),
                   implicature = GetCommentImplicature())
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
