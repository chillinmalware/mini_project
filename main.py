# main.py
# Entry point and input processor for the ASEAN Phonebook program.
#
# Responsibilities:
#   - Read the complete raw input from stdin
#   - Verify the version header and command count
#   - Parse each input line into its command and fields
#   - Dispatch to the correct Phonebook method
#   - Print each result line
#
# This module must NOT directly modify node.next or phonebook.head.
# All structural changes to the linked list go through Phonebook's methods.

from __future__ import annotations

import sys

from constants import COUNTRY_CODES
from contact import Contact, validate_contact
from phonebook import Phonebook


def is_canonical_count(value: str) -> bool:
    """Return True for a valid command-count string per the project spec.

    A valid count is:
      - Exactly "0", OR
      - A string of digits with no leading zero and no sign prefix

    Examples:
      "0"   → True
      "5"   → True
      "120" → True
      "005" → False  (leading zero)
      "+5"  → False  (sign prefix)
      ""    → False  (empty)
      "201" → still passes this check; the 200-cap is enforced in run_program()
    """
    if not value:
        return False
    if value == "0":
        return True
    return value.isdigit() and value[0] != "0"


def process_input_line(phonebook: Phonebook, line: str) -> str:
    """Parse one phonebook input line, dispatch to Phonebook, and return the output string.

    The line is split on '|' to extract the command token and its arguments.
    Each command branch validates field count first (ERROR MALFORMED <CMD> if wrong),
    then delegates validation and uniqueness checking to Contact / Phonebook.

    Returns one complete output string (may contain embedded newlines for multi-line
    responses like LIST and FIND_SURNAME).
    """
    # A blank or whitespace-only line is always malformed
    if not line.strip():
        return "ERROR MALFORMED"

    parts = line.split("|")
    command = parts[0]  # First segment is always the command token

    if command == "ADD":
        # ADD requires exactly 8 pipe-separated segments:
        # ADD|student_id|surname|given_name|occupation|country_code|area_code|local_number
        if len(parts) != 8:
            return "ERROR MALFORMED ADD"
        # Unpack all fields (ignore the leading "ADD" token via _ convention)
        _, student_id, surname, given_name, occupation, country_code, area_code, local_number = parts
        contact = Contact(student_id, surname, given_name, occupation, country_code, area_code, local_number)
        # Validate field values before checking duplicates
        error = validate_contact(contact)
        if error:
            return error
        return phonebook.add_contact(contact)

    elif command == "FIND":
        # FIND requires exactly 2 segments: FIND|student_id
        if len(parts) != 2:
            return "ERROR MALFORMED FIND"
        return phonebook.find_contact(parts[1])

    elif command == "FIND_SURNAME":
        # FIND_SURNAME requires exactly 2 segments: FIND_SURNAME|surname
        if len(parts) != 2:
            return "ERROR MALFORMED FIND_SURNAME"
        return phonebook.find_by_surname(parts[1])

    elif command == "UPDATE":
        # UPDATE requires exactly 4 segments: UPDATE|target_id|FIELD|new_value
        if len(parts) != 4:
            return "ERROR MALFORMED UPDATE"
        _, target_id, field, new_value = parts
        return phonebook.update_contact(target_id, field, new_value)

    elif command == "DELETE":
        # DELETE requires exactly 2 segments: DELETE|student_id
        if len(parts) != 2:
            return "ERROR MALFORMED DELETE"
        return phonebook.delete_contact(parts[1])

    elif command == "LIST":
        # LIST takes no arguments — the line must be exactly "LIST" with no pipe
        if len(parts) != 1:
            return "ERROR MALFORMED LIST"
        return phonebook.list_contacts()

    elif command == "COUNTRY":
        # COUNTRY requires exactly 2 segments: COUNTRY|code[,code,...]
        # The code list must be non-empty; each code must be in COUNTRY_CODES.
        if len(parts) != 2 or not parts[1].strip():
            return "ERROR INVALID_VALUE COUNTRY_CODES"

        raw_codes = parts[1].split(",")

        # Guard against empty segments from malformed input like "63,,60"
        if not raw_codes or any(c.strip() == "" for c in raw_codes):
            return "ERROR INVALID_VALUE COUNTRY_CODES"

        # Validate each code and deduplicate while preserving first-occurrence order.
        # Repeated codes are silently ignored (spec: "COUNTRY|63,63,60" == "COUNTRY|63,60").
        seen = set()
        unique_codes = []
        for code in raw_codes:
            code = code.strip()
            if not code:
                return "ERROR INVALID_VALUE COUNTRY_CODES"
            if code not in COUNTRY_CODES:
                # Report the first unrecognized code encountered
                return f"ERROR INVALID_COUNTRY {code}"
            if code not in seen:
                seen.add(code)
                unique_codes.append(code)

        return phonebook.filter_by_country(set(unique_codes))

    else:
        # The command token is not any recognized keyword
        return f"ERROR UNKNOWN_COMMAND {command}"


def run_program(raw_input: str) -> str:
    """Process one complete ASEAN-PHONEBOOK 1.0 input and return the full output string.

    Steps:
      1. Normalise line endings to '\\n' and split into lines.
      2. Check the version header (first line must be "ASEAN-PHONEBOOK 1.0").
      3. Parse and validate the command count (second line).
      4. Process exactly <count> input lines through process_input_line().
      5. Join all result lines and return the combined output.

    Early exits return a single error string and stop processing:
      ERROR VERSION       — bad or missing header
      ERROR COMMAND_COUNT — missing, malformed, out-of-range, or insufficient lines
    """
    # Normalise Windows line endings before splitting
    lines = raw_input.replace("\r\n", "\n").split("\n")

    # Line 0: version header
    if not lines or lines[0].rstrip() != "ASEAN-PHONEBOOK 1.0":
        return "ERROR VERSION"

    # Line 1: command count — must be a canonical integer in [0, 200]
    if len(lines) < 2 or not is_canonical_count(lines[1].strip()):
        return "ERROR COMMAND_COUNT"

    count = int(lines[1].strip())
    if count > 200:
        return "ERROR COMMAND_COUNT"

    # Lines 2+: the actual phonebook commands
    input_lines = lines[2:]

    # Ensure there are at least <count> lines available to process
    if len(input_lines) < count:
        return "ERROR COMMAND_COUNT"

    # Fresh phonebook for this run — no state persists between program invocations
    phonebook = Phonebook()
    output_lines = []

    for i in range(count):
        # Strip trailing carriage return / newline artifacts but keep internal content intact
        line = input_lines[i].rstrip("\n").rstrip("\r")
        result = process_input_line(phonebook, line)
        output_lines.append(result)

    # Join all individual result strings into one output block
    return "\n".join(output_lines)


def main() -> None:
    """Read standard input, run the phonebook program, and print its output."""
    output = run_program(sys.stdin.read())
    if output:
        print(output)


if __name__ == "__main__":
    main()
