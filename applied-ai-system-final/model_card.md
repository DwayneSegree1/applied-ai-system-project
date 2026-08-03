# Model Card — Glitchy Guesser AI Helper

## Model Details
- **Application:** Glitchy Guesser — an AI helper embedded in a Streamlit number-guessing game.
- **Base model:** Google Gemini (`gemini-flash-latest`), accessed via the `google-genai` SDK.
- **System role:** A friendly assistant that helps players with the game (strategy, hints, how it works) and answers general questions, keeping replies short and conversational.
- **Owner:** Dwayne Segree
- **Version:** 1.0

## Intended Use
- **Primary use:** In-game conversational help — offering strategy tips, hints, and answering player questions inside the Glitchy Guesser app.
- **Intended users:** Players interacting with the guessing game through the Streamlit UI.
- **Out-of-scope use:** Not intended for professional advice (medical, legal, financial), high-stakes decision-making, or use as an authoritative source of factual information.

## How It Works
1. The player opens the "💬 Need help? Chat with me!" bubble and types a message.
2. Input is validated and cleaned (`validate_user_input`).
3. The most recent conversation turns are sent to Gemini with a fixed system prompt (`generate_reply`).
4. The model's reply is displayed in the chat and the exchange is stored in session state.

## Guardrails
- **Input validation:** Rejects empty/whitespace input and messages over 500 characters (`MAX_INPUT_CHARS`); the input box also enforces `max_chars`.
- **Context cap:** Only the last 20 turns (`MAX_HISTORY_MESSAGES`) are sent, bounding cost, latency, and runaway context.
- **Output cap:** `max_output_tokens=1024` limits reply length.
- **Timeout:** 30-second request timeout so a stuck call cannot hang the app.
- **Fail-safe errors:** The API call is wrapped in try/except and never raises; errors are logged and returned as a friendly message, and the unanswered user turn is rolled back so history stays consistent.
- **Empty-reply fallback:** If the model returns nothing, the user is asked to rephrase instead of seeing a blank reply.
- **Missing key handling:** If no API key is configured, the app notifies the user and the game still runs without the chatbot.
- **Logging:** Requests, replies, rejections, and errors are recorded to `chatbot.log` (metadata such as character counts and latency, not message content).

## Limitations
- **Hallucinations:** As a large language model, it can produce confident but incorrect answers; a human in the loop is recommended.
- **Scope drift:** Responses may occasionally go beyond the game's context or suggest irrelevant ideas.
- **Non-determinism:** Replies vary between runs for the same prompt.
- **External dependency:** Requires a valid Gemini API key and network access; availability and behavior depend on Google's service.
- **No memory across sessions:** Conversation history is limited to the current Streamlit session and capped at 20 turns.

## Privacy & Data
- User messages are sent to Google's Gemini API for processing and are subject to Google's data policies.
- The API key is stored in `.streamlit/secrets.toml` and is git-ignored so it is not committed to the repository.
- `chatbot.log` stores only metadata (character counts, timings), not the text of user messages or model replies.

## Ethical Considerations
- The assistant is intended for lighthearted, low-stakes game help and general questions.
- Users should not rely on it for critical or sensitive decisions.
- Human oversight is expected, given the model's potential for hallucination and scope drift.
