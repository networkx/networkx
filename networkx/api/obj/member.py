from graphspace_python.api.obj.response_object import ResponseObject

class Member(ResponseObject):
    """Member object class.

    Encapsulates details of a group member received in response.

    Attributes:
        id (int): Id of group member.
        email (str): Email of group member.
        created_at (str): Timestamp of member creation.
        updated_at (str): Timestamp of member updation.
    """

    _fields = [
        'id',
        'email',
        'created_at',
        'updated_at'
    ]

    def __init__(self, response):
        """Construct a new 'Member' object having the attributes specified in '_fields'

        Args:
            response (dict): Json representation of group member details.
        """
        super(Member, self).__init__(response)
