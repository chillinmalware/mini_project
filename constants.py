# constants.py
# Holds all fixed/immutable values used across the ASEAN Phonebook project.
# This file is intentionally kept separate so other modules can import from
# one authoritative source instead of defining their own copies.

from typing import Final


# Maps each ASEAN country's international calling code (as a string) to its
# display name. Stored as strings — not integers — so that leading zeros in
# area codes and local numbers are preserved throughout the program.
# Used by:
#   - contact.py  → Contact.__str__() to resolve the country name for display
#   - contact.py  → validate_contact() to check whether a country_code is valid
#   - main.py     → COUNTRY command handler to validate requested filter codes
COUNTRY_CODES: Final[dict[str, str]] = {
    "60": "Malaysia",
    "62": "Indonesia",
    "63": "Philippines",
    "65": "Singapore",
    "66": "Thailand",
    "84": "Vietnam",
    "95": "Myanmar",
    "670": "Timor-Leste",
    "673": "Brunei Darussalam",
    "855": "Cambodia",
    "856": "Lao PDR",
}

# The complete set of field names that the UPDATE command accepts.
# Using a frozenset makes membership checks O(1) and prevents accidental
# mutation. Any field name not in this set is rejected with ERROR INVALID_FIELD.
UPDATE_FIELDS: Final[frozenset[str]] = frozenset({
    "ID",
    "SURNAME",
    "GIVEN_NAME",
    "OCCUPATION",
    "COUNTRY_CODE",
    "AREA_CODE",
    "LOCAL_NUMBER",
})
