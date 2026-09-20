from __future__ import annotations

from constants import UPDATE_FIELDS
from contact import Contact, validate_contact


class Node:
    """Store one Contact and a reference to the next node."""

    def __init__(self, contact: Contact, next_node: Node | None = None) -> None:
        self.contact = contact
        self.next = next_node


class Phonebook:
    """Manage contacts through a manually implemented singly linked list."""

    def __init__(self) -> None:
        """Create an empty phonebook with head = None and size = 0."""
        self.head: Node | None = None
        self.size: int = 0

    def _find_node_by_id(self, student_id: str) -> Node | None:
        """Return the node containing student_id, or None when not found."""
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
        """Return True when another contact already uses student_id."""
        current = self.head
        while current is not None:
            if current.contact.student_id == student_id:
                if excluded_student_id is None or student_id != excluded_student_id:
                    return True
            current = current.next
        return False

    def _phone_exists(
        self,
        phone_number: str,
        excluded_student_id: str | None = None,
    ) -> bool:
        """Return True when another contact already uses phone_number."""
        current = self.head
        while current is not None:
            if current.contact.phone_number() == phone_number:
                if excluded_student_id is None or current.contact.student_id != excluded_student_id:
                    return True
            current = current.next
        return False

    def _insert_node_sorted(self, node: Node) -> None:
        """Insert node into its correct linked-list position."""
        node.next = None
        if self.head is None:
            self.head = node
            self.size += 1
            return
        # Insert before head
        if node.contact.sort_key() <= self.head.contact.sort_key():
            node.next = self.head
            self.head = node
            self.size += 1
            return
        # Find insertion point
        current = self.head
        while current.next is not None and current.next.contact.sort_key() <= node.contact.sort_key():
            current = current.next
        node.next = current.next
        current.next = node
        self.size += 1

    def _detach_node(self, student_id: str) -> Node | None:
        """Unlink and return one node, or return None when it is missing."""
        if self.head is None:
            return None
        # Removing head
        if self.head.contact.student_id == student_id:
            node = self.head
            self.head = self.head.next
            node.next = None
            self.size -= 1
            return node
        current = self.head
        while current.next is not None:
            if current.next.contact.student_id == student_id:
                node = current.next
                current.next = node.next
                node.next = None
                self.size -= 1
                return node
            current = current.next
        return None

    def add_contact(self, contact: Contact) -> str:
        """Add one validated Contact and return the exact ADD result line."""
        if self._student_id_exists(contact.student_id):
            return f"ERROR DUPLICATE_ID {contact.student_id}"
        if self._phone_exists(contact.phone_number()):
            return f"ERROR DUPLICATE_PHONE {contact.phone_number()}"
        self._insert_node_sorted(Node(contact))
        return f"OK ADD {contact.student_id}"

    def find_contact(self, student_id: str) -> str:
        """Return the exact FOUND or NOT_FOUND output for student_id."""
        node = self._find_node_by_id(student_id)
        if node is None:
            return f"ERROR NOT_FOUND {student_id}"
        return f"FOUND | {node.contact}"

    def find_by_surname(self, surname: str) -> str:
        """Return MATCHES and CONTACT lines in current linked-list order."""
        lines = []
        current = self.head
        while current is not None:
            if current.contact.surname.lower() == surname.lower():
                lines.append(f"CONTACT | {current.contact}")
            current = current.next
        result = [f"MATCHES {len(lines)}"]
        result.extend(lines)
        return "\n".join(result)

    def update_contact(
        self,
        target_student_id: str,
        field: str,
        new_value: str,
    ) -> str:
        """Validate and apply one complete contact update."""
        node = self._find_node_by_id(target_student_id)
        if node is None:
            return f"ERROR NOT_FOUND {target_student_id}"

        if field not in UPDATE_FIELDS:
            return f"ERROR INVALID_FIELD {field}"

        old_value = node.contact.get_field(field)
        candidate = node.contact.copy_with_update(field, new_value)

        # Validate the proposed contact
        error = validate_contact(candidate)
        if error:
            return error

        # Check duplicates (excluding the contact being updated)
        if field == "ID" and new_value != target_student_id:
            if self._student_id_exists(new_value, excluded_student_id=target_student_id):
                return f"ERROR DUPLICATE_ID {new_value}"

        if field in ("COUNTRY_CODE", "AREA_CODE", "LOCAL_NUMBER"):
            if self._phone_exists(candidate.phone_number(), excluded_student_id=target_student_id):
                return f"ERROR DUPLICATE_PHONE {candidate.phone_number()}"

        # Apply the update
        needs_reinsert = field in ("ID", "SURNAME", "GIVEN_NAME")
        if needs_reinsert:
            self._detach_node(target_student_id)
            new_node = Node(candidate)
            self._insert_node_sorted(new_node)
        else:
            node.contact = candidate

        return f"OK UPDATE {field} | {old_value} -> {new_value}"

    def delete_contact(self, student_id: str) -> str:
        """Delete one contact and return the exact DELETE result line."""
        node = self._detach_node(student_id)
        if node is None:
            return f"ERROR NOT_FOUND {student_id}"
        return f"OK DELETE {student_id}"

    def list_contacts(self) -> str:
        """Return LIST followed by CONTACT lines in linked-list order."""
        lines = [f"LIST {self.size}"]
        current = self.head
        while current is not None:
            lines.append(f"CONTACT | {current.contact}")
            current = current.next
        return "\n".join(lines)

    def filter_by_country(self, country_codes: set[str]) -> str:
        """Return COUNTRY_MATCHES and matching CONTACT lines in list order."""
        lines = []
        current = self.head
        while current is not None:
            if current.contact.country_code in country_codes:
                lines.append(f"CONTACT | {current.contact}")
            current = current.next
        result = [f"COUNTRY_MATCHES {len(lines)}"]
        result.extend(lines)
        return "\n".join(result)
