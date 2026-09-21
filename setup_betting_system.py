import json
import os
from datetime import datetime

CONFIG_FILE = "/data/.openclaw/workspace/wta_betting_config.json"

betting_system = {
    "sport": "Tennis (WTA)",
    "bookmaker": "Betclic",
    "schedule_mode": "Daily automated fetch",
    "timing_rules": {
        "evening_matches": "Send tips 2 hours before start",
        "night_matches": "Send tips in the evening beforehand so user can place bets"
    },
    "feedback_loop": "User reports win/loss to train/adjust agent expectations",
    "updated_at": datetime.now().isoformat()
}

with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(betting_system, f, indent=4, ensure_ascii=False)

print("Zapisano zaawansowaną konfigurację systemu bukmacherskiego WTA.")
