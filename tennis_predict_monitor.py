#!/usr/bin/env python3
"""
Tennis AI Predictor & Value Bet Engine (0 LLM Tokens, Pure Mathematical Model)
Inherits OpenClaw's weighted algorithmic model:
- Surface specific win-rate & court speed
- Weighted 5-match momentum curve
- H2H psychological edge & Fatigue penalties
- Value Bet calculation: (AI Probability * Bookmaker Odds) - 1 > 0
"""

import json
import os
import sys
import math
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "tennis_predictions.json")

class TennisEngine:
    def __init__(self):
        pass

    def calculate_match(self, match):
        p1 = match["p1"]
        p2 = match["p2"]
        surface = match.get("surface", "Hard")
        court_speed = match.get("court_speed", "Medium")
        odds1 = match.get("odds_p1", 1.85)
        odds2 = match.get("odds_p2", 1.95)

        # 1. Ranking Score
        def rank_score(r):
            return 100 * (1 / (1 + math.log10(max(1, r))))
        
        r1 = rank_score(p1["rank"]) * 0.20
        r2 = rank_score(p2["rank"]) * 0.20

        # 2. Surface Win Rate
        s1 = (p1.get("surface_win_rate", 0.60) * 100) * 0.20
        s2 = (p2.get("surface_win_rate", 0.55) * 100) * 0.20

        # 3. Form (Weighted last 5 matches)
        def form_score(form):
            weights = [1, 2, 3, 4, 5]
            score = sum(w for w, res in zip(weights, form[-5:]) if res == 'W')
            return (score / sum(weights[:len(form[-5:])])) * 100
        
        f1 = form_score(p1.get("form", ['W','W','W','L','W'])) * 0.30
        f2 = form_score(p2.get("form", ['L','W','L','W','L'])) * 0.30

        # 4. H2H
        h2h_p1 = match.get("h2h", {}).get("p1", 0)
        h2h_p2 = match.get("h2h", {}).get("p2", 0)
        total_h2h = h2h_p1 + h2h_p2
        h1 = ((h2h_p1 / total_h2h) * 100 if total_h2h > 0 else 50) * 0.15
        h2 = ((h2h_p2 / total_h2h) * 100 if total_h2h > 0 else 50) * 0.15

        # 5. Fatigue & Speed Adjustments
        adj1 = 0
        adj2 = 0
        if p1.get("days_rest", 3) < 2:
            adj1 -= 8
        if p2.get("days_rest", 3) < 2:
            adj2 -= 8
        if court_speed == "Fast" and p1.get("hand") == "Left":
            adj1 += 6
        if court_speed == "Fast" and p2.get("hand") == "Left":
            adj2 += 6

        total1 = max(5, r1 + s1 + f1 + h1 + adj1)
        total2 = max(5, r2 + s2 + f2 + h2 + adj2)

        prob1 = round((total1 / (total1 + total2)) * 100, 1)
        prob2 = round((total2 / (total1 + total2)) * 100, 1)

        # Value Bet detection
        implied_p1 = (1 / odds1) * 100
        implied_p2 = (1 / odds2) * 100

        ev1 = round(((prob1 / 100.0) * odds1) - 1.0, 3)
        ev2 = round(((prob2 / 100.0) * odds2) - 1.0, 3)

        value_bet = None
        if ev1 > 0.07 and prob1 > implied_p1 + 5:
            value_bet = {
                "player": p1["name"],
                "odds": odds1,
                "ai_prob": prob1,
                "implied_prob": round(implied_p1, 1),
                "expected_value": f"+{round(ev1 * 100, 1)}%",
                "edge": f"+{round(prob1 - implied_p1, 1)}%"
            }
        elif ev2 > 0.07 and prob2 > implied_p2 + 5:
            value_bet = {
                "player": p2["name"],
                "odds": odds2,
                "ai_prob": prob2,
                "implied_prob": round(implied_p2, 1),
                "expected_value": f"+{round(ev2 * 100, 1)}%",
                "edge": f"+{round(prob2 - implied_p2, 1)}%"
            }

        predicted_winner = p1["name"] if prob1 > prob2 else p2["name"]
        confidence = "WYSOKA" if abs(prob1 - prob2) >= 20 else ("ŚREDNIA" if abs(prob1 - prob2) >= 10 else "NISKA")

        return {
            "tournament": match.get("tournament", "WTA 1000 / ATP"),
            "surface": surface,
            "court_speed": court_speed,
            "match_time": match.get("time", "Dziś, 14:00"),
            "p1": {"name": p1["name"], "rank": p1["rank"], "prob": prob1, "odds": odds1},
            "p2": {"name": p2["name"], "rank": p2["rank"], "prob": prob2, "odds": odds2},
            "predicted_winner": predicted_winner,
            "confidence": confidence,
            "value_bet": value_bet
        }

def run():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🎾 Uruchamiam Tennis AI Predictor...")
    engine = TennisEngine()

    # Active September Tournaments / Featured Matches (Asian Swing: China Open & Tokyo)
    matches_to_analyze = [
        {
            "tournament": "China Open (Pekin, WTA 1000)",
            "surface": "Hard",
            "court_speed": "Medium-Fast",
            "time": "Dziś, 12:30 CEST",
            "p1": {"name": "Iga Świątek", "rank": 1, "surface_win_rate": 0.84, "form": ['W','W','W','W','W'], "hand": "Right", "days_rest": 4},
            "p2": {"name": "Marta Kostyuk", "rank": 18, "surface_win_rate": 0.62, "form": ['W','L','W','W','L'], "hand": "Right", "days_rest": 2},
            "h2h": {"p1": 3, "p2": 0},
            "odds_p1": 1.25,
            "odds_p2": 4.10
        },
        {
            "tournament": "China Open (Pekin, WTA 1000)",
            "surface": "Hard",
            "court_speed": "Medium-Fast",
            "time": "Dziś, 14:15 CEST",
            "p1": {"name": "Elena Rybakina", "rank": 4, "surface_win_rate": 0.76, "form": ['W','W','W','L','W'], "hand": "Right", "days_rest": 3},
            "p2": {"name": "Liudmila Samsonova", "rank": 15, "surface_win_rate": 0.65, "form": ['W','W','L','W','L'], "hand": "Right", "days_rest": 1},
            "h2h": {"p1": 1, "p2": 3},
            "odds_p1": 1.55,
            "odds_p2": 2.45
        },
        {
            "tournament": "Japan Open (Tokyo, ATP 500)",
            "surface": "Hard",
            "court_speed": "Fast",
            "time": "Jutro, 06:00 CEST",
            "p1": {"name": "Jannik Sinner", "rank": 1, "surface_win_rate": 0.88, "form": ['W','W','W','W','W'], "hand": "Right", "days_rest": 5},
            "p2": {"name": "Ben Shelton", "rank": 16, "surface_win_rate": 0.69, "form": ['W','W','L','W','W'], "hand": "Left", "days_rest": 3},
            "h2h": {"p1": 3, "p2": 1},
            "odds_p1": 1.30,
            "odds_p2": 3.65
        },
        {
            "tournament": "Japan Open (Tokyo, ATP 500)",
            "surface": "Hard",
            "court_speed": "Fast",
            "time": "Jutro, 08:30 CEST",
            "p1": {"name": "Carlos Alcaraz", "rank": 2, "surface_win_rate": 0.82, "form": ['W','W','W','W','L'], "hand": "Right", "days_rest": 4},
            "p2": {"name": "Tallon Griekspoor", "rank": 39, "surface_win_rate": 0.58, "form": ['L','W','L','W','L'], "hand": "Right", "days_rest": 2},
            "h2h": {"p1": 4, "p2": 0},
            "odds_p1": 1.14,
            "odds_p2": 5.80
        }
    ]

    results = []
    for m in matches_to_analyze:
        pred = engine.calculate_match(m)
        results.append(pred)

    payload = {
        "updated_at": datetime.now().isoformat(),
        "total_analyzed": len(results),
        "value_bets_count": len([r for r in results if r["value_bet"]]),
        "predictions": results
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"✅ Zakończono analizę: {len(results)} meczów, znaleziono {payload['value_bets_count']} Value Betów.")

if __name__ == "__main__":
    run()
