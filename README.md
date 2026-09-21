# 🎾 Tennis WTA AI & Bukmacher Engine

Zintegrowany system analityczny AI do predykcji wyników meczów tenisa (WTA / ATP) oraz automatyzacji typowania zakładów bukmacherskich z zarządzaniem kapitałem (Kryterium Kelly'ego).

---

## 🏛️ Architektura Systemu

Projekt łączy trzy kluczowe moduły:

### 1. 🧠 Silnik Predykcyjny AI (`predict.py`, `predict_q2.py`)
Oblicza **Wskaźnik Siły Zawodnika (Strength Score 0–100)** na podstawie 5 ważonych kryteriów:
* **Ranking WTA (20%):** Bieżąca pozycja w rankingu światowym.
* **Skuteczność na danej nawierzchni (30%):** Stosunek zwycięstw do porażek na konkretnej nawierzchni (Hard, Clay, Grass) z ostatnich 12 miesięcy.
* **Bieżąca forma na nawierzchni (25%):** Wyniki ostatnich 5 meczów na danym korcie.
* **Ogólna forma sezonowa (15%):** Ostatnie 5 meczów w sezonie bez względu na kort.
* **Bonus specjalisty nawierzchni (10%):** Dodatkowe punkty, jeśli wskaźnik wygranych na danym typie nawierzchni przekracza o >15% średnią kariery.

### 2. 🤖 Mando WTA Betting Agent (`wta_agent.py`, `setup_betting_system.py`)
Moduł autonomiczny dla agenta Mando na VPS:
* Monitoruje nadchodzące mecze i generuje rekomendacje (`wta_tips.json`).
* Zarządza bankrollem za pomocą **Ułamkowego Kryterium Kelly'ego (`fraction=0.25`)**, minimalizując ryzyko bankructwa.
* Prowadzi historię typów i skuteczności (`wta_history.json`).

### 3. 📊 Wizualizacja & Panele HTML
* `index.html` / `predictions.html` — Główny pulpit z zestawieniem predykcji i prawdopodobieństw.
* `charleston_main_draw.html` / `marrakech_atp_qualifications.html` — Drabinki turniejowe i szczegółowe analizy zawodników.
* `tennis_analysis_guidelines.html` — Wytyczne analityczne i heurystyki meczowe.

---

## 🚀 Uruchomienie

### Uruchomienie silnika predykcji lokalnie:
```bash
python3 predict.py
```

### Uruchomienie autonomicznego agenta WTA:
```bash
python3 wta_agent.py
```

### Podgląd wyników:
Otwórz `predictions.html` w dowolnej przeglądarce.
