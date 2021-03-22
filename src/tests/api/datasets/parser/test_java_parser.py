from api.datasets.parsing.java_class_parser import (
    extract_java_identifiers,
    create_class_doc,
    extract_class_comments,
)
from tests.res.sample_data import get_test_java_class, get_entity_java_class
from tests.res.smart_test import SmartTest


class TestJavaParser(SmartTest):
    def test_parse_class_comments(self):
        class_text = get_test_java_class()
        comments_text = extract_class_comments(class_text)
        self.assertIn("Some sample class documentation", comments_text)
        self.assertIn("ClassTestAuthor", comments_text)
        self.assertIn("Some sample method documentation", comments_text)
        self.assertIn("MethodTestAuthor", comments_text)
        self.assertIn("inlineTestComment", comments_text)

    def test_sample_class(self):
        class_text = get_test_java_class()
        result = extract_java_identifiers(class_text)
        self.assertIn("Test", result, "missing constructor")
        self.assertIn("testMethod", result, "missing method header")

        self.assertIn("Tests SampleData", result, "missing package name")
        self.assertIn(
            "someConstructorParameter", result, "missing constructor parameter"
        )
        self.assertIn("someMethodParameter", result, "missing method parameter")

        result_cleaned = create_class_doc(class_text, -3)
        self.assertIn("Test", result_cleaned, "missing constructor")
        self.assertIn("Test", result_cleaned, "missing constructor")
        self.assertIn("test Method", result_cleaned, "missing method header")
        self.assertIn("Tests Sample Data", result_cleaned, "missing package name")
        self.assertIn(
            "some Constructor Parameter",
            result_cleaned,
            "missing constructor parameter",
        )
        self.assertIn(
            "some Method Parameter", result_cleaned, "missing method parameter"
        )

    def test_entity_class(self):
        class_text = get_entity_java_class()
        result = extract_java_identifiers(class_text)

        self.assertIn("modelPackage", result, "missing package identifier")
        self.assertIn("getId", result, "missing class method")
        self.assertIn("id version name", result, "missing class attributes")
        self.assertIn("Serializable", result, "missing class extensions")
