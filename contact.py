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

        self.student_id = student_id
        self.surname = surname
        self.given_name = given_name
        self.occupation = occupation
        self.country_code = country_code
        self.area_code = area_code
        self.local_number = local_number

    def phone_number(self) -> str:
        return self.country_code + "-" + self.area_code + "-" + self.local_number

    def sort_key(self) -> tuple[str, str, str]:
        return self.surname.lower(), self.given_name.lower(), self.student_id

    def get_field(self, field: str) -> str:
        """Return the current value of one supported UPDATE field."""
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
        """Return a proposed Contact containing one field change.

        Do not modify the current Contact. The proposed Contact is checked
        first so a failed UPDATE can leave the linked list unchanged.
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
        """Return the exact readable contact format required by the project."""
        country_name = COUNTRY_CODES[self.country_code]
        return (
            f"{self.student_id} - {self.surname}, {self.given_name} - "
            f"{self.occupation} - {country_name} - {self.phone_number()}"
        )


def is_valid_student_id(value: str) -> bool:
    """Return True when value follows the published student-ID rules."""
    if not value or len(value) > 20:
        return False
    if not (value[0].isupper() or value[0].isdigit()):
        return False
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
    return all(c in allowed for c in value)


def is_valid_name(value: str) -> bool:
    """Return True when value is a valid surname or given name."""
    if not value or len(value) > 40:
        return False
    if value[0] == ' ' or value[-1] == ' ':
        return False
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '-")
    return all(c in allowed for c in value)


def is_valid_occupation(value: str) -> bool:
    """Return True when value follows the published occupation rules."""
    if not value or len(value) > 60:
        return False
    if value[0] == ' ' or value[-1] == ' ':
        return False
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .'/-")
    return all(c in allowed for c in value)


def is_valid_area_code(value: str) -> bool:
    """Return True for an area code containing 1 to 6 digits."""
    return bool(value) and len(value) <= 6 and value.isdigit()


def is_valid_local_number(value: str) -> bool:
    """Return True for a local number containing 3 to 12 digits."""
    return bool(value) and 3 <= len(value) <= 12 and value.isdigit()


def validate_contact(contact: Contact) -> str | None:
    """Return the first required validation error, or None when valid.

    Check fields from left to right using the order published in the project
    definition. COUNTRY_CODE uses ERROR INVALID_COUNTRY <value>.
    """
    if not is_valid_student_id(contact.student_id):
        return f"ERROR INVALID_VALUE STUDENT_ID"
    if not is_valid_name(contact.surname):
        return f"ERROR INVALID_VALUE SURNAME"
    if not is_valid_name(contact.given_name):
        return f"ERROR INVALID_VALUE GIVEN_NAME"
    if not is_valid_occupation(contact.occupation):
        return f"ERROR INVALID_VALUE OCCUPATION"
    if contact.country_code not in COUNTRY_CODES:
        return f"ERROR INVALID_COUNTRY {contact.country_code}"
    if not is_valid_area_code(contact.area_code):
        return f"ERROR INVALID_VALUE AREA_CODE"
    if not is_valid_local_number(contact.local_number):
        return f"ERROR INVALID_VALUE LOCAL_NUMBER"
    return None
