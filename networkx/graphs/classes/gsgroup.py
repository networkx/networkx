import datetime


class GSGroup(object):
	"""GSGroup class.

	A GSGroup stores the details of a group that is understood by GraphSpace.

	It holds the information about the group such as name and description.

	It provides methods to define, modify and delete the details of the group.

	Attributes:
		name (str): Name of group.
		description (str): Description of group.
	"""

	def __init__(self, name=None, description=None):
		"""Construct a new 'GSGroup' object.

		Args:
			name (str, optional): Name of the group. Defaults to None.
			description (str, optional): Description of the group. Defaults to None.
		"""
		if name is None:
			self.set_name('Group ' + datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))
		else:
			self.name = name
		self.description = description

	def json(self):
		"""Get the json representation of group details.

		Returns:
			dict: Json representation of group details.

		Example:
			>>> from graphspace_python.graphs.classes.gsgroup import GSGroup
			>>> group = GSGroup(name='My sample group', description='a sample group for demo')
			>>> group.json()
			{'name': 'My sample group', 'description': 'a sample group for demo'}
		"""
		data = {
			'name': self.get_name(),
			'description': self.get_description()
		}
		return data

	def get_name(self):
		"""Get the name of group.

		Returns:
			str: Name of group.

		Example:
			>>> from graphspace_python.graphs.classes.gsgroup import GSGroup
			>>> group = GSGroup(name='My sample group', description='a sample group for demo')
			>>> group.get_name()
			'My sample group'
		"""
		return self.name

	def set_name(self, name):
		"""Set the name of the group.

		Args:
			name (str): Name of group.

		Example:
			>>> from graphspace_python.graphs.classes.gsgroup import GSGroup
			>>> group = GSGroup()
			>>> group.set_name('My sample group')
			>>> group.get_name()
			'My sample group'
		"""
		self.name = name

	def get_description(self):
		"""Get description of the group.

		Returns:
			str: Description of group.

		Example:
			>>> from graphspace_python.graphs.classes.gsgroup import GSGroup
			>>> group = GSGroup(name='My sample group', description='a sample group for demo')
			>>> group.get_description()
			'a sample group for demo'
		"""
		return self.description

	def set_description(self, description):
		"""Set description of the group.

		Args:
			description (str): Description of group.

		Example:
			>>> from graphspace_python.graphs.classes.gsgroup import GSGroup
			>>> group = GSGroup()
			>>> group.set_description('a sample group for demo')
			>>> group.get_description()
			'a sample group for demo'
		"""
		self.description = description
