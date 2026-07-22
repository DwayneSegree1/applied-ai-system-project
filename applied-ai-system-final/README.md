# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Describe the game's purpose.** Glitchy Guesser is a number-guessing game built with Streamlit. The app picks a secret number within a range that depends on the chosen difficulty (Easy 1–20, Normal 1–100, Hard 1–50), and the player tries to guess it within a limited number of attempts. After each guess the game gives a "higher/lower" hint and updates the score.

- [x] **Detail which bugs you found.**
  - **Wrong direction hint:** On even-numbered attempts the secret was cast to a string (`str(secret)`), so comparing the integer guess to a string raised a `TypeError`. The fallback path then compared the values as *text* (e.g. `"0" > "42"`), which produced the wrong hint — guessing a low number like `0` told the player to "Go LOWER" instead of "Go HIGHER".
  - **Swapped outcome labels:** A guess below the secret was labeled `"Too High"`, contradicting its own "Go HIGHER" message.
  - **Hardcoded range text:** The prompt always read "between 1 and 100" even on Easy (1–20) or Hard (1–50).
  - **Broken tests:** The existing tests compared `check_guess(...)` to a plain string, but the function returns a `(outcome, message)` tuple, so they failed.

- [x] **Explain what fixes you applied.**
  - Rewrote `check_guess` to compare numerically and return correct, consistent labels: a guess below the secret → `"Too Low"` / "Go HIGHER", above → `"Too High"` / "Go LOWER".
  - Removed the even-attempt `str(secret)` conversion in `app.py` that caused the type mismatch.
  - Moved `check_guess` into `logic_utils.py` and imported it into `app.py`.
  - Made the guess prompt show the real difficulty range instead of a hardcoded 1–100.
  - Fixed the pre-existing tests to unpack the tuple and added a regression test (`test_low_guess_says_go_higher`) that locks in the `0 → "Go HIGHER"` behavior.

## 📸 Demo Walkthrough

A sample playthrough on **Normal** difficulty (secret number is **70**, range 1–100):

1. The game starts and prompts: *"Guess a number between 1 and 100."*
2. User enters **40** → the guess is below the secret, so the game returns **"Too Low" — 📈 Go HIGHER!** (this is the corrected behavior; before the fix, low guesses could wrongly say "Go LOWER").
3. User enters **80** → the guess is above the secret, so the game returns **"Too High" — 📉 Go LOWER!**
4. The score updates after each guess based on the outcome and attempt number, and the "Attempts left" counter ticks down.
5. User enters **70** → exact match, so the game returns **"🎉 Correct!"**, shows balloons, reveals the secret, and displays the final score.
6. The game switches to a "won" state; starting a **New Game** picks a fresh secret and resets the round.

**Edge case (regression check):** entering **0** correctly responds with **"Go HIGHER!"** — the exact input that triggered the original direction bug.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
# Paste your pytest output here, e.g.:
# pytest tests/
# ========================= X passed in 0.XXs =========================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
