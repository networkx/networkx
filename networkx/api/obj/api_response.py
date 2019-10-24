from graphspace_python.api.obj.graph import Graph
from graphspace_python.api.obj.layout import Layout
from graphspace_python.api.obj.group import Group
from graphspace_python.api.obj.member import Member
from graphspace_python.api.obj.response_object import ResponseObject

class APIResponse(ResponseObject):
    """APIResponse class.

    Encapsulates the response from API calls.
    """

    _fields = [
        'total'
    ]

    def __init__(self, response_type, response):
        """Construct a new 'APIResponse' object.

        Calls '_parse' method of parent class 'ResponseObject' to parse the response.

        Args:
            response_type (str): Type of response received from API call.
            response (dict): Response dict received from API call.
        """
        super(APIResponse, self).__init__(response)
        if response_type == 'graph':
            self._parse(response_type, Graph, response)
        elif response_type == 'layout':
            self._parse(response_type, Layout, response)
        elif response_type == 'group':
            self._parse(response_type, Group, response)
        elif response_type == 'member':
            self._parse(response_type, Member, response)
