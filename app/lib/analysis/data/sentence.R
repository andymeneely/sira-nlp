GetYngve <- function(normalize = FALSE){
  query <- "
    SELECT cs.comment_id AS comment_id,
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
  if(normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetFrazier <- function(normalize = FALSE){
  query <- "
    SELECT cs.comment_id AS comment_id,
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
  if(normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetPdensity <- function(normalize = FALSE){
  query <- "
    SELECT cs.comment_id AS comment_id,
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
  if(normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetCdensity <- function(normalize = FALSE){
  query <- "
    SELECT cs.comment_id AS comment_id,
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
  if(normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetSentiment <- function(normalize = FALSE){
  query <- "
    SELECT cs.comment_id AS comment_id,
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
  if(normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetUncertainty <- function(normalize = FALSE){
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
  if(normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetPoliteness <- function(normalize = FALSE){
  query <- "
    SELECT cs.comment_id AS comment_id,
      (s.metrics #>> '{politeness,polite}')::numeric AS politeness
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  if(normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetFormality <- function(normalize = FALSE){
  query <- "
    SELECT cs.comment_id AS comment_id,
      (s.metrics #>> '{formality,formal}')::numeric AS formality
    FROM comment c
      JOIN comment_sentences cs ON cs.comment_id = c.id
      JOIN sentence s ON s.id = cs.sentence_id
    WHERE c.by_reviewer IS true;
  "
  connection <- GetDbConnection(db.settings)
  dataset <- GetData(connection, query)
  Disconnect(connection)
  if(normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetInformativeness <- function(normalize = FALSE){
  query <- "
    SELECT cs.comment_id AS comment_id,
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
  if(normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}

GetImplicature <- function(normalize = FALSE){
  query <- "
    SELECT cs.comment_id AS comment_id,
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
  dataset <- dataset %>%
    mutate(implicature = as.numeric(implicature))
  dataset <- na.omit(dataset)
  if(normalize)
    warning("No implementation for normalization yet.")
  return(dataset)
}
