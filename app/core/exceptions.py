class UserNotFoundError(Exception):
    """
    Raised when user does not exists
    """
    pass

class UsernameAlreadyTakenError(Exception):
    """
    Raised when username already exists
    """
    pass


class InvalidImageTypeError(Exception):
    """
    Raised when Invalid image type found
    """
    pass

class FileTooLargeError(Exception):
    """
    Raised when file is too large
    """
    pass

class UserEmailAlreadyExists(Exception):
    """
    Raised when Invalid image type found
    """
    pass

class TokenNotCreated(Exception):
    """
    Raised when file is too large
    """
    pass
