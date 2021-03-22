from api.datasets.cleaning.cleaners import (
    split_chained_calls,
    separate_camel_case,
    remove_non_alphanumeric_characters,
    remove_stop_words,
    to_lower,
    stem_doc,
    clean_doc,
)
from tests.res.smart_test import SmartTest


class TestCleanDoc(SmartTest):
    def test_separate_chained_calls(self):
        doc = "helloWorld.thisMyThing"
        cleaned_doc = split_chained_calls(doc)
        self.assertEqual("helloWorld thisMyThing", cleaned_doc)

    def test_separate_camel_case_ec_example(self):
        doc = "GUIAnagraficaLaboratorioHandler"
        cleaned_doc = separate_camel_case(doc)
        self.assertEqual("GUI Anagrafica Laboratorio Handler", cleaned_doc)

    def test_remove_non_alphanumeric(self):
        doc = "123helloWorld!.thisMyThing"
        cleaned_doc = remove_non_alphanumeric_characters(doc)
        self.assertEqual("helloWorldthisMyThing", cleaned_doc)

    def test_remove_stop_words(self):
        doc = "the cow jumped over the moon"
        cleaned_doc = remove_stop_words(doc)
        self.assertEqual("cow jumped moon", cleaned_doc)

    def test_to_lower(self):
        doc = "the COW jumPeD over MoOn"
        cleaned_doc = to_lower(doc)
        self.assertEqual("the cow jumped over moon", cleaned_doc)

    def test_stem_doc(self):
        doc = "the cow jumped over the moon"
        cleaned_doc = stem_doc(doc)
        self.assertEqual("the cow jump over the moon", cleaned_doc)

    def test_clean_doc_basic(self):
        doc = "123helloWorld!.thisMyThing"
        actual = clean_doc(doc, -1)
        self.assertEqual("hello world thing", actual)
