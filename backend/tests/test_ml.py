import unittest
import datetime
from backend.app.services.ml_service import (
    extract_features,
    predict_congestion,
    get_model_metadata,
    CLASS_NAMES
)

class TestMachineLearningService(unittest.TestCase):

    def test_feature_extraction(self):
        target_time = datetime.datetime(2026, 10, 28, 9, 30, 0)
        features = extract_features(target_time, temp_c=25.0, precip_mm=2.5)

        self.assertEqual(features.shape, (1, 8))
        self.assertAlmostEqual(features["sin_hour"].iloc[0], 0.6087614, places=4)
        self.assertEqual(features["is_weekend"].iloc[0], 0)
        self.assertEqual(features["is_rush_hour"].iloc[0], 1)
        self.assertEqual(features["temperature_c"].iloc[0], 25.0)
        self.assertEqual(features["precipitation_mm"].iloc[0], 2.5)
        self.assertEqual(features["rain_intensity"].iloc[0], 1)

        weekend_time = datetime.datetime(2026, 10, 25, 9, 30, 0)
        weekend_features = extract_features(weekend_time, temp_c=25.0, precip_mm=0.0)
        self.assertEqual(weekend_features["is_weekend"].iloc[0], 1)
        self.assertEqual(weekend_features["is_rush_hour"].iloc[0], 0)

    def test_prediction_output_structure(self):
        result = predict_congestion(
            location_name="Outer Ring Road",
            latitude=12.9716,
            longitude=77.5946,
            horizon_minutes=30,
            temperature_c=26.0,
            precipitation_mm=0.0
        )

        self.assertIn("predicted_category", result)
        self.assertIn(result["predicted_category"], CLASS_NAMES)
        self.assertIn("confidence_score", result)
        self.assertTrue(0.0 <= result["confidence_score"] <= 1.0)

        self.assertIn("class_probabilities", result)
        for cat in CLASS_NAMES:
            self.assertIn(cat, result["class_probabilities"])
            self.assertTrue(0.0 <= result["class_probabilities"][cat] <= 1.0)

        self.assertIn("feature_attributions", result)
        self.assertTrue(len(result["feature_attributions"]) > 0)

        self.assertIn("horizon_trend", result)
        self.assertEqual(len(result["horizon_trend"]), 5)

        self.assertIn("departure_recommendation", result)
        self.assertIn("suggested_departure", result["departure_recommendation"])

    def test_model_metadata_availability(self):
        meta = get_model_metadata()
        self.assertIn("version", meta)
        self.assertIn("algorithm", meta)
        self.assertIn("accuracy", meta)

if __name__ == "__main__":
    unittest.main()
