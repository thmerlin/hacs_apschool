"""Helpere class
"""

import datetime
import json


class UnreadMessage:
    """UnreadMessage class"""

    id: int
    title: str
    create_at: datetime.datetime

    def __init__(self, json_item) -> None:
        self.id = json_item.get("id")
        self.title = json_item.get("titre")
        self.create_at = json_item.get("dateCreation")


class UserData:
    """UserData class"""

    user_id: int
    firstname: str
    lastname: str
    school_class: str
    balance: float | None = None
    unread_messages: list[UnreadMessage] | None = None
    due_amount: float = 0.0

    def __init__(
        self,
        user_id: int,
        firstname: str,
        lastname: str,
        school_class: str,
        balance: float | None,
        unread_messages: list[UnreadMessage] | None,
        due_amount: float,
    ) -> None:
        self.user_id = user_id
        self.firstname = firstname
        self.lastname = lastname
        self.school_class = school_class
        self.balance = balance
        self.unread_messages = unread_messages
        self.due_amount = due_amount

    def to_json(self):
        """Output the object as a inline JSON"""
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
        )
