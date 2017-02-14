import os

# TF-IDF Output
TFIDF_TOKENS_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'output/tfidf_tokens.csv'
    )
TFIDF_LEMMAS_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'output/tfidf_lemmas.csv'
    )

# Berkeley Parser
BERKELEY_JAR_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'lib/nlp/BerkeleyParser-1.7.jar'
    )
BERKELEY_GRAMMAR_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'lib/nlp/eng_sm6.gr'
    )

# Syntactic Complexity Output
COMPLEXITY_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'output/complexity.csv'
    )
YNGVE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'output/yngve.csv'
    )
FRAZIER_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'output/frazier.csv'
    )
PDENSITY_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'output/pdensity.csv'
    )
CDENSITY_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'output/cdensity.csv'
    )

