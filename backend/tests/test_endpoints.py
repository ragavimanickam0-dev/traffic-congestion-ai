import unittest
from unittest.mock import patch, MagicMock
from backend.app.database import SessionLocal
from backend.app.schemas.auth import UserLoginRequest
from backend.app.schemas.prediction import PredictionRequest
from backend.app.schemas.route import RouteCompareRequest
from backend.app.schemas.report import CommunityReportCreate
from backend.app.routers.auth import login
from backend.app.routers.locations import search, reverse
from backend.app.routers.weather import get_weather
from backend.app.routers.traffic import get_traffic
from backend.app.routers.predictions import make_prediction
from backend.app.routers.routes import compare_available_routes
from backend.app.routers.reports import get_reports, submit_report
from backend.app.routers.analytics import get_traffic_analytics, get_evaluation_metrics
from fastapi import HTTPException

class TestAPIEndpoints(unittest.TestCase):

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_auth_login_demo_success(self):
        req = UserLoginRequest(email="demo@trafficintel.ai", password="Traffic@123")
        res = login(req, db=self.db)
        self.assertIn("access_token", res)
        self.assertEqual(res["user"].email, "demo@trafficintel.ai")

    def test_auth_login_invalid_password(self):
        req = UserLoginRequest(email="demo@trafficintel.ai", password="WrongPassword!99")
        with self.assertRaises(HTTPException) as ctx:
            login(req, db=self.db)
        self.assertEqual(ctx.exception.status_code, 401)

    @patch("backend.app.services.geocoding_service.requests.get")
    def test_locations_search(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            {"display_name": "Downtown Transit Hub", "lat": "12.9716", "lon": "77.5946", "type": "station"}
        ]
        mock_get.return_value = mock_resp

        results = search(q="Downtown", limit=3, db=self.db, current_user=None)
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["display_name"], "Downtown Transit Hub")

    @patch("backend.app.services.weather_service.requests.get")
    def test_weather_endpoint(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "current": {
                "temperature_2m": 24.5,
                "relative_humidity_2m": 60,
                "precipitation": 0.0,
                "weather_code": 1,
                "wind_speed_10m": 12.0
            }
        }
        mock_get.return_value = mock_resp

        data = get_weather(lat=12.9716, lon=77.5946)
        self.assertIn("temperature_c", data)
        self.assertEqual(data["temperature_c"], 24.5)

    def test_traffic_telemetry(self):
        data = get_traffic(lat=12.9716, lon=77.5946, zoom=14)
        self.assertIn(data["congestion_level"], ["LOW", "MODERATE", "HIGH"])
        self.assertIn("segments", data)
        self.assertTrue(len(data["segments"]) > 0)

    def test_prediction_endpoint(self):
        req = PredictionRequest(
            location_name="Silk Board Junction",
            latitude=12.9176,
            longitude=77.6238,
            horizon_minutes=30,
            temperature_c=25.0,
            precipitation_mm=0.0
        )
        res = make_prediction(req, db=self.db, current_user=None)
        self.assertEqual(res["location_name"], "Silk Board Junction")
        self.assertIn(res["predicted_category"], ["LOW", "MODERATE", "HIGH"])
        self.assertIn("feature_attributions", res)

    def test_prediction_invalid_horizon(self):
        req = PredictionRequest(
            location_name="Silk Board Junction",
            latitude=12.9176,
            longitude=77.6238,
            horizon_minutes=45
        )
        with self.assertRaises(HTTPException) as ctx:
            make_prediction(req, db=self.db, current_user=None)
        self.assertEqual(ctx.exception.status_code, 400)

    @patch("backend.app.services.routing_service.requests.get")
    def test_route_comparison(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "routes": [
                {
                    "distance": 21000.0,
                    "duration": 1800.0,
                    "geometry": {"coordinates": [[77.57, 12.97], [77.66, 12.84]]}
                }
            ]
        }
        mock_get.return_value = mock_resp

        req = RouteCompareRequest(
            origin_lat=12.9772,
            origin_lon=77.5708,
            dest_lat=12.8452,
            dest_lon=77.6602
        )
        data = compare_available_routes(req)
        self.assertIn("primary_route", data)
        self.assertIn("departure_guidance", data)

    def test_reports_get_and_post(self):
        reports = get_reports(db=self.db)
        self.assertIsInstance(reports, list)

        req = CommunityReportCreate(
            report_type="Accident",
            road_name="Airport Expressway Tollway",
            description="Minor fender bender on curb lane.",
            latitude=13.1986,
            longitude=77.7066,
            severity="Low"
        )
        created = submit_report(req, db=self.db, current_user=None)
        self.assertEqual(created.road_name, "Airport Expressway Tollway")

    def test_analytics_endpoints(self):
        res1 = get_traffic_analytics(location="All")
        self.assertIn("diurnal_speeds", res1)

        res2 = get_evaluation_metrics()
        self.assertIn("algorithm", res2)

if __name__ == "__main__":
    unittest.main()
