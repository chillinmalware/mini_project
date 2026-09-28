# contact.py
# Defines the Contact data class and all contact-level validation helpers.
# Contact is a pure data holder — it does NOT touch the linked list, read
# input lines, or print results. Those responsibilities live in phonebook.py
# and main.py respectively.

from __future__ import annotations

from constants import COUNTRY_CODES


class Contact:
    """Represent one contact stored by the ASEAN Phonebook."""

    def __init__(self,
        student_id: str,
        surname: str,
        given_name: str,
        occupation: str,
        country_code: str,
        area_code: str,
        local_number: str,) -> None:
        # All seven fields are stored as plain strings.
        # phone-related fields (country_code, area_code, local_number) stay as
        # strings deliberately so leading zeros are never lost (e.g. "03", "000111").
        self.student_id = student_id
        self.surname = surname
        self.given_name = given_name
        self.occupation = occupation
        self.country_code = country_code
        self.area_code = area_code
        self.local_number = local_number

    def phone_number(self) -> str:
        """Return the full phone number as '<country_code>-<area_code>-<local_number>'.

        This combined string is what the uniqueness check compares against so
        that two contacts with the same local number but different country/area
        codes are correctly treated as distinct.
        """
        return self.country_code + "-" + self.area_code + "-" + self.local_number

    def sort_key(self) -> tuple[str, str, str]:
        """Return the three-level sort tuple used for linked-list ordering.

        Sorting priority (all case-insensitive for name comparisons):
          1. surname.lower()    — primary key
          2. given_name.lower() — tiebreaker when surnames match
          3. student_id         — final tiebreaker; ensures a stable, unique order

        The original casing is never changed — .lower() is applied only here
        during comparison so display output keeps the user-supplied spelling.
        """
        return self.surname.lower(), self.given_name.lower(), self.student_id

    def get_field(self, field: str) -> str:
        """Return the current value of one supported UPDATE field.

        Used by Phonebook.update_contact() to capture the old value before
        applying a change, so the OK UPDATE response can show 'old -> new'.
        The caller is responsible for ensuring field is a valid UPDATE_FIELDS key.
        """
        mapping = {
            "ID": self.student_id,
            "SURNAME": self.surname,
            "GIVEN_NAME": self.given_name,
            "OCCUPATION": self.occupation,
            "COUNTRY_CODE": self.country_code,
            "AREA_CODE": self.area_code,
            "LOCAL_NUMBER": self.local_number,
        }
        return mapping[field]

    def copy_with_update(self, field: str, new_value: str) -> Contact:
        """Return a new Contact with exactly one field replaced by new_value.

        The current Contact is never mutated. The caller validates and
        duplicate-checks the returned candidate before committing any change
        to the linked list, so a failed UPDATE leaves the phonebook untouched.
        """
        return Contact(
            student_id=new_value if field == "ID" else self.student_id,
            surname=new_value if field == "SURNAME" else self.surname,
            given_name=new_value if field == "GIVEN_NAME" else self.given_name,
            occupation=new_value if field == "OCCUPATION" else self.occupation,
            country_code=new_value if field == "COUNTRY_CODE" else self.country_code,
            area_code=new_value if field == "AREA_CODE" else self.area_code,
            local_number=new_value if field == "LOCAL_NUMBER" else self.local_number,
        )

    def __str__(self) -> str:
        """Return the exact readable contact format required by the project.

        Format:
            <student_id> - <surname>, <given_name> - <occupation> - <country_name> - <phone>

        Example:
            S-001 - Abad, Lio - Analyst - Indonesia - 62-021-000777
        """
        # Resolve the human-readable country name from the calling code.
        country_name = COUNTRY_CODES[self.country_code]
        return (
            f"{self.student_id} - {self.surname}, {self.given_name} - "
            f"{self.occupation} - {country_name} - {self.phone_number()}"
        )


# ---------------------------------------------------------------------------
# Field-level validation helpers
# Each function focuses on a single field and returns a plain bool so the
# caller (validate_contact) can compose them in whatever order the spec requires.
# ---------------------------------------------------------------------------

def is_valid_student_id(value: str) -> bool:
    """Return True when value follows the published student-ID rules.

    Rules:
      - 1 to 20 characters
      - First character must be an uppercase letter (A-Z) or a digit (0-9)
      - Remaining characters may be uppercase letters, digits, or hyphens (-)
    """
    if not value or len(value) > 20:
        return False
    # First character: uppercase letter or digit only
    if not (value[0].isupper() or value[0].isdigit()):
        return False
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
    return all(c in allowed for c in value)


def is_valid_name(value: str) -> bool:
    """Return True when value is a valid surname or given name.

    Rules:
      - 1 to 40 characters
      - No leading or trailing space
      - Allowed characters: letters (A-Z, a-z), space, apostrophe ('), hyphen (-)
    """
    if not value or len(value) > 40:
        return False
    # Leading/trailing spaces are forbidden even though internal spaces are allowed.
    if value[0] == ' ' or value[-1] == ' ':
        return False
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '-")
    return all(c in allowed for c in value)


def is_valid_occupation(value: str) -> bool:
    """Return True when value follows the published occupation rules.

    Rules:
      - 1 to 60 characters
      - No leading or trailing space
      - Allowed characters: letters, digits, space, period (.), apostrophe ('),
        hyphen (-), and forward slash (/)
    """
    if not value or len(value) > 60:
        return False
    if value[0] == ' ' or value[-1] == ' ':
        return False
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .'/-")
    return all(c in allowed for c in value)


def is_valid_area_code(value: str) -> bool:
    """Return True for an area code containing 1 to 6 digits.

    Digits only — no letters, no hyphens. Leading zeros are valid (e.g. "02").
    """
    return bool(value) and len(value) <= 6 and value.isdigit()


def is_valid_local_number(value: str) -> bool:
    """Return True for a local number containing 3 to 12 digits.

    Digits only. Leading zeros are valid and must be preserved in storage.
    """
    return bool(value) and 3 <= len(value) <= 12 and value.isdigit()


def validate_contact(contact: Contact) -> str | None:
    """Return the first required validation error string, or None when valid.

    Checks are applied left-to-right in the field order defined by the project
    spec. Returning on the first failure ensures only one error is ever reported
    for a single bad contact, consistent with the project's single-error rule.

    Error strings match the exact output formats required:
      ERROR INVALID_VALUE <FIELD>   — for most bad field values
      ERROR INVALID_COUNTRY <code>  — specifically for an unknown country code
    """
    if not is_valid_student_id(contact.student_id):
        return f"ERROR INVALID_VALUE STUDENT_ID"
    if not is_valid_name(contact.surname):
        return f"ERROR INVALID_VALUE SURNAME"
    if not is_valid_name(contact.given_name):
        return f"ERROR INVALID_VALUE GIVEN_NAME"
    if not is_valid_occupation(contact.occupation):
        return f"ERROR INVALID_VALUE OCCUPATION"
    # Country code uses a different error token (INVALID_COUNTRY, not INVALID_VALUE).
    if contact.country_code not in COUNTRY_CODES:
        return f"ERROR INVALID_COUNTRY {contact.country_code}"
    if not is_valid_area_code(contact.area_code):
        return f"ERROR INVALID_VALUE AREA_CODE"
    if not is_valid_local_number(contact.local_number):
        return f"ERROR INVALID_VALUE LOCAL_NUMBER"
    return None  # All fields valid
