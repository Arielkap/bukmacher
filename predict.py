from typing import List, Dict
import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class Player:
    def __init__(self, name: str, ranking: int, last_season_surface_stats: Dict[str, Dict], 
                 current_season_form: List[str], surface_form: List[str], 
                 days_since_last_match: int, nationality: str = "Unknown", 
                 bp_conversion: float = 0.45, hand: str = "Right", style: str = "All-Court",
                 peak_ranking: int = None, is_returning: bool = False):
        self.name = name
        self.ranking = ranking
        self.peak_ranking = peak_ranking or ranking
        self.is_returning = is_returning
        self.last_season_surface_stats = last_season_surface_stats
        self.current_season_form = current_season_form
        self.surface_form = surface_form
        self.days_since_last_match = days_since_last_match
        self.nationality = nationality
        self.bp_conversion = bp_conversion
        self.hand = hand
        self.style = style # 'Aggressive', 'Defensive', 'All-Court'

    def get_surface_win_rate(self, surface: str) -> float:
        stats = self.last_season_surface_stats.get(surface, {'W': 0, 'L': 0})
        total = stats['W'] + stats['L']
        return stats['W'] / total if total > 0 else 0.5

    def get_form_score(self, form: List[str]) -> float:
        if not form:
            return 0.5
        # Weighted form: more recent matches (end of list) count more
        weights = [i + 1 for i in range(len(form))]
        total_weight = sum(weights)
        score = sum(weights[i] for i, res in enumerate(form) if res == 'W') / total_weight
        return score

class MatchPredictor:
    def __init__(self, surface: str, is_qualifying: bool = False, tournament_country: str = "Unknown", court_speed: str = "Medium"):
        self.surface = surface
        self.is_qualifying = is_qualifying
        self.tournament_country = tournament_country
        self.court_speed = court_speed # 'Slow', 'Medium', 'Fast'

    def calculate_score(self, player: Player, opponent: Player, h2h_wins: int, total_h2h: int) -> float:
        import math
        
        # Hidden Gem Logic: If player is returning, use weighted average of current and peak ranking
        effective_ranking = player.ranking
        if player.is_returning and player.peak_ranking < player.ranking:
            # Weight: 60% Peak Ranking, 40% Current (reflecting quality but some rust)
            effective_ranking = (player.peak_ranking * 0.6) + (player.ranking * 0.4)
            
        ranking_score = 100 * (1 / (1 + math.log10(effective_ranking)))
        ranking_weight = 0.20 
        
        surface_win_rate = player.get_surface_win_rate(self.surface)
        surface_weight = 0.15
        
        # MASSIVE UPDATE: Form is now king when delta is high
        overall_form_score = player.get_form_score(player.current_season_form)
        overall_form_weight = 0.30 
        
        surface_form_score = player.get_form_score(player.surface_form)
        surface_form_weight = 0.15
        
        h2h_score = (h2h_wins / total_h2h) if total_h2h > 0 else 0.5
        h2h_weight = 0.05

        # Fatigue Penalty: -12 pts if played < 3 days ago after a long run (W-W-W-W)
        fatigue_penalty = 0
        if player.days_since_last_match < 3 and len(player.current_season_form) >= 4 and all(r == 'W' for r in player.current_season_form[-4:]):
            fatigue_penalty = -12
            
        # Court Speed Adjustment: Defensive players get +10 pts on Slow courts
        speed_bonus = 0
        if self.court_speed == "Slow" and player.style == "Defensive":
            speed_bonus = 10
        elif self.court_speed == "Fast" and player.style == "Aggressive":
            speed_bonus = 10
        elif self.court_speed == "Slow" and player.style == "Aggressive":
            speed_bonus = -8 # Aggressive players struggle with timing on slow, high-bounce courts

        # Streak Penalty: -15 points if last 3 matches are losses
        streak_penalty = 0
        if len(player.current_season_form) >= 3 and all(r == 'L' for r in player.current_season_form[-3:]):
            streak_penalty = -15
            
        # BP Conversion & Tactical
        bp_score = player.bp_conversion
        bp_weight = 0.05

        home_bonus = 1.05 if player.nationality.lower() in self.tournament_country.lower() else 1.0
        
        # Lefty Bonus: +7% on fast courts (Hard/Grass)
        lefty_multiplier = 1.07 if player.hand.lower() == "left" and self.surface.lower() in ["hard", "grass"] else 1.0

        class_bonus = 15 if player.ranking <= 20 else (10 if player.ranking <= 32 else 0)
        
        total_score = (
            (ranking_score * ranking_weight) +
            (surface_win_rate * 100 * surface_weight) +
            (overall_form_score * 100 * overall_form_weight) +
            (surface_form_score * 100 * surface_form_weight) +
            (h2h_score * 100 * h2h_weight) +
            (bp_score * 100 * bp_weight) +
            (class_bonus * 10) + 
            streak_penalty +
            fatigue_penalty +
            speed_bonus
        ) * home_bonus * lefty_multiplier
        
        return max(5, total_score)

    def predict(self, player1: Player, player2: Player, h2h_stats: Dict[str, int], event_name: str = "Unknown Event"):
        total_h2h = h2h_stats['p1_wins'] + h2h_stats['p2_wins']
        score1 = self.calculate_score(player1, player2, h2h_stats['p1_wins'], total_h2h)
        score2 = self.calculate_score(player2, player1, h2h_stats['p2_wins'], total_h2h)

        print(f"\n" + "="*50)
        print(f"EVENT: {event_name}")
        print(f"MATCH: {player1.name} vs {player2.name} on {self.surface}")
        print("="*50)
        print(f"Ranking: {player1.name} (#{player1.ranking}) vs {player2.name} (#{player2.ranking})")
        print(f"H2H: {h2h_stats['p1_wins']} - {h2h_stats['p2_wins']}")
        
        print(f"\nCalculated Strength Scores:")
        print(f"{player1.name:20}: {score1:.2f}")
        print(f"{player2.name:20}: {score2:.2f}")

        win_prob1 = (score1 / (score1 + score2)) * 100
        win_prob2 = (score2 / (score1 + score2)) * 100

        winner = player1.name if score1 > score2 else player2.name
        confidence = abs(win_prob1 - win_prob2)

        print(f"\nFINAL PREDICTION:")
        print(f"Predicted Winner: {winner}")
        print(f"Confidence Level: {confidence:.2f}%")
        print(f"Probabilities: {player1.name} {win_prob1:.1f}% | {player2.name} {win_prob2:.1f}%")
        print("="*50 + "\n")

class GeminiDataFetcher:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in .env file.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def fetch_match_data(self, p1_name: str, p2_name: str, event_name: str, surface: str) -> Dict:
        prompt = f"""
        Act as a professional tennis analyst. Provide the latest data for a WTA match:
        Event: {event_name}
        Surface: {surface}
        Player 1: {p1_name}
        Player 2: {p2_name}

        Return ONLY a JSON object with this exact structure (no other text):
        {{
            "p1": {{
                "ranking": int,
                "peak_ranking": int,
                "is_returning": boolean (true if returning from injury/pregnancy/long layoff),
                "nationality": "string",
                "hand": "Left" or "Right",
                "style": "Aggressive", "Defensive", or "All-Court",
                "bp_conversion": float (e.g. 0.48),
                "last_season_surface_stats": {{"W": int, "L": int}},
                "current_season_form": ["W", "L", "W", "W", "L"],
                "surface_form": ["W", "L", "W", "W", "L"],
                "days_since_last_match": int
            }},
            "p2": {{
                "ranking": int,
                "peak_ranking": int,
                "is_returning": boolean,
                "nationality": "string",
                "hand": "Left" or "Right",
                "style": "Aggressive", "Defensive", or "All-Court",
                "bp_conversion": float,
                "last_season_surface_stats": {{"W": int, "L": int}},
                "current_season_form": ["W", "L", "W", "W", "L"],
                "surface_form": ["W", "L", "W", "W", "L"],
                "days_since_last_match": int
            }},
            "h2h": {{
                "p1_wins": int,
                "p2_wins": int
            }},
            "tournament": {{
                "country": "string",
                "is_qualifying": boolean,
                "court_speed": "Slow", "Medium", or "Fast"
            }}
        }}
        Use the most recent data available as of February 2026.
        """
        try:
            response = self.model.generate_content(prompt)
            json_str = re.search(r'\{.*\}', response.text, re.DOTALL).group()
            return json.loads(json_str)
        except Exception as e:
            print(f"Error fetching data from Gemini: {e}")
            return None

class MatchParser:
    @staticmethod
    def parse_paste_format(text: str) -> List[Dict]:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines: return []
        
        event_name = lines[0]
        surface = "Hard"
        if len(lines) > 1:
            surface_match = re.search(r'·\s*(\w+)', lines[1])
            surface = surface_match.group(1) if surface_match else "Hard"

        matches = []
        i = 2
        while i < len(lines):
            try:
                # Looking for country code pattern (2 uppercase letters)
                if len(lines[i]) == 2 and lines[i].isupper():
                    p1_name = lines[i+1]
                    p1_rank = lines[i+2]
                    p2_name = lines[i+4]
                    p2_rank = lines[i+5]
                    matches.append({
                        'event': event_name, 'surface': surface,
                        'p1_name': p1_name, 'p1_rank': p1_rank,
                        'p2_name': p2_name, 'p2_rank': p2_rank
                    })
                    i += 8
                else: i += 1
            except: break
        return matches

if __name__ == "__main__":
    print("Welcome to Tennis Prediction AI (Powered by Gemini)")
    mode = input("Choose mode: (1) Names (2) Paste Format (3) Sample [Default 2]: ") or "2"
    fetcher = GeminiDataFetcher()

    if mode == "1":
        p1_n = input("Player 1 Name: ")
        p2_n = input("Player 2 Name: ")
        evt = input("Event: ")
        srf = input("Surface: ").capitalize()
        data = fetcher.fetch_match_data(p1_n, p2_n, evt, srf)
        if data:
            p1 = Player(p1_n, data['p1']['ranking'], {srf: data['p1']['last_season_surface_stats']}, 
                        data['p1']['current_season_form'], data['p1']['surface_form'], 
                        data['p1']['days_since_last_match'], data['p1'].get('nationality'), 
                        data['p1'].get('bp_conversion'), data['p1'].get('hand', 'Right'),
                        data['p1'].get('style', 'All-Court'), data['p1'].get('peak_ranking'),
                        data['p1'].get('is_returning', False))
            p2 = Player(p2_n, data['p2']['ranking'], {srf: data['p2']['last_season_surface_stats']}, 
                        data['p2']['current_season_form'], data['p2']['surface_form'], 
                        data['p2']['days_since_last_match'], data['p2'].get('nationality'), 
                        data['p2'].get('bp_conversion'), data['p2'].get('hand', 'Right'),
                        data['p2'].get('style', 'All-Court'), data['p2'].get('peak_ranking'),
                        data['p2'].get('is_returning', False))
            
            predictor = MatchPredictor(srf, data.get('tournament', {}).get('is_qualifying', False), 
                                      data.get('tournament', {}).get('country', 'Unknown'),
                                      data.get('tournament', {}).get('court_speed', 'Medium'))
            predictor.predict(p1, p2, data['h2h'], evt)

    elif mode == "2":
        print("\nPaste match list (Ctrl+D to finish):")
        lines = []
        try:
            while True: lines.append(input())
        except EOFError: pass
        
        matches = MatchParser.parse_paste_format("\n".join(lines))
        if matches:
            for idx, m in enumerate(matches):
                print(f"{idx+1}. {m['p1_name']} vs {m['p2_name']}")
            choice = int(input("\nSelect match #: ")) - 1
            m = matches[choice]
            print(f"\nFetching AI data for {m['p1_name']} vs {m['p2_name']}...")
            data = fetcher.fetch_match_data(m['p1_name'], m['p2_name'], m['event'], m['surface'])
            if data:
                p1 = Player(m['p1_name'], data['p1']['ranking'], {m['surface']: data['p1']['last_season_surface_stats']}, 
                            data['p1']['current_season_form'], data['p1']['surface_form'], 
                            data['p1']['days_since_last_match'], data['p1'].get('nationality'), 
                            data['p1'].get('bp_conversion'), data['p1'].get('hand', 'Right'),
                            data['p1'].get('style', 'All-Court'), data['p1'].get('peak_ranking'),
                            data['p1'].get('is_returning', False))
                p2 = Player(m['p2_name'], data['p2']['ranking'], {m['surface']: data['p2']['last_season_surface_stats']}, 
                            data['p2']['current_season_form'], data['p2']['surface_form'], 
                            data['p2']['days_since_last_match'], data['p2'].get('nationality'), 
                            data['p2'].get('bp_conversion'), data['p2'].get('hand', 'Right'),
                            data['p2'].get('style', 'All-Court'), data['p2'].get('peak_ranking'),
                            data['p2'].get('is_returning', False))
                
                predictor = MatchPredictor(m['surface'], data.get('tournament', {}).get('is_qualifying', False), 
                                          data.get('tournament', {}).get('country', 'Unknown'),
                                          data.get('tournament', {}).get('court_speed', 'Medium'))
                predictor.predict(p1, p2, data['h2h'], m['event'])
    else:
        # Simple sample
        p1 = Player("Iga Swiatek", 1, {'Clay': {'W': 20, 'L': 2}}, ['W']*5, ['W']*5, 3)
        p2 = Player("Aryna Sabalenka", 2, {'Clay': {'W': 15, 'L': 5}}, ['W', 'W', 'L', 'W', 'W'], ['W', 'L', 'W', 'W', 'W'], 2)
        MatchPredictor('Clay').predict(p1, p2, {'p1_wins': 7, 'p2_wins': 3}, "Sample Final")