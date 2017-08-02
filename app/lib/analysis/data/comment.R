GetYngve <- function(normalize = TRUE){
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
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  if (normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetFrazier <- function(normalize = TRUE){
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
  if (normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetPdensity <- function(normalize = TRUE){
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
  if (normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetCdensity <- function(normalize = TRUE){
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
  if (normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetSentiment <- function(normalize = TRUE){
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
    if (normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetUncertainty <- function(normalize = TRUE){
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
    if (normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetPoliteness <- function(normalize = TRUE){
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
  if (normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetFormality <- function(normalize = TRUE){
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
  if (normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetInformativeness <- function(normalize = TRUE){
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
  if (normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetImplicature <- function(normalize = TRUE){
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
  if (normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetMetric <- function(metric, normalize = TRUE) {
  dataset = switch(metric,
                   yngve = GetYngve(),
                   frazier = GetFrazier(),
                   pdensity = GetPdensity(),
                   cdensity = GetCdensity(),
                   sentiment = GetSentiment(),
                   uncertainty = GetUncertainty(),
                   politeness = GetPoliteness(),
                   formality = GetFormality(),
                   informativeness = GetInformativeness(),
                   implicature = GetImplicature())
  return(dataset)
}
