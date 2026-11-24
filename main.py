"""One Emoji, One Dream Vacation.

Writes exactly one emoji -- the single most evocative dream-vacation
postcard -- to /output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt).

The pick: a desert island. Palm tree, white sand, turquoise lagoon,
nothing else on the horizon. One glance and a stranger is already
booking the flight.
"""

import os
import stat
import tempfile

# U+1F3DD DESERT ISLAND -- a single Unicode emoji codepoint.
EMOJI = "\U0001F3DD"


def main() -> None:
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(output_dir, exist_ok=True)
    target = os.path.join(output_dir, "entry.txt")

    data = EMOJI.encode("utf-8")
    assert len(data) == 4, "desert-island emoji must encode to 4 UTF-8 bytes"

    # Write via a temp file in the same directory, then atomically replace.
    fd, tmp_path = tempfile.mkstemp(dir=output_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    os.chmod(target, 0o644)

    # Read back and verify: exact bytes, no trailing newline, mode 0644.
    with open(target, "rb") as f:
        actual = f.read()
    assert actual == data, f"entry bytes mismatch: {actual!r} != {data!r}"
    assert not actual.endswith(b"\n"), "entry must have no trailing newline"
    assert len(EMOJI) == 1, "entry must be exactly one character"
    assert EMOJI.strip() == EMOJI and EMOJI, "entry must not be whitespace"
    # The single character must be a genuine emoji codepoint, not a
    # letter, digit, or punctuation mark.
    cp = ord(EMOJI)
    assert cp > 0xFFFF or 0x2600 <= cp <= 0x27BF, (
        f"codepoint U+{cp:04X} is not in an emoji range"
    )
    mode = stat.S_IMODE(os.stat(target).st_mode)
    assert mode == 0o644, f"entry mode is {oct(mode)}, expected 0o644"


if __name__ == "__main__":
    main()
