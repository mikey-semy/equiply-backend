from .base import BaseAPIException, DatabaseError, ValueNotFoundError
from .auth import (
    AuthenticationError,
    InvalidCredentialsError,
    InvalidEmailFormatError,
    InvalidPasswordError,
    InvalidCurrentPasswordError,
    WeakPasswordError,
    TokenExpiredError,
    TokenInvalidError,
    TokenMissingError,
    TokenError
)
from .users import (
    UserCreationError,
    UserExistsError,
    ForbiddenError,
    UserNotFoundError
)

from .profile import (
    ProfileNotFoundError,
    InvalidFileTypeError,
    FileTooLargeError,
    StorageError
)
from .workspaces import (
    WorkspaceNotFoundError,
    WorkspaceMemberNotFoundError,
    WorkspaceAccessDeniedError,
    WorkspaceExistsError
)

__all__ = [
    "BaseAPIException",
    "DatabaseError",
    "ValueNotFoundError",
    "AuthenticationError",
    "InvalidCredentialsError",
    "InvalidEmailFormatError",
    "InvalidPasswordError",
    "InvalidCurrentPasswordError",
    "WeakPasswordError",
    "TokenInvalidError",
    "TokenMissingError",
    "TokenExpiredError",
    "TokenError",
    "UserExistsError",
    "ForbiddenError",
    "UserNotFoundError",
    "UserCreationError",
    "ProfileNotFoundError",
    "InvalidFileTypeError",
    "FileTooLargeError",
    "StorageError",
    "WorkspaceNotFoundError",
    "WorkspaceMemberNotFoundError",
    "WorkspaceAccessDeniedError",
    "WorkspaceExistsError"
]
