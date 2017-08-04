KEYS <- c("comment_id", "sentence_id")

GetSentenceYngve <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      (s.metrics #>> '{complexity,yngve}')::numeric AS yngve
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true AND
      s.metrics #>> '{complexity,yngve}' <> 'null';
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  if (normalize) {
    normalization.dataset <- GetSentenceLength()
    dataset <- inner_join(dataset, normalization.dataset, by = KEYS) %>%
      mutate(yngve = ifelse(slength > 0, yngve / slength, yngve)) %>%
      select(-slength)
  }
  return(dataset)
}

GetSentenceFrazier <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      (s.metrics #>> '{complexity,frazier}')::numeric AS frazier
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true AND
      s.metrics #>> '{complexity,frazier}' <> 'null';
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetSentencePdensity <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      (s.metrics #>> '{complexity,pdensity}')::numeric AS pdensity
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true AND
      s.metrics #>> '{complexity,pdensity}' <> 'null';
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetSentenceCdensity <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      (s.metrics #>> '{complexity,cdensity}')::numeric AS cdensity
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true AND
      s.metrics #>> '{complexity,cdensity}' <> 'null';
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetSentenceSentiment <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      CASE
        WHEN (
          (s.metrics #>> '{sentiment,vneg}')::int +
          (s.metrics #>> '{sentiment,neg}')::int
        ) = 1 THEN 'negative'
        WHEN (
          (s.metrics #>> '{sentiment,pos}')::int +
          (s.metrics #>> '{sentiment,vpos}')::int
        ) = 1 THEN 'positive'
        ELSE
          'neutral'
      END AS sentiment
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
  return(dataset)
}

GetSentenceUncertainty <- function(normalize = TRUE) {
  query <- "
    SELECT DISTINCT
      cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      t.uncertainty AS uncertainty
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN token t ON t.sentence_id = cs.sentence_id
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query) %>%
    filter(uncertainty != 'C') %>%
    select(-sentence_id)
  Disconnect(connection)
  return(dataset)
}

GetSentencePoliteness <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      (s.metrics #>> '{politeness,polite}')::numeric AS politeness
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetSentenceFormality <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      (s.metrics #>> '{formality,formal}')::numeric AS formality
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetSentenceInformativeness <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      (s.metrics #>> '{informativeness,informative}')::numeric
        AS informativeness
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetSentenceImplicature <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      (s.metrics #>> '{implicature,implicative}')::numeric
        AS implicature
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetSentenceLength <- function(normalize = TRUE) {
  query <- "
    SELECT cs.comment_id AS comment_id,
      cs.sentence_id AS sentence_id,
      (SELECT COUNT(*) FROM token t WHERE t.sentence_id = s.id) AS slength
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  return(dataset)
}

GetSentenceContinuousMetrics <- function(normalize = TRUE) {
  dataset <- NA

  interim.dataset <- GetSentenceYngve(normalize = normalize)
  dataset <- interim.dataset

  interim.dataset <- GetSentenceFrazier(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetSentencePdensity(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetSentenceCdensity(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetSentencePoliteness(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetSentenceFormality(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetSentenceInformativeness(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetSentenceImplicature(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  interim.dataset <- GetSentenceLength(normalize = normalize)
  dataset <- inner_join(dataset, interim.dataset, by = KEYS)

  return(dataset)
}

GetSentenceMetric <- function(metric, normalize = TRUE) {
  dataset = switch(metric,
                   yngve = GetSentenceYngve(),
                   frazier = GetSentenceFrazier(),
                   pdensity = GetSentencePdensity(),
                   cdensity = GetSentenceCdensity(),
                   sentiment = GetSentenceSentiment(),
                   uncertainty = GetSentenceUncertainty(),
                   politeness = GetSentencePoliteness(),
                   formality = GetSentenceFormality(),
                   informativeness = GetSentenceInformativeness(),
                   implicature = GetSentenceImplicature())
  return(dataset)
}
