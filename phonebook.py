# phonebook.py
# Defines the Node and Phonebook classes that implement the singly linked list
# required by the ASEAN Phonebook project.
#
# Design constraints enforced here:
#   - No Python list is used as the primary contact store.
#   - sort() and sorted() are never called.
#   - Sorted order is maintained through manual linked-list insertion/reinsertion.
#   - Every structural change (insert, detach) goes through Phonebook methods;
#     external code (main.py) never touches node.next or self.head directly.

from __future__ import annotations

from constants import UPDATE_FIELDS
from contact import Contact, validate_contact


class Node:
    """Store one Contact and a reference to the next node.

    A Node is a single position in the singly linked list. It knows only about
    its own contact and whatever node follows it. Searching, sorting, and list
    maintenance are the Phonebook's responsibility, not Node's.
    """

    def __init__(self, contact: Contact, next_node: Node | None = None) -> None:
        self.contact = contact    # The data payload for this list position
        self.next = next_node     # Link to the next Node, or None if this is the tail


class Phonebook:
    """Manage contacts through a manually implemented singly linked list.

    Public interface (called by main.py):
        add_contact      — insert a validated Contact in sorted order
        find_contact     — look up a contact by student_id
        find_by_surname  — list all contacts matching a surname (case-insensitive)
        update_contact   — change one field on an existing contact
        delete_contact   — remove a contact by student_id
        list_contacts    — print every contact in linked-list order
        filter_by_country — print contacts whose country_code is in a given set

    Internal helpers (prefixed with _):
        _find_node_by_id   — linear scan returning a Node reference
        _student_id_exists — uniqueness check for student IDs
        _phone_exists      — uniqueness check for complete phone numbers
        _insert_node_sorted — insert a detached Node into its correct position
        _detach_node       — unlink and return a Node without destroying it
    """

    def __init__(self) -> None:
        """Create an empty phonebook with head = None and size = 0."""
        self.head: Node | None = None  # Entry point to the linked list
        self.size: int = 0             # Tracks node count; must stay in sync with actual list length

    # ------------------------------------------------------------------
    # Private helpers — list traversal and structural operations
    # ------------------------------------------------------------------

    def _find_node_by_id(self, student_id: str) -> Node | None:
        """Return the node containing student_id, or None when not found.

        Linear O(n) scan from head. Used by find_contact, update_contact,
        and delete_contact to locate a specific node before acting on it.
        """
        current = self.head
        while current is not None:
            if current.contact.student_id == student_id:
                return current
            current = current.next
        return None

    def _student_id_exists(
        self,
        student_id: str,
        excluded_student_id: str | None = None,
    ) -> bool:
        """Return True when another contact already uses student_id.

        excluded_student_id lets update_contact skip the contact being edited,
        so updating a contact's own ID to the same value doesn't false-positive.
        """
        current = self.head
        while current is not None:
            if current.contact.student_id == student_id:
                # If an exclusion is set, skip the excluded contact's own entry.
                if excluded_student_id is None or student_id != excluded_student_id:
                    return True
            current = current.next
        return False

    def _phone_exists(
        self,
        phone_number: str,
        excluded_student_id: str | None = None,
    ) -> bool:
        """Return True when another contact already uses phone_number.

        excluded_student_id works the same as in _student_id_exists — it lets
        update_contact ignore the contact being edited when checking for phone
        number duplicates across the remaining contacts.
        """
        current = self.head
        while current is not None:
            if current.contact.phone_number() == phone_number:
                # Skip the contact we're currently updating so it doesn't
                # conflict with its own existing phone number.
                if excluded_student_id is None or current.contact.student_id != excluded_student_id:
                    return True
            current = current.next
        return False

    def _insert_node_sorted(self, node: Node) -> None:
        """Insert node into its correct sorted position in the linked list.

        Sort order is determined by Contact.sort_key():
            (surname.lower(), given_name.lower(), student_id)

        Handles all four structural cases:
          1. Empty list          → node becomes head
          2. Before current head → node becomes the new head
          3. Middle insertion    → splice between two existing nodes
          4. Tail insertion      → append after the last node (handled by case 3's loop exit)

        size is incremented here so callers don't need to track it manually.
        The node's .next pointer is reset to None at the start so that a
        previously detached node can be reinserted cleanly.
        """
        node.next = None  # Ensure a reinserted node doesn't carry stale links

        # Case 1: list is empty
        if self.head is None:
            self.head = node
            self.size += 1
            return

        # Case 2: node belongs before the current head
        if node.contact.sort_key() <= self.head.contact.sort_key():
            node.next = self.head
            self.head = node
            self.size += 1
            return

        # Cases 3 & 4: find the last node whose sort_key is <= the new node's
        current = self.head
        while current.next is not None and current.next.contact.sort_key() <= node.contact.sort_key():
            current = current.next
        # Splice: current -> node -> (old current.next)
        node.next = current.next
        current.next = node
        self.size += 1

    def _detach_node(self, student_id: str) -> Node | None:
        """Unlink and return one node without destroying it, or None if missing.

        The returned node has its .next cleared so it can be safely reinserted
        (by _insert_node_sorted) or discarded (by delete_contact).

        Handles all structural cases:
          - Empty list             → returns None immediately
          - Removing head          → advances self.head to head.next
          - Removing middle node   → bridges predecessor.next over the target
          - Removing tail node     → predecessor.next becomes None

        size is decremented only when a node is actually removed.
        """
        if self.head is None:
            return None

        # Special case: the target is the head node
        if self.head.contact.student_id == student_id:
            node = self.head
            self.head = self.head.next  # Advance head past the removed node
            node.next = None            # Disconnect the removed node from the list
            self.size -= 1
            return node

        # General case: scan for the node preceding the target
        current = self.head
        while current.next is not None:
            if current.next.contact.student_id == student_id:
                node = current.next
                current.next = node.next  # Bridge over the removed node
                node.next = None          # Isolate the removed node
                self.size -= 1
                return node
            current = current.next

        return None  # student_id not found anywhere in the list

    # ------------------------------------------------------------------
    # Public operations — called by main.py's input processor
    # ------------------------------------------------------------------

    def add_contact(self, contact: Contact) -> str:
        """Validate uniqueness, insert contact in sorted order, and return the result line.

        Duplicate checks run before insertion so the list stays unchanged on error.
        Check order (per spec): duplicate ID first, then duplicate phone.
        """
        # Reject if the student ID is already taken by another contact
        if self._student_id_exists(contact.student_id):
            return f"ERROR DUPLICATE_ID {contact.student_id}"
        # Reject if the complete phone number is already in use
        if self._phone_exists(contact.phone_number()):
            return f"ERROR DUPLICATE_PHONE {contact.phone_number()}"
        # Both checks passed — insert into the sorted list
        self._insert_node_sorted(Node(contact))
        return f"OK ADD {contact.student_id}"

    def find_contact(self, student_id: str) -> str:
        """Return the exact FOUND or NOT_FOUND output for student_id."""
        node = self._find_node_by_id(student_id)
        if node is None:
            return f"ERROR NOT_FOUND {student_id}"
        # Contact.__str__() produces the full formatted contact line
        return f"FOUND | {node.contact}"

    def find_by_surname(self, surname: str) -> str:
        """Return MATCHES and CONTACT lines in current linked-list order.

        Matching is case-insensitive (both sides lowercased for comparison).
        Results are printed in whatever order they appear in the linked list —
        no additional sorting is performed here.
        """
        lines = []
        current = self.head
        while current is not None:
            if current.contact.surname.lower() == surname.lower():
                lines.append(f"CONTACT | {current.contact}")
            current = current.next
        # Header line always appears, even when there are zero matches
        result = [f"MATCHES {len(lines)}"]
        result.extend(lines)
        return "\n".join(result)

    def update_contact(
        self,
        target_student_id: str,
        field: str,
        new_value: str,
    ) -> str:
        """Validate and apply one complete contact update.

        Update order (per spec):
          1. Confirm the target contact exists.
          2. Confirm the field name is valid.
          3. Build a candidate Contact with the proposed change.
          4. Validate the candidate's field values.
          5. Check the candidate for duplicate ID / phone (excluding self).
          6. Only if all checks pass: apply the change to the linked list.

        If ID, SURNAME, or GIVEN_NAME changes, the contact's sort position may
        change, so it is detached and reinserted rather than edited in place.
        All other fields are updated directly on the existing node's contact.

        A failed update at any step leaves the phonebook completely unchanged.
        """
        node = self._find_node_by_id(target_student_id)
        if node is None:
            return f"ERROR NOT_FOUND {target_student_id}"

        # Reject unknown field names before touching anything
        if field not in UPDATE_FIELDS:
            return f"ERROR INVALID_FIELD {field}"

        # Capture the current value for the success response line
        old_value = node.contact.get_field(field)

        # Build a candidate contact with the proposed single-field change
        candidate = node.contact.copy_with_update(field, new_value)

        # Validate all fields of the candidate (not just the changed one)
        error = validate_contact(candidate)
        if error:
            return error

        # Duplicate ID check — only needed when the ID is actually changing
        if field == "ID" and new_value != target_student_id:
            if self._student_id_exists(new_value, excluded_student_id=target_student_id):
                return f"ERROR DUPLICATE_ID {new_value}"

        # Duplicate phone check — any phone-component field change could create a conflict
        if field in ("COUNTRY_CODE", "AREA_CODE", "LOCAL_NUMBER"):
            if self._phone_exists(candidate.phone_number(), excluded_student_id=target_student_id):
                return f"ERROR DUPLICATE_PHONE {candidate.phone_number()}"

        # All checks passed — apply the update
        if field in ("ID", "SURNAME", "GIVEN_NAME"):
            # Sort position may have changed: detach the old node and reinsert the candidate
            self._detach_node(target_student_id)
            new_node = Node(candidate)
            self._insert_node_sorted(new_node)
        else:
            # Sort position is unaffected: update the contact in place
            node.contact = candidate

        return f"OK UPDATE {field} | {old_value} -> {new_value}"

    def delete_contact(self, student_id: str) -> str:
        """Unlink the contact with student_id and return the result line.

        _detach_node handles all structural cases (head, middle, tail, only node).
        size is updated inside _detach_node.
        """
        node = self._detach_node(student_id)
        if node is None:
            return f"ERROR NOT_FOUND {student_id}"
        return f"OK DELETE {student_id}"

    def list_contacts(self) -> str:
        """Return LIST followed by one CONTACT line per entry in linked-list order.

        The header always shows the current size. When the list is empty, only
        'LIST 0' is printed with no CONTACT lines following it.
        """
        lines = [f"LIST {self.size}"]
        current = self.head
        while current is not None:
            lines.append(f"CONTACT | {current.contact}")
            current = current.next
        return "\n".join(lines)

    def filter_by_country(self, country_codes: set[str]) -> str:
        """Return COUNTRY_MATCHES and matching CONTACT lines in list order.

        country_codes is a set of validated calling code strings (e.g. {"63", "60"}).
        Contacts are printed in global linked-list order, not grouped by country.
        The caller (main.py) is responsible for deduplicating and validating the
        incoming codes before calling this method.
        """
        lines = []
        current = self.head
        while current is not None:
            if current.contact.country_code in country_codes:
                lines.append(f"CONTACT | {current.contact}")
            current = current.next
        result = [f"COUNTRY_MATCHES {len(lines)}"]
        result.extend(lines)
        return "\n".join(result)
