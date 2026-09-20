from __future__ import annotations

import sys

from constants import COUNTRY_CODES
from contact import Contact, validate_contact
from phonebook import Phonebook


def is_canonical_count(value: str) -> bool:
    """Return True for 0 or a nonzero decimal without signs/leading zeros."""
    if not value:
        return False
    if value == "0":
        return True
    return value.isdigit() and value[0] != "0"


def process_input_line(phonebook: Phonebook, line: str) -> str:
    """Process one phonebook input line and return its exact output."""
    if not line.strip():
        return "ERROR MALFORMED"

    parts = line.split("|")
    command = parts[0]

    if command == "ADD":
        if len(parts) != 8:
            return "ERROR MALFORMED ADD"
        _, student_id, surname, given_name, occupation, country_code, area_code, local_number = parts
        contact = Contact(student_id, surname, given_name, occupation, country_code, area_code, local_number)
        error = validate_contact(contact)
        if error:
            return error
        return phonebook.add_contact(contact)

    elif command == "FIND":
        if len(parts) != 2:
            return "ERROR MALFORMED FIND"
        return phonebook.find_contact(parts[1])

    elif command == "FIND_SURNAME":
        if len(parts) != 2:
            return "ERROR MALFORMED FIND_SURNAME"
        return phonebook.find_by_surname(parts[1])

    elif command == "UPDATE":
        if len(parts) != 4:
            return "ERROR MALFORMED UPDATE"
        _, target_id, field, new_value = parts
        return phonebook.update_contact(target_id, field, new_value)

    elif command == "DELETE":
        if len(parts) != 2:
            return "ERROR MALFORMED DELETE"
        return phonebook.delete_contact(parts[1])

    elif command == "LIST":
        if len(parts) != 1:
            return "ERROR MALFORMED LIST"
        return phonebook.list_contacts()

    elif command == "COUNTRY":
        if len(parts) != 2 or not parts[1].strip():
            return "ERROR INVALID_VALUE COUNTRY_CODES"
        raw_codes = parts[1].split(",")
        if not raw_codes or any(c.strip() == "" for c in raw_codes):
            return "ERROR INVALID_VALUE COUNTRY_CODES"
        seen = set()
        unique_codes = []
        for code in raw_codes:
            code = code.strip()
            if not code:
                return "ERROR INVALID_VALUE COUNTRY_CODES"
            if code not in COUNTRY_CODES:
                return f"ERROR INVALID_COUNTRY {code}"
            if code not in seen:
                seen.add(code)
                unique_codes.append(code)
        return phonebook.filter_by_country(set(unique_codes))

    else:
        return f"ERROR UNKNOWN_COMMAND {command}"


def run_program(raw_input: str) -> str:
    """Process one complete ASEAN-PHONEBOOK 1.0 input."""
    lines = raw_input.replace("\r\n", "\n").split("\n")

    if not lines or lines[0].rstrip() != "ASEAN-PHONEBOOK 1.0":
        return "ERROR VERSION"

    if len(lines) < 2 or not is_canonical_count(lines[1].strip()):
        return "ERROR COMMAND_COUNT"

    count = int(lines[1].strip())
    if count > 200:
        return "ERROR COMMAND_COUNT"

    input_lines = lines[2:]
    # Filter trailing empty line from split but keep intentional empties
    if len(input_lines) < count:
        return "ERROR COMMAND_COUNT"

    phonebook = Phonebook()
    output_lines = []

    for i in range(count):
        line = input_lines[i].rstrip("\n").rstrip("\r")
        result = process_input_line(phonebook, line)
        output_lines.append(result)

    return "\n".join(output_lines)


def main() -> None:
    """Read standard input, run the phonebook program, and print its output."""
    output = run_program(sys.stdin.read())
    if output:
        print(output)


if __name__ == "__main__":
    main()
