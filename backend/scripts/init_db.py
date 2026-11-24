"""
TrafficIntel AI - Database Initialization & Seed Script
Creates all relational database tables and seeds demo account, sample community reports,
saved places, and model version records.
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.database import engine, SessionLocal, Base
from backend.app.models.user import User
from backend.app.models.location import SavedLocation
from backend.app.models.report import CommunityReport
from backend.app.models.model_version import ModelVersion
from backend.app.utils.security import hash_password

def init_and_seed_db():
    print("=================================================================")
    print(" TrafficIntel AI - Database Initialization")
    print("=================================================================")

    print("\n[1/4] Creating database tables...", flush=True)
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables verified/created successfully.")

    db = SessionLocal()
    try:
        print("\n[2/4] Seeding demo user account...", flush=True)
        demo_user = db.query(User).filter(User.email == "demo@trafficintel.ai").first()
        if not demo_user:
            demo_user = User(
                name="Demo User",
                email="demo@trafficintel.ai",
                hashed_password=hash_password("Traffic@123"),
                role="admin"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print("[OK] Created Demo User: demo@trafficintel.ai / Password: Traffic@123")
        else:
            print("[OK] Demo user already present.")

        print("\n[3/4] Seeding saved locations...", flush=True)
        existing_locs = db.query(SavedLocation).filter(SavedLocation.user_id == demo_user.id).count()
        if existing_locs == 0:
            sample_locs = [
                SavedLocation(
                    user_id=demo_user.id,
                    label="Home",
                    address="Indiranagar 100ft Road, Bangalore",
                    category="Home",
                    latitude=12.9784,
                    longitude=77.6408
                ),
                SavedLocation(
                    user_id=demo_user.id,
                    label="Tech Park Office",
                    address="Manyata Tech Park, Nagavara",
                    category="Work",
                    latitude=13.0475,
                    longitude=77.6212
                ),
                SavedLocation(
                    user_id=demo_user.id,
                    label="University Campus",
                    address="Central University Transit Hub",
                    category="College",
                    latitude=12.9345,
                    longitude=77.6060
                )
            ]
            db.add_all(sample_locs)
            db.commit()
            print(f"[OK] Seeded {len(sample_locs)} default saved locations.")
        else:
            print("[OK] Saved locations already populated.")

        print("\n[4/4] Seeding sample community incident reports...", flush=True)
        existing_reports = db.query(CommunityReport).count()
        if existing_reports == 0:
            sample_reports = [
                CommunityReport(
                    user_id=demo_user.id,
                    report_type="Accident",
                    road_name="Outer Ring Road near Marathahalli Bridge",
                    description="Two-vehicle fender bender in center lane. Traffic backed up ~1.5 km.",
                    latitude=12.9562,
                    longitude=77.7019,
                    severity="Medium",
                    status="verified",
                    votes=5
                ),
                CommunityReport(
                    user_id=demo_user.id,
                    report_type="Road Closure",
                    road_name="MG Road Flyover Down-Ramp",
                    description="Scheduled maintenance barricades placed. Diversion via side lane.",
                    latitude=12.9734,
                    longitude=77.6083,
                    severity="Critical",
                    status="active",
                    votes=8
                ),
                CommunityReport(
                    user_id=demo_user.id,
                    report_type="Waterlogging",
                    road_name="Silk Board Junction Underpass",
                    description="Drain overflow after evening rain. Lane 1 flooded.",
                    latitude=12.9176,
                    longitude=77.6238,
                    severity="Medium",
                    status="active",
                    votes=3
                ),
                CommunityReport(
                    user_id=demo_user.id,
                    report_type="Construction",
                    road_name="Bannerghatta Metro Construction Zone",
                    description="Narrow single lane passage due to piling work. Expect 10-15m slowdown.",
                    latitude=12.8950,
                    longitude=77.5990,
                    severity="Low",
                    status="active",
                    votes=4
                )
            ]
            db.add_all(sample_reports)
            db.commit()
            print(f"[OK] Seeded {len(sample_reports)} active community incident reports.")
        else:
            print("[OK] Community reports already present.")

        metadata_file = BASE_DIR / "backend" / "app" / "ml" / "artifacts" / "model_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                meta = json.load(f)

            mv = db.query(ModelVersion).filter(ModelVersion.version_tag == meta.get("version", "1.2.0")).first()
            if not mv:
                mv = ModelVersion(
                    version_tag=meta.get("version", "1.2.0"),
                    algorithm=meta.get("algorithm", "RandomForestClassifier"),
                    accuracy=meta.get("accuracy", 0.72),
                    f1_macro=meta.get("f1_macro", 0.72),
                    precision_macro=0.77,
                    recall_macro=0.71,
                    active_status=True,
                    hyperparameters_json=json.dumps({"n_estimators": 50, "max_depth": 10})
                )
                db.add(mv)
                db.commit()
                print("[OK] Recorded active ModelVersion 1.2.0 in database.")

        print("\n=================================================================")
        print(" Database Initialization Completed Successfully!")
        print("=================================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    init_and_seed_db()
