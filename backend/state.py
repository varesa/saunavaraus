import base64
import json
import re


class StateMissingException(Exception):
    pass


class State:
    email: str = ""

    def __init__(self, email: str):
        self.email = email

    def encode(self):
        b64encoded = base64.b64encode(json.dumps({
            "email": self.email
        }).encode())
        return "%%" + b64encoded.decode() + "%%"

    @staticmethod
    def from_str(input: str) -> "State":
        match = re.match("%%(.*)%%", input)
        if match:
            data = match.group(1)
            decoded = json.loads(base64.b64decode(data).decode())

            return State(email=decoded['email'])
        raise StateMissingException
