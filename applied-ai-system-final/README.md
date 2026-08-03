1. Explicitly name your original project (from Modules 1-3) and provide a 2-3 sentence summary of its original goals and capabilities.
I enhanced the gameglitch project which is from module 1 week 1 and 2

2. Title and Summary: What your project does and why it matters.
Along with the help of clude, I was able to implement a AI chat bot on the gameglitch stream lit site which which acts a helper to the users that are interacting with the game. 

3. Architecture Overview: A short explanation of your system diagram.

The system is a single-process Streamlit web app (Glitchy Guesser, a number-guessing game) with an embedded AI chatbot powered by Google Gemini (gemini-flash-latest). It separates two decoupled subsystems:

- Game Engine (deterministic core): Session state in st.session_state holds the secret number, attempts, score, and status. Pure logic functions — get_range_for_difficulty(), parse_guess(), update_score(), and check_guess() (from logic_utils) — drive difficulty, input parsing, and scoring.

- AI Helper (the enhancement): A chat bubble (st.popover) lets players ask for hints or strategy. get_gemini_client() does cached, key-aware client init (reads from Streamlit secrets or env vars and degrades gracefully if no key is present). validate_user_input() and generate_reply() form the request pipeline that cleans input, trims context, calls Gemini, and returns a safe result. A dedicated logger records every request, reply, rejection, and error to chatbot.log.

Data flow:
User → validate_user_input() → append to chat history → generate_reply() [trim to last 20 turns → Gemini API] → on success: append assistant reply; on error: roll back the user turn.

A guardrail layer wraps the AI path end-to-end: input validation (500-char cap), context capping (20 messages), output capping (1024 tokens), a 30s timeout, and fail-safe error handling so an API call never crashes the app.

The key architectural idea is separation of concerns: the deterministic game logic and the probabilistic AI helper are decoupled, so the AI runs as an optional, self-contained module that fails gracefully without affecting gameplay.

4. Setup Instructions: Step-by-step directions to run your code.

Prerequisites: Python 3.9+ and a Google Gemini API key (get one free at https://aistudio.google.com/apikey).

Step 1 — Open a terminal in the project folder:
    cd applied-ai-system-final

Step 2 — (Recommended) Create and activate a virtual environment:
    python3 -m venv .venv
    source .venv/bin/activate        # macOS/Linux
    .venv\Scripts\activate           # Windows

Step 3 — Install the dependencies:
    pip install -r requirements.txt

Step 4 — Provide your Gemini API key using ONE of these options:
    Option A (Streamlit secrets): add this line to .streamlit/secrets.toml
        GEMINI_API_KEY = "your-api-key-here"
    Option B (environment variable):
        export GEMINI_API_KEY="your-api-key-here"   # macOS/Linux
        set GEMINI_API_KEY=your-api-key-here         # Windows
    Note: The game itself runs without a key — the AI helper simply shows a
    "No Gemini API key found" message until a key is provided.

Step 5 — Launch the app:
    streamlit run app.py

Step 6 — Open the app in your browser at http://localhost:8501 (Streamlit
usually opens it automatically). Play the game, then click the
"💬 Need help? Chat with me!" bubble to talk to the AI helper.

Optional — Run the tests:
    pytest
5. Sample Interactions: Include at least 2-3 examples of inputs and the resulting AI outputs to demonstrate the system is functional.

These are real exchanges captured from the running app's AI helper (model: gemini-flash-latest). The chatbot.log confirms the requests were served (e.g. "Model reply OK: 377 chars in 3.50s").

Example 1
User: How to beat the game
AI: The best strategy to win fast is binary search! Always guess the exact middle of your remaining range (for example, start with 50 if the range is 1 to 100). That cuts the remaining possibilities in half every single time.

Just keep a close eye on the feedback—since this is Glitchy Guesser, some hints might try to trick you!

What range are you playing with right now?

Example 2
User: What is the purpose of the game
AI: The main goal is to guess the hidden number in as few tries as possible!

The fun twist is outsmarting the game itself—you have to use your logic to spot when a "glitch" is trying to throw you off course.

Are the glitches giving you a hard time, or are you holding your own?

6. Design Decisions: Why you built it this way, and what trade-offs you made.
I built the chatbot this way because I think its enhances the UX and the UI looks cohesive

7. Testing Summary: What worked, what didn't, and what you learned.
At first I did not know how to configure the API key but I eventually figured it out. Cluade helped me to add the API key to the gitignore so that it wouldnt be committed to the publc which I thibk was a good ctach

8. Reflection: A brief note on what this project taught you about AI and problem-solving. Overall, this project taught me the capabilities of AI and what can be achieved. I think AI tools are really powerful at turning what might be days of debugging work into 10 minutes, but I also believe a human in the loop is still required, because hallucinations do happen and AI tends to deviate from the scope at times, sometimes suggesting additions that are not relevant or too grand.

Reliability and Evaluation:
Guradrails implemented: 
Input validation — validate_user_input() rejects empty/whitespace and messages over MAX_INPUT_CHARS (500); the text box also enforces max_chars.
Context cap — Only the last MAX_HISTORY_MESSAGES (20) turns are sent — bounds cost/latency and runaway context.
Output cap — max_output_tokens=1024 limits reply length.
Timeout — 30s request timeout so a stuck call can't hang the app.
Fail-safe errors — generate_reply() wraps the API call in try/except — it never raises. Errors are logged and returned as a friendly message; the unanswered user turn is rolled back so history stays consistent.
Empty-reply fallback — If the model returns nothing, the user gets a "try rephrasing" message instead of a blank.
Missing key — Notify that the Api Key is Missing

All test case passed and the AI chatbot functions as expected.