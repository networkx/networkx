from graphspace_python.api.obj.response_object import ResponseObject
from graphspace_python.graphs.classes.gsgroup import GSGroup

class Group(ResponseObject, GSGroup):
    """Group object class.

    Encapsulates details of a group received in response.

    Attributes:
        id (int): Id of group.
        name (str): Name of group.
        owner_email (str): Email of owner of group.
        description (str): Description of group.
        total_graphs (int): Total graphs of group.
        total_members (int): Total members of group.
        invite_code (str): Invite code for the group.
        created_at (str): Timestamp of group creation.
        updated_at (str): Timestamp of group updation.
        url (str): URL of group on GraphSpace.
        invite_link (str): Invite link for joining the group.
    """

    _fields = [
        'id',
        'name',
        'owner_email',
        'description',
        'created_at',
        'updated_at',
        'total_graphs',
        'total_members',
        'invite_code'
    ]

    def __init__(self, response):
        """Construct a new 'Group' object having the attributes specified in '_fields'

        Args:
            response (dict): Json representation of group details.
        """
        GSGroup.__init__(self)
        ResponseObject.__init__(self, response)
        self.url = 'http://graphspace.org/groups/' + str(self.id)
        self.invite_link = self.url + '/join/?code=' + self.invite_code
