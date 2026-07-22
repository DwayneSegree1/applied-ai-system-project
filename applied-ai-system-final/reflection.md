# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
Before I ran it, it look production ready with clear instructions - nothing really stood out.
After running it, it started to guess numbers that are out of range


- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

1. The game kept saying I should go lower even though I entered zero and the 
 game should guess values between 1 - 100.
   2. After clicking new game, the game does not restart

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| 1 | Guess again| | Go lower| None
| -2 | Out of range | Go lower|None|
| -20| Out of range| Go Lower| None |

---

## 2. How did you use AI as a teammate?
I was running a command (python -m streamlit run app.py) in the terminal that was not working and the AI was able to identify why the command was not working. 
"python" section of the command was incorrect and required "python3" as python2
was not installed on my laptop.

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)? CoPilot and ChatGPT
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).

The "Go LOWER" bug had two parts working together:

String conversion on even attempts — every other guess, the code did secret = str(st.session_state.secret), turning the number into text. Comparing 0 < "42" raises a TypeError in Python, falling into an except block that did a text comparison ("0" > "42"), which gives nonsense answers. I removed the conversion so the secret is always compared as a number.

Swapped labels — guess < secret was returning "Too High". When your guess is below the secret you need to go higher, so I corrected the labels (Too Low → "Go HIGHER", Too High → "Go LOWER") and dropped the dead string-comparison fallback.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result). So far there we no sugestions by the AI that was misleading, it was able to identify the bug correctly and apply the correct fix

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
I ran the same test case which throw the error/was giving the bug along with a couple variety of the similar case and the code worked perfectly. 

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.
I entered a value that is negative or out of range (1 -100) and to test the comparrison logic that the code is using to compare the guessed value and the secret. This reveled that there was a bug in the code base

- Did AI help you design or understand any tests? How?
The AI helped me understand why the particular bug was happening and predicted correctly where in the code base the error is. But the actually test case was derived by me. 

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
