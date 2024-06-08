class NotAuthorizedException(Exception):
    message = "Not Authorized"


class UserNotFoundException(Exception):
    message = "User not found"
