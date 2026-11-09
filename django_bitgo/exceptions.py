class BitGoException(Exception):
    """
    Raised for any failure talking to BitGo.

    For HTTP errors the BitGo error body is parsed when possible:

    - ``status_code``: HTTP status of the response
    - ``error_name``: BitGo's machine-readable error code (the ``name`` field)
    - ``request_id``: BitGo's ``requestId``, useful when contacting support
    - ``response_body``: the decoded JSON body (or ``None``)
    """

    def __init__(
        self,
        message: str = "",
        status_code: int = None,
        error_name: str = None,
        request_id: str = None,
        response_body=None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_name = error_name
        self.request_id = request_id
        self.response_body = response_body
