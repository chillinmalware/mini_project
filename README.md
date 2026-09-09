# ASEAN Phonebook — Project 0

A console-based phonebook application built in Python for managing student and partner contacts from Southeast Asian countries. Built as a university project for a BSIT course.

## What it does

Stores contacts in a manually implemented singly linked list (no Python lists, no sort/sorted). Supports adding, finding, updating, deleting, and listing contacts — all while keeping them sorted at all times.

## Commands

| Command | Description |
|---|---|
| `ADD` | Add a new contact |
| `FIND` | Find a contact by student ID |
| `FIND_SURNAME` | Find contacts by surname (case-insensitive) |
| `UPDATE` | Update a contact field |
| `DELETE` | Delete a contact |
| `LIST` | List all contacts in sorted order |
| `COUNTRY` | Filter contacts by country code |

## How to run

```bash
python main.py < input.txt
```

Or pipe input directly:

```bash
echo "ASEAN-PHONEBOOK 1.0
2
ADD|S-001|Abad|Lio|Analyst|62|021|000777
LIST" | python main.py
```

## How to run tests

```bash
python public_tests/run_tests.py
```

## Project structure

```
contact.py      — Contact class and validation helpers
phonebook.py    — Node and Phonebook (linked list)
main.py         — Input parsing and program entry point
constants.py    — Country codes and update field names
```

## Supported countries

Malaysia, Indonesia, Philippines, Singapore, Thailand, Vietnam, Myanmar, Timor-Leste, Brunei Darussalam, Cambodia, Lao PDR
