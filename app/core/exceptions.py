class UserNotFoundError(Exception):
    """
    Raised when user does not exists
    """
    pass

class UserEmailNotFound(Exception):
    """
    Raised when user email does not exists
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

class WrongPassword(Exception):
    """
    Raised when file is too large
    """
    pass


class NoTestCasesFound(Exception):
    """
    No test cases fetched or found
    """
    pass

class NoLanguageFound(Exception):
    """
    No programming language found
    """
    pass


class FailedPistonExecution(Exception):
    """
    failed code exectution
    """
    pass


