from predict import Player, MatchPredictor, GeminiDataFetcher
import os
import json

def run_batch():
    fetcher = GeminiDataFetcher()
    matches = [
        ("Anastasia Zakharova", "Linda Fruhvirtova"),
        ("Lulu Sun", "Diane Parry"),
        ("Kamilla Rakhimova", "Maria Timofeeva"),
        ("Darja Semenistaja", "Kayla Day"),
        ("Elvina Kalieva", "Talia Gibson"),
        ("Marina Stakusic", "Mananchaya Sawangkaew"),
        ("Himeno Sakatsume", "Nikola Bartunkova"),
        ("Dalma Galfi", "Lanlana Tararudee"),
        ("Storm Sanders", "Leolia Jeanjean"),
        ("Priscilla Hon", "Darja Vidmanova"),
        ("Katie Boulter", "Victoria Jimenez Kasintseva"),
        ("Akasha Urhobo", "Taylor Townsend")
    ]
    
    event = "WTA Indian Wells Q2"
    surface = "Hard"
    court_speed = "Slow"
    
    results = []
    
    for p1_name, p2_name in matches:
        print(f"Fetching data for {p1_name} vs {p2_name}...")
        data = fetcher.fetch_match_data(p1_name, p2_name, event, surface)
        if data:
            p1 = Player(p1_name, data['p1']['ranking'], {surface: data['p1']['last_season_surface_stats']}, 
                        data['p1']['current_season_form'], data['p1']['surface_form'], 
                        data['p1']['days_since_last_match'], data['p1'].get('nationality'), 
                        data['p1'].get('bp_conversion'), data['p1'].get('hand', 'Right'),
                        data['p1'].get('style', 'All-Court'), data['p1'].get('peak_ranking'),
                        data['p1'].get('is_returning', False))
            p2 = Player(p2_name, data['p2']['ranking'], {surface: data['p2']['last_season_surface_stats']}, 
                        data['p2']['current_season_form'], data['p2']['surface_form'], 
                        data['p2']['days_since_last_match'], data['p2'].get('nationality'), 
                        data['p2'].get('bp_conversion'), data['p2'].get('hand', 'Right'),
                        data['p2'].get('style', 'All-Court'), data['p2'].get('peak_ranking'),
                        data['p2'].get('is_returning', False))
            
            predictor = MatchPredictor(surface, True, data.get('tournament', {}).get('country', 'USA'), court_speed)
            
            # Extract scores and calculate win probs
            total_h2h = data['h2h']['p1_wins'] + data['h2h']['p2_wins']
            score1 = predictor.calculate_score(p1, p2, data['h2h']['p1_wins'], total_h2h)
            score2 = predictor.calculate_score(p2, p1, data['h2h']['p2_wins'], total_h2h)
            
            win_prob1 = (score1 / (score1 + score2)) * 100
            win_prob2 = (score2 / (score1 + score2)) * 100
            
            winner = p1_name if score1 > score2 else p2_name
            conf = abs(win_prob1 - win_prob2)
            
            results.append({
                "matchup": f"{p1_name} vs {p2_name}",
                "winner": winner,
                "confidence": f"{conf:.1f}%",
                "p1_prob": f"{win_prob1:.1f}%",
                "p2_prob": f"{win_prob2:.1f}%",
                "insight": f"{'Slow court bonus' if (p1.style == 'Defensive' if score1 > score2 else p2.style == 'Defensive') else 'Ranking class'}"
            })
            
    with open("q2_predictions.json", "w") as f:
        json.dump(results, f, indent=4)
    print("Predictions saved to q2_predictions.json")

if __name__ == "__main__":
    run_batch()
