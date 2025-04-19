# Palindrome Checker 🚀

Welcome to the *Bazing!* Palindrome Checker, a Python tool that hunts for palindromes in any text, from “Racecar” to “A man, a plan, a canal -- Panama”! Whether you’re scanning a sentence or a whole article, this checker supports left-to-right, right-to-left, and *center-out* modes, with emoji flair 😊👍 and case-preserving magic. Built with a sci-fi twist inspired by the *Zyran Saga*, it’s ready to impress at xAI interviews or dazzle on GitHub! 🌟

## Overview

This project checks for palindromes—sequences that read the same forward and backward—in text inputs. It ignores spaces, punctuation, and diacritics, supports emojis, and tracks positions for real-world text analysis. From palindromic sentences like “Sore was I ere I saw Eros” to emoji strings like 😊👍😊, it’s robust, fun, and *bazing!* 🚀

## Features

- **Multi-Mode Processing**:
  - `ltr`: Left-to-right (e.g., `#Racecar`).
  - `rtl`: Right-to-left for scripts like Arabic.
  - `center-out`: Expands from the middle for *bazing!* flair.
- **Emoji Support**: Handles 😊, 👍, 🚀, 🙌, 👋, 🌟, 🐾 (with skin tone variants).
- **Case Preservation**: Outputs `#RaDaR` with original capitalization.
- **Robust Text Handling**:
  - Skips spaces, punctuation, and diacritics.
  - Tracks palindrome positions in text.
  - Processes streams or full paragraphs.
- **Performance**: Hash caching for efficient character comparison.
- **Fun Outputs**: Detailed `:FINAL:` messages with skipped char counts and *bazing!* vibes.

## Installation

Get started on Windows 11 (or any platform) with Python 3.8+.

1. **Install Python**:

   - Download from python.org.
   - Ensure `pip` and `Add to PATH` are selected during setup.

2. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/palindrome-checker.git
   cd palindrome-checker
   ```

3. **Install Dependencies**:

   - No external libraries needed! The script uses only `unicodedata` (built-in).

4. **Verify Setup**:

   ```bash
   python --version
   ```

## Usage

Run the script to scan text for palindromes.

1. **Run the Script**:

   ```bash
   python PalindromeChecker.py
   ```

   - The script includes test cases for an article scan and emoji-augmented text.

2. **Customize Inputs**:

   - Edit the `test_paragraphs` list in `PalindromeChecker.py` to add your text.
   - Example:

     ```python
     test_paragraphs = [
         ("Your text here!", "ltr", 2),
         ("😊👍😊 in center!", "center-out", 2),
     ]
     ```

3. **Interpret Outputs**:

   - Outputs show `#WORD`, validity, and `:FINAL:` details (e.g., valid chars, skipped spaces).
   - Example:

     ```
     Found palindrome: #AmanaplanacanalPanama is True :FINAL: Valid palindrome with preserved case and unique emojis built from left-to-right! Valid chars: 22. Skipped 5 spaces, 2 commas, 2 dashes. [Positions 82–103]
     ```

## Examples

Here’s what the checker found in an article from University of Arizona:

- **Full Sentence**:

  ```
  Found palindrome: #AmanaplanacanalPanama is True :FINAL: Valid palindrome with preserved case and unique emojis built from left-to-right! Valid chars: 22. Skipped 5 spaces, 2 commas, 2 dashes. [Positions 82–103]
  ```
- **Substring**:

  ```
  Found palindrome: #ere is True :FINAL: Valid palindrome with preserved case and unique emojis built from left-to-right! Valid chars: 3. Skipped 2 spaces. [Positions 59–61]
  ```
- **Center-Out Mode**:

  ```
  Found palindrome: #SorewasIereIsawEros is True :FINAL: Valid palindrome with preserved case and unique emojis built from center-out! Valid chars: 20. Skipped 4 spaces. *Bazing!* [Positions 54–73]
  ```
- **Emoji Test**:

  ```
  Found palindrome: #😊👍😊 is True :FINAL: Valid palindrome with preserved case and unique emojis built from left-to-right! Valid chars: 3. Skipped 6 spaces, 2 commas, 2 dashes. [Positions 23–25]
  ```

## Contributing

Love palindromes? Want to add new modes or optimize performance? Contributions are welcome! 🎉

1. Fork the repo.
2. Create a branch (`git checkout -b feature/awesome-mode`).
3. Commit changes (`git commit -m "Added palindrome mode"`).
4. Push to the branch (`git push origin feature/awesome-mode`).
5. Open a Pull Request.

Please include tests and update the README for new features.

## License

MIT License. See LICENSE for details.

## Credits

Crafted with *Zyran Saga* flair by \[Elirjo\]. Inspired by palindromic adventures and *bazing!* center-out magic. Special thanks to the xAI team for sparking curiosity! 🌟

---

*Built to conquer palindromes like a Fortnite recon legend!* 😄