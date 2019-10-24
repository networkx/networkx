import json
from graphspace_python.api.obj.response_object import ResponseObject
from graphspace_python.graphs.classes.gslayout import GSLayout

class Layout(ResponseObject, GSLayout):
    """Layout object class.

    Encapsulates details of a layout received in response.

    Attributes:
        id (int): Id of layout.
        graph_id (int): Id of graph to which the layout belongs.
        name (str): Name of layout.
        owner_email (str): Email of owner of layout.
        is_shared (int): Sharing status of layout. Has value 0 if layout is private, 1 if layout is shared.
        style_json (dict): Json representation for layout style.
        positions_json (dict): Json representation for layout node positions.
        created_at (str): Timestamp of layout creation.
        updated_at (str): Timestamp of layout updation.
        url (str): URL of graph layout on GraphSpace.
    """

    _fields = [
        'id',
        'graph_id',
        'name',
        'owner_email',
        'is_shared',
        'created_at',
        'updated_at',
        'style_json',
        'positions_json'
    ]

    def __init__(self, response):
        """Construct a new 'Layout' object having the attributes specified in '_fields'

        Args:
            response (dict): Json representation of layout details.
        """
        GSLayout.__init__(self)
        ResponseObject.__init__(self, response)
        self.url = 'http://graphspace.org/graphs/{0}?user_layout={1}'.format(self.graph_id, self.id)
        self._convert_string_to_json()

    def _convert_string_to_json(self):
        """Convert the json dumped string attributes 'positions_json' and 'style_json'
        into dictionaries.
        """
        self.style_json = json.loads(self.style_json)
        self.positions_json = json.loads(self.positions_json)
