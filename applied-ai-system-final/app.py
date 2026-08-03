import logging
import os
import random
import time

import streamlit as st
from google import genai
from google.genai import types

from logic_utils import check_guess

CHAT_MODEL = "gemini-flash-latest"
CHAT_SYSTEM_PROMPT = (
    "You are a friendly assistant embedded in a Streamlit number-guessing game "
    "called Glitchy Guesser. Help the player with the game (strategy, hints, how "
    "it works) and answer any general questions they have. Keep replies short and "
    "conversational."
)

# --- Guardrail limits -----------------------------------------------------
MAX_INPUT_CHARS = 500          # reject overly long user messages
MAX_HISTORY_MESSAGES = 20      # cap conversation context sent to the model
MAX_OUTPUT_TOKENS = 1024       # cap the model's reply length
REQUEST_TIMEOUT_S = 30         # give up on a stuck request


@st.cache_resource
def get_logger():
    """Return a singleton logger that writes chatbot activity to chatbot.log."""
    logger = logging.getLogger("glitchy_guesser.chatbot")
    logger.setLevel(logging.INFO)
    if not logger.handlers:  # avoid duplicate handlers across Streamlit reruns
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        file_handler = logging.FileHandler("chatbot.log")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(fmt)
        logger.addHandler(stream_handler)
    return logger


@st.cache_resource
def get_gemini_client():
    """Return a cached Gemini client, or None if no API key is configured."""
    api_key = st.secrets.get("GEMINI_API_KEY", None) if hasattr(st, "secrets") else None
    api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        get_logger().warning("Gemini client unavailable: no API key configured.")
        return None
    get_logger().info("Gemini client initialized (model=%s).", CHAT_MODEL)
    return genai.Client(api_key=api_key)


def validate_user_input(text):
    """Guardrail: clean and validate a user message.

    Returns (ok: bool, cleaned_text: str, error_message: str | None).
    """
    if text is None:
        return False, "", "Please type a message first."
    cleaned = text.strip()
    if not cleaned:
        return False, "", "Please type a message first."
    if len(cleaned) > MAX_INPUT_CHARS:
        return (
            False,
            "",
            f"That message is too long ({len(cleaned)} characters). "
            f"Please keep it under {MAX_INPUT_CHARS} characters.",
        )
    return True, cleaned, None


def generate_reply(client, messages):
    """Call Gemini safely and return (reply_text, error_message).

    Guardrails: trims context to the most recent messages, caps output length,
    enforces a timeout, and never raises — errors come back as a message.
    """
    logger = get_logger()
    # Guardrail: only send the most recent turns to bound cost and latency.
    trimmed = messages[-MAX_HISTORY_MESSAGES:]
    contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part.from_text(text=m["content"])],
        )
        for m in trimmed
    ]
    config = types.GenerateContentConfig(
        system_instruction=CHAT_SYSTEM_PROMPT,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_S * 1000),
    )
    start = time.monotonic()
    logger.info("Model request: %d msgs in context (of %d total).", len(trimmed), len(messages))
    try:
        response = client.models.generate_content(
            model=CHAT_MODEL, contents=contents, config=config
        )
        reply = (response.text or "").strip()
        elapsed = time.monotonic() - start
        if not reply:
            logger.warning("Model returned an empty reply (%.2fs).", elapsed)
            return (
                "Sorry, I couldn't come up with a response. Please try rephrasing.",
                None,
            )
        logger.info("Model reply OK: %d chars in %.2fs.", len(reply), elapsed)
        return reply, None
    except Exception as err:  # guardrail: fail safe, never crash the app
        elapsed = time.monotonic() - start
        logger.exception("Model request failed after %.2fs: %s", elapsed, err)
        return None, "The AI helper is temporarily unavailable. Please try again in a moment."

def get_range_for_difficulty(difficulty: str):
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    # FIXME: Logic breaks here
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def update_score(current_score: int, outcome: str, attempt_number: int):
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(1, 100)
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(message)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            # FIXME: Logic breaks here
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()

# --- AI help bubble -------------------------------------------------------
st.caption("👇 Stuck or curious? Click the bubble below — I'm here to help!")

with st.popover("💬 Need help? Chat with me!", use_container_width=False):
    st.markdown("#### 🤖 Glitchy Guesser Helper")
    st.caption("Ask me for hints, strategy, or anything else!")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    client = get_gemini_client()

    if client is None:
        st.warning(
            "No Gemini API key found. Set `GEMINI_API_KEY` in your "
            "environment or add it to `.streamlit/secrets.toml` to enable the chatbot."
        )
    else:
        # Replay the conversation so far.
        for msg in st.session_state.chat_messages:
            st.chat_message(msg["role"]).write(msg["content"])

        with st.form("chat_form", clear_on_submit=True):
            user_text = st.text_input(
                "Your message",
                placeholder="Ask me anything about the game...",
                max_chars=MAX_INPUT_CHARS,
                label_visibility="collapsed",
            )
            sent = st.form_submit_button("Send 📨")

        if sent:
            logger = get_logger()
            ok, cleaned, error = validate_user_input(user_text)
            if not ok:
                logger.info("Rejected user input: %s", error)
                st.warning(error)
            else:
                logger.info("User message accepted (%d chars).", len(cleaned))
                st.session_state.chat_messages.append(
                    {"role": "user", "content": cleaned}
                )
                with st.spinner("Thinking..."):
                    reply, error = generate_reply(client, st.session_state.chat_messages)
                if error:
                    # Roll back the unanswered user turn so history stays clean.
                    st.session_state.chat_messages.pop()
                    st.error(error)
                else:
                    st.session_state.chat_messages.append(
                        {"role": "assistant", "content": reply}
                    )
                    st.toast("💬 The helper replied — reopen the bubble to read it!")
                    st.rerun()

st.divider()
