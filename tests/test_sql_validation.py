import unittest

from src.talk_to_data.nl_to_sql import NLToSQLGenerator


class SQLValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = NLToSQLGenerator(api_key="")

    def test_adds_default_limit_to_valid_query(self):
        result = self.generator._sanitize_sql("SELECT COUNT(*) FROM applications")
        self.assertTrue(result.endswith("LIMIT 100;"))

    def test_rejects_destructive_query(self):
        with self.assertRaisesRegex(ValueError, "Destructive SQL keyword"):
            self.generator._sanitize_sql("DROP TABLE applications")

    def test_rejects_multiple_statements(self):
        with self.assertRaisesRegex(ValueError, "Multiple statements"):
            self.generator._sanitize_sql("SELECT 1; SELECT 2")

    def test_rejects_limit_above_maximum(self):
        with self.assertRaisesRegex(ValueError, "cannot exceed 500"):
            self.generator._sanitize_sql("SELECT * FROM applications LIMIT 501")

    def test_rejects_unknown_schema_column(self):
        with self.assertRaisesRegex(ValueError, "Invalid SQL schema or syntax"):
            self.generator._sanitize_sql("SELECT missing_column FROM applications")


if __name__ == "__main__":
    unittest.main()
