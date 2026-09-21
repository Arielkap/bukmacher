# Tennis Prediction AI - Project Context

## Project Overview
This project is an AI-driven tennis match predictor specifically designed for WTA tournaments. It combines traditional statistical analysis (rankings, H2H, surface win rates) with real-time performance factors (momentum, fatigue, and "The Mental Cliff" analysis) using Google's Gemini 2.0 Flash model for data fetching and strategic insights.

### Core Technologies
- **Language:** Python 3.x
- **AI Model:** Google Gemini 2.0 Flash (via `google-generativeai`)
- **Data Management:** Environment-based configuration (`.env`)
- **Output:** Dynamic HTML reporting (`predictions.html`)

## Architecture & Logic
The system uses a weighted scoring model (Model v2.9 "Master Momentum") to calculate a "Strength Score" for each player:
1.  **Form Supremacy (30%):** Heavily weights year-to-date (YTD) and recent 60-day performance.
2.  **Ranking (20%):** Logarithmic scale to differentiate player classes.
3.  **Surface Performance (15%):** Win/Loss ratio on specific surfaces (Hard, Clay, Grass).
4.  **Strategic Bonuses:** 
    - **Home Bonus (1.05x):** Advantage for local players (e.g., USA players in Austin).
    - **Lefty Bonus (+7%):** Adjusts for the tactical advantage of left-handed players on fast courts.
    - **Streak Penalty (-15 pts):** Deducts points for 3+ consecutive losses.

## Building and Running

### Prerequisites
- Python 3.10+
- A valid `GEMINI_API_KEY` in a `.env` file.

### Installation
```bash
pip install -r requirements.txt
```

### Execution
To run the predictor and fetch data for new matchups:
```bash
python predict.py
```

### Viewing Predictions
Open the `predictions.html` file in any browser to view the latest AI Master Predictions and Learning Logs.

## Development Conventions

### Model Iteration
- The project follows a strict **Research -> Strategy -> Execution** lifecycle.
- **Evidence-Based Calibration:** Every major match outcome (especially upsets) must be documented in the "Learning Log" within `predictions.html` to refine model weights.
- **Project Context:** Current focus is on **WTA Austin (250)** and **WTA Merida (500)**.

### Coding Style
- Use Python type hints for clarity.
- Maintain the `Player` and `MatchPredictor` class abstractions.
- All scoring logic changes must be reflected in the `calculate_score` method in `predict.py`.

### Safety & Security
- Never commit the `.env` file.
- Do not log or print the Gemini API Key.
