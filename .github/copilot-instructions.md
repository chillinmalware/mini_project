# Copilot instructions

## Project overview

This is a Python console application for managing ASEAN student/partner contacts. The
program reads the `ASEAN-PHONEBOOK 1.0` format from standard input, processes a fixed
number of command lines, and emits exact result lines. The four project modules are
intentionally separated:

- `constants.py` defines the country-code mapping and the supported `UPDATE` fields.
- `contact.py` owns the `Contact` value object, display/phone formatting, and field
  validation.
- `phonebook.py` owns `Node` and `Phonebook`, including all linked-list traversal,
  ordering, duplicate checks, and mutations.
- `main.py` owns input framing, command parsing, top-level validation, and delegation
  to `Phonebook`.

## Build, test, and lint commands

There is no build system or configured linter. Run the program with:

```bash
python main.py < input.txt
```

Run the complete preliminary suite (structure tests plus all public `.in`/`.out`
golden-file cases) with:

```bash
python public_tests/run_tests.py
```

Run one focused unit test with:

```bash
python -m unittest public_tests.test_structure.ContactTests.test_copy_with_update_does_not_mutate_original
```

To exercise one public I/O case manually:

```bash
python main.py < public_tests/cases/05_add_single.in
```

The public tests are development checks; instructor-only cases may also be used.

## Architecture and invariants

- Contacts are stored in a manually implemented singly linked list. `Phonebook.head`
  points to the first `Node`, each node has `contact` and `next`, and `size` must
  exactly match the number of nodes.
- The chain is always sorted by `Contact.sort_key()`: case-insensitive surname,
  case-insensitive given name, then the student ID. Insertions and updates must
  preserve this order without using Python `list`, `sort()`, or `sorted()`.
- `Phonebook` is the only layer that relinks nodes or changes `head`/`size`.
  `main.process_input_line` may parse and validate input, but must delegate mutations
  rather than manipulating the data structure directly.
- `Contact.copy_with_update()` must create a proposed contact without mutating the
  original. `UPDATE` validation and duplicate checks happen before committing any
  change; failed updates must leave both the contact and linked-list position
  unchanged. Changes to ID, surname, or given name may require detach/reinsert.
- Phone and identifier components remain strings so leading zeroes are preserved.
  Complete phone uniqueness uses the formatted country-area-local combination.

## Input and output contracts

- Preserve exact result strings and their ordering; public tests compare output against
  the checked-in `.out` files.
- Follow the specified validation precedence. For `ADD`, malformed field count is
  handled before field validation, and duplicate student ID is reported before a
  duplicate complete phone number. For `UPDATE`, a missing target is reported before
  validating the requested field.
- Country filtering accepts country codes from the command input and reports matching
  contacts in the existing linked-list order. Country names come from
  `constants.COUNTRY_CODES`; do not duplicate that mapping elsewhere.
- Keep supported update field names synchronized with `constants.UPDATE_FIELDS`.
- Treat blank and unknown input commands according to the existing `main.py` contract;
  do not introduce ad hoc output or exceptions for them.

## Repository workflow constraints

`HOW_TO_RUN_TESTS.txt` is the local submission guidance: read the project definition
when needed, use the public tests for confidence, and submit only the four required
Python modules rather than the `public_tests` directory.
