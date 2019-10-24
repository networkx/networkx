class GraphSpaceError(Exception):
    """GraphSpaceError class.

    Base error class for the GraphSpace HTTP errors.

    Attributes:
        status_code (int): HTTP error status code.
        reason (str): Reason of HTTP error.
        error_code (int): Error code received from GraphSpace.
        error_message (str): Error message received from GraphSpace.
    """

    def __init__(self, status_code, reason, response):
        """Construct a new 'GraphSpaceError' object.

        Args:
            status_code (int): Status Code of the HTTP error.
            reason (str): Reason of HTTP error.
            response (dict): Response dict having error details from the API call.
        """
        self.status_code = status_code
        self.reason = reason
        self.error_code = response['error_code']
        self.error_message = response['error_message']

    def __str__(self):
        """Prints the error message when exception occurs.
        """
        return self.error_message

class UserAlreadyExists(GraphSpaceError):
    pass

class BadRequest(GraphSpaceError):
    pass

class UserNotAuthorised(GraphSpaceError):
    pass

class UserNotAuthenticated(GraphSpaceError):
    pass

class LayoutNameAlreadyExists(GraphSpaceError):
    pass

class ErrorHandler(object):
    """ErrorHandler class.

    Exception handling class for GraphSpace API's HTTP errors.
    """

    _error_map = {
        1000: UserAlreadyExists,
        1002: BadRequest,
        1004: UserNotAuthorised,
        1005: UserNotAuthenticated,
        1014: LayoutNameAlreadyExists
    }

    def raise_error(self, error, response):
        """Raises exception based on the 'error_code' received in response when
        any HTTP error occurs in API call.

        Args:
            error (object): HTTPError object.
            response (dict): Response dict having error details from the API call.

        Raises:
            GraphSpaceError: If an error response is received from the API call,
                it raises any one of the GraphSpaceError depending upon the error
                code.
        """
        try:
            raise self._error_map[response['error_code']](
                error.response.status_code,
                error.response.reason,
                response
            )
        except KeyError:
            raise error
