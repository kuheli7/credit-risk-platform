import unittest

from fastapi.testclient import TestClient

from backend.main import app
from src.utils.helpers import get_risk_band


class APISmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "online")

    def test_core_read_routes(self):
        for path in (
            "/api/overview",
            "/api/eda/insights",
            "/api/eda/categories",
            "/api/eda/data-quality",
            "/api/eda/portfolio",
            "/api/risk/presets",
            "/api/rules",
            "/api/chat/samples",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_risk_prediction_returns_decision_fields(self):
        payload = {
            "AMT_INCOME_TOTAL": 320000,
            "AMT_CREDIT": 600000,
            "AMT_ANNUITY": 24000,
            "AMT_GOODS_PRICE": 600000,
            "NAME_CONTRACT_TYPE": "Cash loans",
            "CODE_GENDER": "M",
            "NAME_INCOME_TYPE": "Commercial associate",
            "NAME_EDUCATION_TYPE": "Higher education",
            "OCCUPATION_TYPE": "Managers",
            "AGE": 38,
            "YEARS_EMPLOYED": 9.5,
            "EXT_SOURCE_2": 0.72,
            "EXT_SOURCE_3": 0.68,
            "BUREAU_ACTIVE_LOANS": 1,
            "PREV_APP_REFUSED_RATE": 0,
        }
        response = self.client.post("/api/risk/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn(body["risk_band"], {"Low", "Medium", "High"})
        self.assertIn(body["decision"], {"APPROVED", "CONDITIONAL REVIEW", "DECLINED"})
        self.assertIn("risk_increasing_factors", body)
        self.assertIn("risk_reducing_factors", body)
        self.assertIn("ai_explanation", body)

    def test_risk_band_boundaries(self):
        self.assertEqual(get_risk_band(0.19), "Low")
        self.assertEqual(get_risk_band(0.20), "Medium")
        self.assertEqual(get_risk_band(0.50), "Medium")
        self.assertEqual(get_risk_band(0.51), "High")


if __name__ == "__main__":
    unittest.main()
