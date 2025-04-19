import unicodedata

# Custom exceptions
class InvalidInputError(Exception):
    """Raised for null, empty, space-only, or non-string inputs."""
    pass

class UnallowedCharacterError(Exception):
    """Raised for unallowed emojis or invalid characters."""
    pass

# Constant array of allowed emojis, including skin tone variants
ALLOWED_EMOJIS = [
    "😊", "😊🏻", "😊🏼", "😊🏽", "😊🏾", "😊🏿",  # Smiling Face
    "👍", "👍🏻", "👍🏼", "👍🏽", "👍🏾", "👍🏿",  # Thumbs Up
    "🚀",  # Rocket
    "🙌", "🙌🏻", "🙌🏼", "🙌🏽", "🙌🏾", "🙌🏿",  # Raised Hands
    "👋", "👋🏻", "👋🏼", "👋🏽", "👋🏾", "👋🏿",  # Waving Hand
    "🌟",  # Glowing Star
    "🐾"   # Paw Prints
]

def is_null(s):
    """Check if string is null."""
    return s is None

def is_empty(s):
    """Check if string is empty or contains only spaces."""
    return len(s) == 0 or s.isspace()

def is_emoticon(char):
    """Check if a single char is an allowed emoji, return (char, is_allowed)."""
    if char.isalpha() or char.isspace():
        return (char, False)
    return (char, char in ALLOWED_EMOJIS)

def clean(char, valid_chars=None):
    """Check if char is a letter or allowed emoji, reject spaces and diacritics."""
    if char.isspace() or unicodedata.category(char) == 'Mn':  # Skip non-spacing marks
        return False
    if valid_chars is not None:
        return char in valid_chars
    if char.isalpha():
        return True
    _, is_allowed = is_emoticon(char)
    if not is_allowed:
        raise UnallowedCharacterError(f"Unallowed character '{char}'")
    return True

def has_valid_chars(s, valid_chars=None):
    """Check if s has at least one valid character."""
    return any(clean(c, valid_chars) for c in s)

def hash_char(c, cache=None):
    """Lightweight hash for a character, using cache if provided."""
    if cache is not None and c in cache:
        return cache[c]
    normalized = unicodedata.normalize('NFC', c.lower())
    result = ord(normalized[0]) if normalized and normalized[0].isalpha() else hash(normalized)
    if cache is not None:
        cache[c] = result
    return result

class Left:
    """Manages the left pointer for stream processing."""
    def __init__(self, buffer, pos, direction="ltr", valid_chars=None):
        self.buffer = buffer
        self.pos = pos
        self.direction = direction
        self.valid_chars = valid_chars
        self.valid = True
        self.chars = []

    def set_char(self, char, was_capitalized, is_emoji, is_allowed):
        """Store a valid character with its states."""
        self.chars.append((char, was_capitalized, is_emoji, is_allowed))

    def get_chars(self):
        """Return stored characters."""
        return self.chars

    def get_hash(self, hash_cache):
        """Get hash of current character, store it, or return None if invalid."""
        if not self.valid or self.pos < 0 or self.pos >= len(self.buffer):
            self.valid = False
            return None
        char = self.buffer[self.pos]
        if not clean(char, self.valid_chars):
            self.valid = False
            return None
        if char.isalpha():
            was_capitalized = char.isupper()
            is_emoji = False
            is_allowed = True
        else:
            _, is_allowed = is_emoticon(char)
            is_emoji = is_allowed
            was_capitalized = False
            if not is_allowed:
                self.valid = False
                return None
        self.set_char(char, was_capitalized, is_emoji, is_allowed)
        return hash_char(char, hash_cache)

    def advance(self):
        """Move to the next position."""
        self.pos += 1 if self.direction in ["ltr", "center-out"] else -1
        if self.pos < 0 or self.pos >= len(self.buffer):
            self.valid = False

class Right:
    """Manages the right pointer for stream processing."""
    def __init__(self, buffer, pos, direction="ltr", valid_chars=None):
        self.buffer = buffer
        self.pos = pos
        self.direction = direction
        self.valid_chars = valid_chars
        self.valid = True
        self.chars = []

    def get_hash(self, hash_cache):
        """Get hash of current character, skip storage, or return None if invalid."""
        if not self.valid or self.pos < 0 or self.pos >= len(self.buffer):
            self.valid = False
            return None
        char = self.buffer[self.pos]
        if not clean(char, self.valid_chars):
            self.valid = False
            return None
        if not char.isalpha():
            _, is_allowed = is_emoticon(char)
            if not is_allowed:
                self.valid = False
                return None
        return hash_char(char, hash_cache)

    def advance(self):
        """Move to the previous position."""
        self.pos -= 1 if self.direction in ["ltr", "center-out"] else 1
        if self.pos < 0 or self.pos >= len(self.buffer):
            self.valid = False

class StreamProcessor:
    """Processes palindrome stream with ltr, rtl, or center-out reading."""
    def __init__(self, direction="ltr", valid_chars=None):
        self.buffer = []
        self.direction = direction
        self.valid_chars = valid_chars
        self.left = None
        self.right = None
        self.center = -1
        self.valid = True
        self.error_msg = None
        self.stopped = False
        self.skipped_diacritics = 0
        self.skipped_spaces = 0
        self.hash_cache = {}

    def reset(self):
        """Reset the processor to initial state."""
        self.buffer = []
        self.valid = True
        self.error_msg = None
        self.stopped = False
        self.skipped_diacritics = 0
        self.skipped_spaces = 0
        self.hash_cache = {}
        self.left = None
        self.right = None
        self.center = -1

    def process_char(self, char, auto_reset=False):
        """Process a single character in the stream."""
        if self.stopped:
            if auto_reset:
                self.reset()
            else:
                return False, self.error_msg, []

        try:
            if is_null(char) or not isinstance(char, str) or len(char) != 1:
                self.valid = False
                self.error_msg = "Input Error: Invalid character"
                self.stopped = True
                return False, self.error_msg, []

            # Track skipped chars
            if char.isspace():
                self.skipped_spaces += 1
                return False, None, []
            if unicodedata.category(char) == 'Mn':
                self.skipped_diacritics += 1
                return False, None, []

            # Validate character
            if not clean(char, self.valid_chars):
                return False, None, []

            # Append to buffer
            self.buffer.append(char)

            # Initialize or update pointers
            if self.direction == "center-out":
                self.center = len(self.buffer) // 2
                left_pos = self.center - (len(self.buffer) // 2)
                right_pos = self.center + (len(self.buffer) // 2)
            else:
                left_pos = 0 if self.direction == "ltr" else len(self.buffer) - 1
                right_pos = len(self.buffer) - 1 if self.direction == "ltr" else 0

            self.left = Left(self.buffer, left_pos, self.direction, self.valid_chars)
            self.right = Right(self.buffer, right_pos, self.direction, self.valid_chars)

            # Validate palindrome
            self.left.pos = left_pos
            self.right.pos = right_pos
            self.left.chars = []
            valid_char_count = 0
            while self.left.valid and self.right.valid and \
                  ((self.direction in ["ltr", "center-out"] and self.left.pos < self.right.pos) or \
                   (self.direction == "rtl" and self.left.pos > self.right.pos)):
                left_hash = self.left.get_hash(self.hash_cache)
                right_hash = self.right.get_hash(self.hash_cache)
                if left_hash is None or right_hash is None or left_hash != right_hash:
                    self.valid = False
                    return False, self.error_msg, []
                valid_char_count += 1
                self.left.advance()
                self.right.advance()

            self.valid = self.left.valid and self.right.valid
            chars = self.left.get_chars() if self.valid else []
            self.error_msg = None
            return self.valid, self.error_msg, chars

        except UnallowedCharacterError as e:
            self.valid = False
            self.error_msg = f"Character Error: {e}"
            self.stopped = True
            return False, self.error_msg, []

def String_Output(word, result, error_msg=None, direction="ltr", chars=None, streaming=False, skipped_diacritics=0, skipped_spaces=0):
    """Format palindrome result with #WORD or #INVALID and :FINAL: details."""
    is_valid_input = (
        word is not None and
        isinstance(word, str) and
        not is_empty(word) and
        has_valid_chars(word)
    )
    if is_valid_input and chars and result:
        half_stack = [(char, was_cap, is_emoji, is_allowed) for char, was_cap, is_emoji, is_allowed in chars]
        if len(half_stack) == 1:
            mirrored = half_stack
        else:
            mirrored = half_stack + [(char, was_cap, is_emoji, is_allowed) for char, was_cap, is_emoji, is_allowed in half_stack[-1::-1]]
            expected_length = 2 * len(half_stack) - 1
            mirrored = mirrored[:expected_length]
        display_chars = [
            char if is_emoji else (char.upper() if was_cap and char.isalpha() else char.lower() if char.isalpha() else char)
            for char, was_cap, is_emoji, is_allowed in mirrored
        ]
        display_word = "".join(display_chars) if direction in ["ltr", "center-out"] else "".join(display_chars[::-1])
    else:
        display_word = word if is_valid_input and not result else "INVALID"
    output = f"#{display_word} is {result}"
    if error_msg:
        output += f" :FINAL: {error_msg}"
    else:
        direction_text = "left-to-right" if direction == "ltr" else "right-to-left" if direction == "rtl" else "center-out"
        status = "Valid palindrome" if result else "Building palindrome" if streaming and is_valid_input else "Not a palindrome"
        skip_info = []
        if skipped_diacritics > 0:
            skip_info.append(f"{skipped_diacritics} diacritic{'s' if skipped_diacritics > 1 else ''}")
        if skipped_spaces > 0:
            skip_info.append(f"{skipped_spaces} space{'s' if skipped_spaces > 1 else ''}")
        skip_text = f" Skipped {', '.join(skip_info)}." if skip_info else ""
        valid_chars = len([c for c in word if clean(c)]) if is_valid_input else 0
        char_text = f" Valid chars: {valid_chars}." if result else ""
        output += f" :FINAL: {status} with preserved case and unique emojis built from {direction_text}!{char_text}{skip_text}{' *Bazing!*' if direction == 'center-out' else ''}"
    return output

def stream_palindrome(chars, direction="ltr", valid_chars=None, auto_reset=False):
    """Process a stream of characters and check for palindrome."""
    processor = StreamProcessor(direction, valid_chars)
    results = []
    current_word = ""
    for char in chars:
        current_word += char
        result, error_msg, chars_out = processor.process_char(char, auto_reset)
        results.append(String_Output(
            current_word, result, error_msg, direction, chars_out, streaming=True,
            skipped_diacritics=processor.skipped_diacritics, skipped_spaces=processor.skipped_spaces
        ))
    return results

def find_palindromes_in_paragraph(paragraph, direction="ltr", valid_chars=None, min_length=1):
    """Find all palindromes in a paragraph, returning their positions and details."""
    if is_null(paragraph) or not isinstance(paragraph, str):
        raise InvalidInputError("Paragraph must be a non-null string")
    if is_empty(paragraph):
        return []

    # Extract valid char sequences
    valid_sequences = []
    current_sequence = []
    start_pos = 0
    for i, char in enumerate(paragraph):
        try:
            if clean(char, valid_chars):
                if not current_sequence:
                    start_pos = i
                current_sequence.append(char)
            else:
                if current_sequence:
                    valid_sequences.append((start_pos, i - 1, current_sequence))
                    current_sequence = []
        except UnallowedCharacterError:
            if current_sequence:
                valid_sequences.append((start_pos, i - 1, current_sequence))
                current_sequence = []

    if current_sequence:
        valid_sequences.append((start_pos, len(paragraph) - 1, current_sequence))

    # Check each sequence and its substrings for palindromes
    palindromes = []
    for start, end, sequence in valid_sequences:
        sequence_str = "".join(sequence)
        # Check all substrings of valid chars
        for i in range(len(sequence)):
            for j in range(i, len(sequence)):
                substring = sequence[i:j + 1]
                if len(substring) < min_length:
                    continue
                processor = StreamProcessor(direction, valid_chars)
                result = True
                chars_out = []
                error_msg = None
                for char in substring:
                    res, err, chars = processor.process_char(char)
                    if not res:
                        result = False
                        error_msg = err
                        chars_out = []
                        break
                    chars_out = chars
                if result:
                    substring_str = "".join(substring)
                    output = String_Output(
                        substring_str, result, error_msg, direction, chars_out,
                        streaming=False, skipped_diacritics=processor.skipped_diacritics,
                        skipped_spaces=processor.skipped_spaces
                    )
                    palindromes.append({
                        "palindrome": substring_str,
                        "start_pos": start + i,
                        "end_pos": start + j,
                        "output": output
                    })

    return palindromes

# Test cases
if __name__ == "__main__":
    # Paragraph test cases
    article_text = """Palindromic Sentences

Some palindromic sentences collected by Ralph Griswold

Sore was I ere I saw Eros.
A man, a plan, a canal -- Panama
Never a foot too far, even.
Euston saw I was not Sue.
Live on evasions? No, I save no evil.
Red Roses run no risk, sir, on nurses order.
Salisbury moor, sir, is roomy.
Rub Silas.
Marge, let's "went." I await news telegram.
A new order began, a more Roman age bred Rowena.
I, man, am regal; a German am I.
Tracy, no panic in a pony-cart.
Egad! Loretta has Adams as mad as a hatter. Old age!
Eve, mad Adam, Eve!
Resume so pacific a pose, muser.
Marge let a moody baby doom a telegram.
Tenet C is a basis, a basic tenet.
Nella's simple hymn: "I attain my help, Miss Allen."
Straw? No, too stupid a fad. I put soot on warts.
Sir, I demand, I am a maid named Iris.
Lay a wallaby baby ball away, Al.
Tessa's in Italy, Latin is asset."""
    
    test_paragraphs = [
        (
            article_text,
            "ltr",
            2  # min_length
        ),
        (
            article_text,
            "center-out",
            2
        ),
        (
            "A man, a plan, a canal -- Panama 😊👍😊",
            "ltr",
            2
        ),
        (
            "A man,,,a plan,,,a canal---Panama",
            "ltr",
            2
        ),
    ]

    for paragraph, direction, min_length in test_paragraphs:
        print(f"\nTesting paragraph in {direction} with min_length={min_length}:")
        try:
            palindromes = find_palindromes_in_paragraph(paragraph, direction, min_length=min_length)
            if not palindromes:
                print("No palindromes found.")
            else:
                # Filter to show full-sentence palindromes and select substrings
                key_palindromes = [p for p in palindromes if len(p['palindrome']) >= 7 or p['palindrome'] in ['ere', 'deked', 'level', 'eve']]
                for p in key_palindromes:
                    print(f"Found palindrome: {p['output']} [Positions {p['start_pos']}–{p['end_pos']}]")
        except InvalidInputError as e:
            print(f"Error: {e}")