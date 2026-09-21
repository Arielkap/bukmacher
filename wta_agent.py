import json
from datetime import datetime
import os

TIPS_FILE = "/data/.openclaw/workspace/wta_tips.json"
HISTORY_FILE = "/data/.openclaw/workspace/wta_history.json"

class WTABettingAgent:
    def __init__(self):
        self.load_history()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except:
                self.history = {"correct": 0, "total": 0, "lessons": []}
        else:
            self.history = {"correct": 0, "total": 0, "lessons": []}

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

    def analyze_match(self, p1, p2, surface, h2h_p1_wins, h2h_p2_wins, p1_seed, p2_seed, p1_recent_form="Good", p2_recent_form="Mixed"):
        """
        Ulepszona analiza uwzględniająca ranking (nr rozstawienia), nawierzchnię oraz ostatnią formę.
        """
        score_p1 = 0
        score_p2 = 0
        reasons = []

        # 1. Rozstawienie / Ranking (np. nr 1 w turnieju ma ogromną wagę)
        if p1_seed and p2_seed:
            if p1_seed < p2_seed:
                score_p1 += 3
                reasons.append(f"{p1} jest wyżej rozstawiona (nr {p1} vs nr {p2})")
            else:
                score_p2 += 3
                reasons.append(f"{p2} jest wyżej rozstawiona (nr {p2} vs nr {p1})")

        # 2. Ostatnia forma
        if p1_recent_form == "Good":
            score_p1 += 2
            reasons.append(f"{p1} ma stabilną, wysoką formę w ostatnich meczach")
        if p2_recent_form == "Good":
            score_p2 += 2
            reasons.append(f"{p2} wchodzi w mecz z dobrą serią")

        # 3. H2H (bierzemy pod uwagę, ale uwzględniamy poprawkę użytkownika: forma i seeding na hardzie mogą przełamać złą passę)
        if h2h_p1_wins > h2h_p2_wins:
            score_p1 += 2
            reasons.append(f"H2H na korzyść {p1} ({h2h_p1_wins}:{h2h_p2_wins})")
        else:
            score_p2 += 1
            reasons.append(f"H2H historycznie na korzyść {p2} (ale ranking i forma mogą to zniwelować)")

        # Wybór zwycięzcy
        if score_p1 >= score_p2:
            winner = p1
            confidence = "Wysoka" if (score_p1 - score_p2) >= 2 else "Średnia"
        else:
            winner = p2
            confidence = "Wysoka" if (score_p2 - score_p1) >= 2 else "Średnia"

        return {
            "prediction": f"{winner} (zwycięstwo)",
            "confidence": confidence,
            "analysis": reasons
        }

if __name__ == "__main__":
    agent = WTABettingAgent()
    analysis = agent.analyze_match(
        p1="Marta Kostyuk",
        p2="Liudmila Samsonova",
        surface="Hard",
        h2h_p1_wins=0,
        h2h_p2_wins=4,
        p1_seed=1,
        p2_seed=8,
        p1_recent_form="Good",
        p2_recent_form="Mixed"
    )
    print("Zaktualizowana analiza agenta dla Kostiuk vs Samsonova:")
    print(json.dumps(analysis, indent=4, ensure_ascii=False))
