import os

PARSED_STACK_EXCHANGE = os.path.join(
        os.path.split(__file__)[0], 'politeness/stack-exchange.parsed.json'
    )

PARSED_WIKIPEDIA = os.path.join(
        os.path.split(__file__)[0], 'politeness/wikipedia.parsed.json'
    )

FORMALITY_CLASSIFIER_PATH = os.path.join(
        os.path.split(__file__)[0], 'squinky-corpus/cls_form.p'
    )
FORMALITY_VECTORIZER_PATH = os.path.join(
        os.path.split(__file__)[0], 'squinky-corpus/vec_form.p'
    )
INFORMATIVENESS_CLASSIFIER_PATH = os.path.join(
        os.path.split(__file__)[0], 'squinky-corpus/cls_info.p'
    )
INFORMATIVENESS_VECTORIZER_PATH = os.path.join(
        os.path.split(__file__)[0], 'squinky-corpus/vec_info.p'
    )
IMPLICATURE_CLASSIFIER_PATH = os.path.join(
        os.path.split(__file__)[0], 'squinky-corpus/cls_impl.p'
    )
IMPLICATURE_VECTORIZER_PATH = os.path.join(
        os.path.split(__file__)[0], 'squinky-corpus/vec_impl.p'
    )

#os.path.join(os.path.split(__file__)[0], 'politeness-svm.p')
#os.path.join(os.path.split(__file__)[0], 'politeness-svm.p')
