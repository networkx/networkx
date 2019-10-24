from graphspace_python.api.config import GROUPS_PATH
from graphspace_python.api.obj.api_response import APIResponse


class Groups(object):
    """Groups endpoint class.

    Provides methods for group related operations such as saving, fetching, updating, deleting groups on GraphSpace.

    Also provides methods for group member and group graph related operations such as fetching
    all members or graphs of the group, adding or deleting new member or graph to the group.
    """

    def __init__(self, client):
        self.client = client

    def post_group(self, group):
        """Create a group for the requesting user.

        Args:
                group (GSGroup or Group): Object having group details, such as name, description.

        Returns:
                Group: Saved group on GraphSpace.

        Raises:
                GraphSpaceError: If error response is received from the GraphSpace API.

        Example:
                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Creating a group
                >>> from graphspace_python.graphs.classes.gsgroup import GSGroup
                >>> group = GSGroup(name='My Sample Group', description='sample group')
                >>> # Saving group on GraphSpace
                >>> graphspace.post_graph(group)

        Note:
                Refer to the `tutorial <../tutorial/tutorial.html#creating-a-group>`_ for more about posting groups.
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = group.json()
        data.update({'owner_email': self.client.username})
        return APIResponse('group',
                           self.client._make_request(
                               "POST", GROUPS_PATH, data=data, headers=headers)
                           ).group

    def get_group(self, group_name=None, group_id=None):
        """Get a group with the given group_name or group_id, where the requesting user is a member.

        Args:
                group_name (str, optional): Name of the group to be fetched. Defaults to None.
                group_id (int, optional): ID of the group to be fetched. Defaults to None.

        Returns:
                Group or None: Group object, if group with the given 'group_name' or 'group_id' exists; otherwise None.

        Raises:
                Exception: If both 'group_name' and 'group_id' are None.
                GraphSpaceError: If error response is received from the GraphSpace API.

        Examples:
                Getting a group by name:

                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Fetching a group
                >>> group = graphspace.get_group(group_name='My Sample Group')
                >>> group.get_name()
                u'My Sample Group'

                Getting a group by id:

                >>> group = graphspace.get_group(group_id=198)
                >>> group.get_name()
                u'My Sample Graph'

        Note:
                Refer to the `tutorial <../tutorial/tutorial.html#fetching-a-group-from-graphspace>`_ for more about fetching groups.
        """
        if group_id is not None:
            group_by_id_path = GROUPS_PATH + str(group_id)
            return APIResponse('group',
                               self.client._make_request(
                                   "GET", group_by_id_path)
                               ).group

        if group_name is not None:
            response = self.client._make_request("GET", GROUPS_PATH, url_params={
                'member_email': self.client.username,
                'name': group_name
            })
            if response.get('total', 0) > 0:
                return APIResponse('group',
                                   response.get('groups')[0]
                                   ).group
            else:
                return None

        raise Exception('Both group_id and group_name can\'t be none!')

    def update_group(self, group, group_name=None, group_id=None):
        """Update a group on GraphSpace with the provided group object. If group_name or group_id
        is also provided then the update will be performed for that group having the given name or id.

        Args:
                group (GSGroup or Group): Object having group details, such as name, description.
                group_name (str, optional): Name of the group to be updated. Defaults to None.
                group_id (int, optional): ID of the group to be updated. Defaults to None.

        Returns:
                Group: Updated group on GraphSpace.

        Raises:
                Exception: If both 'group_name' and 'group_id' are None and group object has
                        no 'name' or 'id' attribute; or if group doesnot exist.
                GraphSpaceError: If error response is received from the GraphSpace API.

        Examples:
                Updating a group by creating a new group and replacing the existing group:

                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Creating the new group
                >>> group = GSGroup(name='My Sample Group', description='updated sample group')
                >>> # Updating to replace the existing group
                >>> group = graphspace.update_group(group)
                >>> group.get_description()
                u'updated sample group'

                Another way of updating a group by fetching and editing the existing group:

                >>> # Fetching the group
                >>> group = graphspace.get_group(group_name='My Sample Group')
                >>> # Modifying the fetched group
                >>> group.set_description('updated sample group')
                >>> # Updating group
                >>> group = graphspace.update_group(group)
                >>> group.get_description()
                u'updated sample group'

                If you also provide 'group_name' or 'group_id' as param then the update will
                be performed for that group having the given name or id:

                >>> graphspace.update_group(group, group_id=198)

        Note:
                Refer to the `tutorial <../tutorial/tutorial.html#updating-a-group-on-graphspace>`_ for more about updating groups.
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        if group_id is not None or hasattr(group, 'id'):
            group_id = group_id if group_id is not None else group.id
            group_by_id_path = GROUPS_PATH + str(group_id)
            return APIResponse('group',
                               self.client._make_request(
                                   "PUT", group_by_id_path, data=group.json(), headers=headers)
                               ).group

        if group_name is not None or hasattr(group, 'name'):
            group_name = group_name if group_name is not None else group.name
            group1 = self.get_group(group_name=group_name)
            if group1 is None or group1.id is None:
                raise Exception('Group with name `%s` doesnt exist for user `%s`!' % (
                    group_name, self.client.username))
            else:
                group_by_id_path = GROUPS_PATH + str(group1.id)
                return APIResponse('group',
                                   self.client._make_request(
                                       "PUT", group_by_id_path, data=group.json(), headers=headers)
                                   ).group

        raise Exception(
            'Both group_id and group_name can\'t be none when group object has no \'name\' or \'id\' attribute!')

    def delete_group(self, group_name=None, group_id=None, group=None):
        """Delete a group from GraphSpace provided the group_name, group_id or the group
        object itself, where the requesting user is the owner.

        Args:
                group_name (str, optional): Name of the group to be deleted. Defaults to None.
                group_id (int, optional): ID of the group to be deleted. Defaults to None.
                group (GSGroup or Group, optional): Object having group details, such as name, description. Defaults to None.

        Returns:
                str: Success/Error Message from GraphSpace.

        Raises:
                Exception: If both 'group_name' and 'group_id' are None and group object has no
                        'name' or 'id' attribute; or if group doesnot exist.
                GraphSpaceError: If error response is received from the GraphSpace API.

        Examples:
                Deleting a group by name:

                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Deleting a group
                >>> graphspace.delete_group(group_name='My Sample Group')
                u'Successfully deleted group with id=198'

                Deleting a group by id:

                >>> graphspace.delete_group(group_id=198)
                u'Successfully deleted group with id=198'

                Deleting a group by passing group object itself as param:

                >>> group = graphspace.get_group(group_name='My Sample Group')
                >>> graphspace.delete_group(group=group)
                u'Successfully deleted group with id=198'

        Note:
                Refer to the `tutorial <../tutorial/tutorial.html#deleting-a-group-on-graphspace>`_ for more about deleting groups.
        """
        if group is not None:
            if hasattr(group, 'id'):
                group_id = group.id
            elif hasattr(group, 'name'):
                group_name = group.name

        if group_id is not None:
            group_by_id_path = GROUPS_PATH + str(group_id)
            response = self.client._make_request("DELETE", group_by_id_path)
            return response['message']

        if group_name is not None:
            group = self.get_group(group_name=group_name)
            if group is None or group.id is None:
                raise Exception('Group with name `%s` doesnt exist for user `%s`!' % (
                    group_name, self.client.username))
            else:
                group_by_id_path = GROUPS_PATH + str(group.id)
                response = self.client._make_request(
                    "DELETE", group_by_id_path)
                return response['message']

        raise Exception(
            'Both group_id and group_name can\'t be none when group object has no \'name\' or \'id\' attribute!')

    def get_my_groups(self, limit=20, offset=0):
        """Get groups created by the requesting user.

        Args:
                offset (int, optional): Offset the list of returned entities by this number. Defaults to 0.
                limit (int, optional): Number of entities to return. Defaults to 20.

        Returns:
                List[Group]: List of groups owned by the requesting user.

        Raises:
                GraphSpaceError: If error response is received from the GraphSpace API.

        Example:
                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Fetching my groups
                >>> groups = graphspace.get_my_groups(limit=5)
                >>> groups[0].get_name()
                u'Test Group'
        """
        query = {
            'limit': limit,
            'offset': offset,
            'owner_email': self.client.username
        }

        return APIResponse('group',
                           self.client._make_request(
                               "GET", GROUPS_PATH, url_params=query)
                           ).groups

    def get_all_groups(self, limit=20, offset=0):
        """Get groups where the requesting user is a member.

        Args:
                offset (int, optional): Offset the list of returned entities by this number. Defaults to 0.
                limit (int, optional): Number of entities to return. Defaults to 20.

        Returns:
                List[Group]: List of groups where the requesting user is a member.

        Raises:
                GraphSpaceError: If error response is received from the GraphSpace API.

        Example:
                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Fetching all groups
                >>> groups = graphspace.get_all_groups(limit=5)
                >>> groups[0].get_name()
                u'Test Group'
        """
        query = {
            'limit': limit,
            'offset': offset,
            'member_email': self.client.username
        }

        return APIResponse('group',
                           self.client._make_request(
                               "GET", GROUPS_PATH, url_params=query)
                           ).groups

    def get_group_members(self, group_name=None, group_id=None, group=None):
        """Get members of a group provided the group_name, group_id or the group object itself.

        Args:
                group_name (str, optional): Name of the group. Defaults to None.
                group_id (int, optional): ID of the group. Defaults to None.
                group (GSGroup or Group, optional): Object having group details, such as name, description. Defaults to None.

        Returns:
                List[Member]: List of members belonging to the group.

        Raises:
                Exception: If both 'group_name' and 'group_id' are None and group object has no
                        'name' or 'id' attribute; or if group doesnot exist.
                GraphSpaceError: If error response is received from the GraphSpace API.

        Examples:
                Getting members of a group when group name is known:

                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Fetching group members
                >>> members = graphspace.get_group_members(group_name='My Sample Group')
                >>> members[0].email
                u'user1@example.com'

                Getting members of a group when group id is known:

                >>> members = graphspace.get_group_members(group_id=198)
                >>> members[0].email
                u'user1@example.com'

                Getting members of a group by passing group object itself as param:

                >>> group = graphspace.get_group(group_name='My Sample Group')
                >>> members = graphspace.get_group_members(group=group)
                >>> members[0].email
                u'user1@example.com'

        Note:
                Refer to the `tutorial <../tutorial/tutorial.html#fetching-members-of-a-group-from-graphspace>`_ for more about fetching group members.
        """
        if group is not None:
            if hasattr(group, 'id'):
                group_id = group.id
            elif hasattr(group, 'name'):
                group_name = group.name

        if group_id is not None:
            group_members_path = GROUPS_PATH + str(group_id) + '/members'
            return APIResponse('member',
                               self.client._make_request(
                                   "GET", group_members_path)
                               ).members

        if group_name is not None:
            group = self.get_group(group_name=group_name)
            if group is None or group.id is None:
                raise Exception('Group with name `%s` doesnt exist for user `%s`!' % (
                    group_name, self.client.username))
            else:
                group_members_path = GROUPS_PATH + str(group.id) + '/members'
                return APIResponse('member',
                                   self.client._make_request(
                                       "GET", group_members_path)
                                   ).members

        raise Exception(
            'Both group_id and group_name can\'t be none when group object has no \'name\' or \'id\' attribute!')

    def add_group_member(self, member_email, group_name=None, group_id=None, group=None):
        """Add a member to a group provided the group_name, group_id or the group object itself.

        Args:
                member_email (str): Email of the member to be added to the group.
                group_name (str, optional): Name of the group. Defaults to None.
                group_id (int, optional): ID of the group. Defaults to None.
                group (GSGroup or Group, optional): Object having group details, such as name, description. Defaults to None.

        Returns:
                dict: Dict containing 'group_id' and 'user_id' of the added member.

        Raises:
                Exception: If both 'group_name' and 'group_id' are None and group object has no
                        'name' or 'id' attribute; or if group doesnot exist.
                GraphSpaceError: If error response is received from the GraphSpace API.

        Examples:
                Adding a member to a group when group name is known:

                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Adding a member to group
                >>> graphspace.add_group_member(member_email='user2@example.com', group_name='My Sample Group')
                {u'group_id': u'198', u'user_id': 2}

                Adding a member to a group when group id is known:

                >>> graphspace.add_group_member(member_email='user2@example.com', group_id=198)
                {u'group_id': u'198', u'user_id': 2}

                Adding a member to a group by passing group object itself as param:

                >>> group = graphspace.get_group(group_name='My Sample Group')
                >>> graphspace.add_group_member(member_email='user2@example.com', group=group)
                {u'group_id': u'198', u'user_id': 2}

        Note:
                Refer to the `tutorial <../tutorial/tutorial.html#adding-a-member-to-a-group-on-graphspace>`_ for more about adding group members.
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        if group is not None:
            if hasattr(group, 'id'):
                group_id = group.id
            elif hasattr(group, 'name'):
                group_name = group.name

        if group_id is not None:
            group_members_path = GROUPS_PATH + str(group_id) + '/members'
            return self.client._make_request("POST", group_members_path, data={'member_email': member_email}, headers=headers)

        if group_name is not None:
            group = self.get_group(group_name=group_name)
            if group is None or group.id is None:
                raise Exception('Group with name `%s` doesnt exist for user `%s`!' % (
                    group_name, self.client.username))
            else:
                group_members_path = GROUPS_PATH + str(group.id) + '/members'
                return self.client._make_request("POST", group_members_path, data={'member_email': member_email}, headers=headers)

        raise Exception(
            'Both group_id and group_name can\'t be none when group object has no \'name\' or \'id\' attribute!')

    def delete_group_member(self, member_id=None, member=None, group_name=None, group_id=None, group=None):
        """Delete a member with given member_id or member object from a group provided
        the group_name, group_id or the group object itself.

        Args:
                member_id (int, optional): ID of the member to be deleted from the group. Defaults to None.
                member (Member, optional): Object having member details, such as id, email. Defaults to None.
                group_name (str, optional): Name of the group. Defaults to None.
                group_id (int, optional): ID of the group. Defaults to None.
                group (GSGroup or Group, optional): Object having group details, such as name, description. Defaults to None.

        Returns:
                str: Success/Error Message from GraphSpace.

        Raises:
                Exception: If both 'group_name' and 'group_id' are None and group object has no
                        'name' or 'id' attribute; or if 'member_id' is None and member object has no
                        'id' attribute; or if group doesnot exist.
                GraphSpaceError: If error response is received from the GraphSpace API.

        Examples:
                Deleting a member from a group when group name is known:

                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Deleting a member from group
                >>> graphspace.delete_group_member(member_id=2, group_name='My Sample Group')
                u'Successfully deleted member with id=2 from group with id=198'

                Deleting a member from a group when group id is known:

                >>> graphspace.delete_group_member(member_id=2, group_id=198)
                u'Successfully deleted member with id=2 from group with id=198'

                Deleting a member from a group by passing group object itself as param:

                >>> group = graphspace.get_group(group_name='My Sample Group')
                >>> graphspace.delete_group_member(member_id=2, group=group)
                u'Successfully deleted member with id=2 from group with id=198'

                Deleting a member from a group by passing member object as param:

                >>> members = graphspace.get_group_members(group_name='My Sample Group')
                >>> graphspace.delete_group_member(member=members[0], group_name='My Sample Group')
                u'Successfully deleted member with id=2 from group with id=198'

        Note:
                Refer to the `tutorial <../tutorial/tutorial.html#deleting-a-member-from-a-group-on-graphspace>`_ for more about deleting group members.
        """
        if group is not None:
            if hasattr(group, 'id'):
                group_id = group.id
            elif hasattr(group, 'name'):
                group_name = group.name

        if member is not None:
            if hasattr(member, 'id'):
                member_id = member.id

        if member_id is None:
            raise Exception(
                'member_id can\'t be none when member object has no \'id\' attribute!')

        if group_id is not None:
            group_members_path = GROUPS_PATH + \
                str(group_id) + '/members/' + str(member_id)
            response = self.client._make_request("DELETE", group_members_path)
            return response['message']

        if group_name is not None:
            group = self.get_group(group_name=group_name)
            if group is None or group.id is None:
                raise Exception('Group with name `%s` doesnt exist for user `%s`!' % (
                    group_name, self.client.username))
            else:
                group_members_path = GROUPS_PATH + \
                    str(group.id) + '/members/' + str(member_id)
                response = self.client._make_request(
                    "DELETE", group_members_path)
                return response['message']

        raise Exception(
            'Both group_id and group_name can\'t be none when group object has no \'name\' or \'id\' attribute!')

    def get_group_graphs(self, group_name=None, group_id=None, group=None, limit=20, offset=0):
        """Get graphs shared with a group provided the group_name, group_id or the group object itself.

        Args:
                group_name (str, optional): Name of the group. Defaults to None.
                group_id (int, optional): ID of the group. Defaults to None.
                group (GSGroup or Group, optional): Object having group details, such as name, description. Defaults to None.
                offset (int, optional): Offset the list of returned entities by this number. Defaults to 0.
                limit (int, optional): Number of entities to return. Defaults to 20.


        Returns:
                List[Graph]: List of graphs belonging to the group.

        Raises:
                Exception: If both 'group_name' and 'group_id' are None and group object has no
                        'name' or 'id' attribute; or if group doesnot exist.
                GraphSpaceError: If error response is received from the GraphSpace API.

        Examples:
                Getting graphs of a group when group name is known:

                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Fetching group graphs
                >>> graphs = graphspace.get_group_graphs(group_name='My Sample Group')
                >>> graphs[0].get_name()
                u'My Sample Graph'

                Getting graphs of a group when group id is known:

                >>> graphs = graphspace.get_group_graphs(group_id=198)
                >>> graphs[0].get_name()
                u'My Sample Graph'

                Getting graphs of a group by passing group object itself as param:

                >>> group = graphspace.get_group(group_name='My Sample Group')
                >>> graphs = graphspace.get_group_graphs(group=group)
                >>> graphs[0].get_name()
                u'My Sample Graph'

        Note:
                Refer to the `tutorial <../tutorial/tutorial.html#fetching-graphs-shared-with-a-group>`_ for more about fetching graphs of a group.
        """
        query = {
            'limit': limit,
            'offset': offset
        }
        
        if group is not None:
            if hasattr(group, 'id'):
                group_id = group.id
            elif hasattr(group, 'name'):
                group_name = group.name

        if group_id is not None:
            group_graphs_path = GROUPS_PATH + str(group_id) + '/graphs'
            return APIResponse('graph',
                               self.client._make_request(
                                   "GET", group_graphs_path, url_params=query)
                               ).graphs

        if group_name is not None:
            group = self.get_group(group_name=group_name)
            if group is None or group.id is None:
                raise Exception('Group with name `%s` doesnt exist for user `%s`!' % (
                    group_name, self.client.username))
            else:
                group_graphs_path = GROUPS_PATH + str(group.id) + '/graphs'
                return APIResponse('graph',
                                   self.client._make_request(
                                       "GET", group_graphs_path, url_params=query)
                                   ).graphs

        raise Exception(
            'Both group_id and group_name can\'t be none when group object has no \'name\' or \'id\' attribute!')

    def share_graph(self, graph_name=None, graph_id=None, graph=None, group_name=None, group_id=None, group=None):
        """Share a graph with a group by providing any of graph_name, graph_id or graph object
         along with any of group_name, group_id or group object.

        Args:
                graph_name (str, optional): Name of the graph. Defaults to None.
                graph_id (int, optional): ID of the graph. Defaults to None.
                graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.
                group_name (str, optional): Name of the group. Defaults to None.
                group_id (int, optional): ID of the group. Defaults to None.
                group (GSGroup or Group, optional): Object having group details, such as name, description. Defaults to None.

        Returns:
                dict: Dict containing 'group_id', 'graph_id', 'created_at', 'updated_at' details of the shared graph.

        Raises:
                Exception: If both 'group_name' and 'group_id' are None and group object has no
                        'name' or 'id' attribute; or if both 'graph_name' and 'graph_id' are None and
                        graph object has no 'name' or 'id' attribute; or if the group or graph doesnot exist.
                GraphSpaceError: If error response is received from the GraphSpace API.

        Examples:
                Sharing a graph with a group when group name is known:

                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Sharing a graph with a group
                >>> graphspace.share_graph(graph_id=65390, group_name='My Sample Group')
                {u'created_at': u'2017-07-20T18:40:36.267052', u'group_id': u'198', u'graph_id':
                65390, u'updated_at': u'2017-07-20T18:40:36.267052'}

                Sharing a graph with a group when group id is known:

                >>> graphspace.share_graph(graph_id=65390, group_id=198)
                {u'created_at': u'2017-07-20T18:40:36.267052', u'group_id': u'198', u'graph_id':
                65390, u'updated_at': u'2017-07-20T18:40:36.267052'}

                Sharing a graph with a group by passing group object itself as param:

                >>> group = graphspace.get_group(group_name='My Sample Group')
                >>> graphspace.share_graph(graph_id=65390, group=group)
                {u'created_at': u'2017-07-20T18:40:36.267052', u'group_id': u'198', u'graph_id':
                65390, u'updated_at': u'2017-07-20T18:40:36.267052'}

                Sharing a graph with a group by providing graph name:

                >>> graphspace.share_graph(graph_name='My Sample Graph', group_id=198)
                {u'created_at': u'2017-07-20T18:40:36.267052', u'group_id': u'198', u'graph_id':
                65390, u'updated_at': u'2017-07-20T18:40:36.267052'}

                Sharing a graph with a group by providing graph object:

                >>> graph = graphspace.get_graph(graph_name='My Sample Graph')
                >>> graphspace.share_graph(graph=graph, group_id=198)
                {u'created_at': u'2017-07-20T18:40:36.267052', u'group_id': u'198', u'graph_id':
                65390, u'updated_at': u'2017-07-20T18:40:36.267052'}

        Note:
                Refer to the `tutorial <../tutorial/tutorial.html#sharing-a-graph-with-a-group>`_ for more about adding graph to a group.
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        if group is not None:
            if hasattr(group, 'id'):
                group_id = group.id
            elif hasattr(group, 'name'):
                group_name = group.name

        if graph is not None:
            if hasattr(graph, 'id'):
                graph_id = graph.id
            elif hasattr(graph, 'name'):
                graph_name = graph.name

        if graph_id is None and graph_name is None:
            raise Exception(
                'Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')

        if graph_id is None:
            graph = self.client.get_graph(graph_name=graph_name)
            if graph is None or graph.id is None:
                raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (
                    graph_name, self.client.username))
            else:
                graph_id = graph.id

        if group_id is not None:
            group_graphs_path = GROUPS_PATH + str(group_id) + '/graphs'
            return self.client._make_request("POST", group_graphs_path, data={'graph_id': graph_id}, headers=headers)

        if group_name is not None:
            group = self.get_group(group_name=group_name)
            if group is None or group.id is None:
                raise Exception('Group with name `%s` doesnt exist for user `%s`!' % (
                    group_name, self.client.username))
            else:
                group_graphs_path = GROUPS_PATH + str(group.id) + '/graphs'
                return self.client._make_request("POST", group_graphs_path, data={'graph_id': graph_id}, headers=headers)

        raise Exception(
            'Both group_id and group_name can\'t be none when group object has no \'name\' or \'id\' attribute!')

    def unshare_graph(self, graph_name=None, graph_id=None, graph=None, group_name=None, group_id=None, group=None):
        """Unshare a graph with a group by providing any of graph_name, graph_id or graph object
         along with any of group_name, group_id or group object.

        Args:
                graph_name (str, optional): Name of the graph. Defaults to None.
                graph_id (int, optional): ID of the graph. Defaults to None.
                graph (GSGraph or Graph, optional): Object having graph details, such as name, graph_json, style_json, is_public, tags. Defaults to None.
                group_name (str, optional): Name of the group. Defaults to None.
                group_id (int, optional): ID of the group. Defaults to None.
                group (GSGroup or Group, optional): Object having group details, such as name, description. Defaults to None.

        Returns:
                str: Success/Error Message from GraphSpace.

        Raises:
                Exception: If both 'group_name' and 'group_id' are None and group object has no
                        'name' or 'id' attribute; or if both 'graph_name' and 'graph_id' are None and
                        graph object has no 'name' or 'id' attribute; or if the group or graph doesnot exist.
                GraphSpaceError: If error response is received from the GraphSpace API.

        Examples:
                Unshare a graph with a group when group name is known:

                >>> # Connecting to GraphSpace
                >>> from graphspace_python.api.client import GraphSpace
                >>> graphspace = GraphSpace('user1@example.com', 'user1')
                >>> # Unsharing a graph with a group
                >>> graphspace.unshare_graph(graph_id=65390, group_name='My Sample Group')
                u'Successfully deleted graph with id=65390 from group with id=198'

                Unshare a graph with a group when group id is known:

                >>> graphspace.unshare_graph(graph_id=65390, group_id=198)
                u'Successfully deleted graph with id=65390 from group with id=198'

                Unshare a graph with a group by passing group object itself as param:

                >>> group = graphspace.get_group(group_name='My Sample Group')
                >>> graphspace.unshare_graph(graph_id=65390, group=group)
                u'Successfully deleted graph with id=65390 from group with id=198'

                Unshare a graph with a group by providing graph name:

                >>> graphspace.unshare_graph(graph_name='My Sample Graph', group_id=198)
                u'Successfully deleted graph with id=65390 from group with id=198'

                Unshare a graph with a group by providing graph object:

                >>> graph = graphspace.get_graph(graph_name='My Sample Graph')
                >>> graphspace.unshare_graph(graph=graph, group_id=198)
                u'Successfully deleted graph with id=65390 from group with id=198'

        Note:
                Refer to the `tutorial <../tutorial/tutorial.html#unsharing-a-graph-with-a-group>`_ for more about deleting graph from a group.
        """
        if group is not None:
            if hasattr(group, 'id'):
                group_id = group.id
            elif hasattr(group, 'name'):
                group_name = group.name

        if graph is not None:
            if hasattr(graph, 'id'):
                graph_id = graph.id
            elif hasattr(graph, 'name'):
                graph_name = graph.name

        if graph_id is None and graph_name is None:
            raise Exception(
                'Both graph_id and graph_name can\'t be none when graph object has no \'name\' or \'id\' attribute!')

        if graph_id is None:
            graph = self.client.get_graph(graph_name=graph_name)
            if graph is None or graph.id is None:
                raise Exception('Graph with name `%s` doesnt exist for user `%s`!' % (
                    graph_name, self.client.username))
            else:
                graph_id = graph.id

        if group_id is not None:
            group_graphs_path = GROUPS_PATH + \
                str(group_id) + '/graphs/' + str(graph_id)
            response = self.client._make_request("DELETE", group_graphs_path)
            return response['message']

        if group_name is not None:
            group = self.get_group(group_name=group_name)
            if group is None or group.id is None:
                raise Exception('Group with name `%s` doesnt exist for user `%s`!' % (
                    group_name, self.client.username))
            else:
                group_graphs_path = GROUPS_PATH + \
                    str(group.id) + '/graphs/' + str(graph_id)
                response = self.client._make_request(
                    "DELETE", group_graphs_path)
                return response['message']

        raise Exception(
            'Both group_id and group_name can\'t be none when group object has no \'name\' or \'id\' attribute!')
