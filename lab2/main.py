import sys
import os
from typing import Union


def check_token(token: Union[str, int]) -> int:
    if isinstance(token, int):
        value = token
    elif isinstance(token, str):
        # Če je token type str ga probamo prevesti v int.
        try:
            value = int(token)
        except ValueError as e:
            raise ValueError(f"Token {token!r} is not a valid integer") from e
    else:
        raise TypeError(f"token must be str or int, not {type(token).__name__}")

    # Če ima token preveliko vrednost ni validen unicode character.
    if value > 0x10FFFF:
        raise ValueError(f"Token too large: {value}")

    # Vrednost more biti pozitivna.
    if value < 0:
        raise ValueError(f"Token must be non-negative, got {value}")

    # Vrednosti za "surrogate" števila.
    # https://learn.microsoft.com/en-us/windows/win32/intl/surrogates-and-supplementary-characters#about-supplementary-characters
    # https://www.johndcook.com/blog/2025/03/09/unicode-surrogates/
    if 0xD800 <= value and value <= 0xDFFF:
        raise ValueError(f"Token cant be supplementary/surrage: {token}")

    return value


def encode_utf8(token: int) -> bytes:
    """
    Ročno kodiranje Unicode za bajte UTF-8.
    """

    # 1 bajt: 0xxxxxxx
    if token <= 0x7F:
        return bytes([token])

    # 2 bajta: 110xxxxx 10xxxxxx
    if token <= 0x7FF:
        return bytes(
            [
                0b11000000 | (token >> 6),
                0b10000000 | (token & 0b00111111),
            ]
        )

    # 3 bajti: 1110xxxx 10xxxxxx 10xxxxxx
    if token <= 0xFFFF:
        return bytes(
            [
                0b11100000 | (token >> 12),
                0b10000000 | ((token >> 6) & 0b00111111),
                0b10000000 | (token & 0b00111111),
            ]
        )

    # 4 bajti: 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx
    return bytes(
        [
            0b11110000 | (token >> 18),
            0b10000000 | ((token >> 12) & 0b00111111),
            0b10000000 | ((token >> 6) & 0b00111111),
            0b10000000 | (token & 0b00111111),
        ]
    )


def convert_file(input_path: str, output_path: str) -> None:
    """
    Preberemo datoteko in jo zapisemo v novo datoteko zapisano z UTF-8.
    """
    # Brana datoteka ima samo številke in vejice, zato jo lahko preberemo kot ASCII.
    with open(input_path, encoding="ASCII") as f:
        content = f.read()

    # Shranimo podatke iz datoteke v tip "list".
    tokens = content.split(", ")

    # Definiramo izhod.
    out = bytearray()

    for tok in tokens:
        # Prevedmo iz številk v znake.
        out.extend(encode_utf8(check_token(tok)))

    # Zapišemo rezultat v datoteko.
    with open(output_path, "wb") as f:
        f.write(out)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: main.py <input_file> <output_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Preverimo ali datoteka obstaja.
    if not os.path.isfile(input_path):
        raise OSError(f"Input file does not exist: {input_path}")

    # Preverimo ali lahko prebermo datoteko.
    if not os.access(input_path, os.R_OK):
        raise OSError(f"Input file is not readable: {input_path}")

    # Preverimo ali imamo dostop do direktorija za shranjevanje datoteke.
    full_output_path = os.path.abspath(output_path)

    # Direktorij, kamor bomo pisali.
    output_dir = os.path.dirname(full_output_path) or os.getcwd()

    # Preveri, ali direktorij obstaja.
    if not os.path.isdir(output_dir):
        raise OSError(f"Output directory does not exist: {output_dir}")

    # Preveri, ali lahko v ta direktorij pišemo.
    if not os.access(output_dir, os.W_OK):
        raise OSError(f"Output directory not writable: {output_dir}")

    convert_file(input_path, output_path)
