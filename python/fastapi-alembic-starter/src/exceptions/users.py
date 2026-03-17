from src.exceptions.base import StarterBaseException


class EmailAlreadyExistsError(StarterBaseException):
    def __init__(self, email: str):
        # Do not expose email!!!
        # The error message confirms to an unauthenticated caller that a specific email
        # address exists in the system. An attacker can enumerate the entire user base
        # by calling POST /v*/auth/register with a list of emails and watching for the
        # different error codes.
        # super().__init__(f"Email '{email}' already registered", "EMAIL_EXISTS")
        super().__init__("Email already registered", "EMAIL_EXISTS")


class InvalidCredentialsOrUserDisabledError(StarterBaseException):
    def __init__(self):
        super().__init__(
            "Invalid email or password or user disabled",
            "INVALID_CREDENTIALS_OR_USER_DISABLED",
        )


class UserNotFoundError(StarterBaseException):
    def __init__(self, user_id: int):
        # The user ID is already inside the JWT,
        # so this isn't a new leak for the owner of the token.
        # But if this error ever surfaces in a context where a third party can
        # trigger it, it leaks internal IDs.
        # Safe to generalize to "User not found".
        # super().__init__(f"User {user_id} not found", "USER_NOT_FOUND")
        super().__init__("User not found", "USER_NOT_FOUND")
