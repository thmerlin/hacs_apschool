"""Helpere class
"""

import datetime


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

    id: int
    firstname: str
    lastname: str
    school_class: str
    balance: float | None = None
    unread_messages: list[UnreadMessage] | None = None

    def __init__(
        self,
        id: int,
        firstname: str,
        lastname: str,
        school_class: str,
        balance: float | None,
        unread_messages: list[UnreadMessage] | None,
    ) -> None:
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.school_class = school_class
        self.balance = balance
        self.unread_messages = unread_messages
