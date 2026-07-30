import secrets
import string
from collections.abc import Callable

SHORT_CODE_ALPHABET = string.digits + string.ascii_letters
SHORT_CODE_LENGTH = 7

ShortCodeSource = Callable[[], str]


def generate_short_code() -> str:
    return "".join(
        secrets.choice(SHORT_CODE_ALPHABET) for _ in range(SHORT_CODE_LENGTH)
    )


def short_code_source() -> ShortCodeSource:
    return generate_short_code
