from api.technique.parser.definition_parser import parse_technique_definition
from tests.res.smart_test import SmartTest


class TestTechniqueNameParser(SmartTest):
    """
    parse_technique_definition
    """

    def test_parse_technique_definition_with_nested(self):
        result = parse_technique_definition("(SUM (SUM B C) A)")
        self.assertEqual(3, len(result))
        self.assertEqual("SUM", result[0])
        self.assertEqual(["SUM", "B", "C"], result[1])
        self.assertEqual("A", result[2])

    def test_parse_technique_definition_with_combined(self):
        t_one = "0-2_VSM"
        t_two = "0-1-2_VSM_NONETRACED_GLOBAL_SUM"
        result = parse_technique_definition("(SUM %s %s)" % (t_one, t_two))
        self.assertEqual(3, len(result))
        self.assertEqual("SUM", result[0])
        self.assertEqual(t_one, result[1])
        self.assertEqual(t_two, result[2])

    def test_parse_technique_definition_with_single(self):
        t_name = "0-2_VSM"
        result = parse_technique_definition(t_name)
        self.assertEqual(t_name, result)

    def test_parse_technique_definition_with_extra_paren(self):
        t_name = ") (SUM A B)"
        self.assertRaises(Exception, lambda: parse_technique_definition(t_name))

    def test_parse_technique_definition_without_paren(self):
        t_name = "(SUM A B"
        self.assertRaises(Exception, lambda: parse_technique_definition(t_name))

    def test_parse_technique_definition_with_empty(self):
        t_name = ""
        self.assertRaises(Exception, lambda: parse_technique_definition(t_name))
