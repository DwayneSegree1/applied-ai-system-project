from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


def test_low_guess_says_go_higher():
    """Regression test for the guess-direction bug.

    Previously, low guesses (especially 0) were compared as strings on some
    attempts, which made the game tell the player to "Go LOWER" even though
    their guess was below the secret. A guess below the secret must always
    return the "Too Low" outcome with a "Go HIGHER" hint.
    """
    outcome, message = check_guess(0, 42)
    assert outcome == "Too Low"
    assert "HIGHER" in message
