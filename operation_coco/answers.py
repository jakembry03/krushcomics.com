"""
Checking security-question answers.

Answers are never stored. Each accepted answer is normalized, so small
differences in how Coco types it don't matter, and saved as a salted
hash. Use only made-up examples anywhere in the code, like the ones
below.
"""
import unicodedata

from django.contrib.auth.hashers import check_password, make_password

STOP_WORDS = {"a", "an", "the", "and"}


def normalize_answer(text):
    """
    Reduce an answer to a canonical form:

    - Unicode NFKC, lowercase, and accents removed ("Café" -> "cafe")
    - "&" becomes "and"
    - anything other than letters and digits becomes a space
    - the words "a", "an", "the", and "and" are dropped
    - all spaces are removed

    So "The Cat & the Hat" and "cat hat" both become "cathat", and
    "A Red Balloon" and "red balloon" both become "redballoon".
    """
    text = unicodedata.normalize("NFKC", text or "").casefold()
    text = "".join(
        char for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )
    text = text.replace("&", " and ")
    text = "".join(char if char.isalnum() else " " for char in text)
    return "".join(word for word in text.split() if word not in STOP_WORDS)


def hash_answer(answer):
    """
    Salted hash of an answer's normalized form, for SecurityQuestion.
    Raises ValueError if nothing is left after normalizing.
    """
    normalized = normalize_answer(answer)
    if not normalized:
        raise ValueError("That answer is empty once normalized.")
    return make_password(normalized)


def check_answer(question, answer):
    """
    True if the answer matches any of the question's accepted answers.
    """
    normalized = normalize_answer(answer)
    if not normalized:
        return False
    return any(check_password(normalized, stored) for stored in question.answer_hashes)
