class BVH(object):
	

	def __init__(self):
		super(BVH, self).__init__()
		self.root = []


	def load_from_file(self, bvh_file_path):
		bvh_file = open(bvh_file_path, 'r')
		bvh_str = bvh_file.read()

		self.tokens = self.tokenize(bvh_str)
		self.token_index = 0

		self.parse_hierarchy()
		# for root in self.root:
		# 	print root
		self.parse_motion()

		bvh_file.close()


	def tokenize(self, source):
		import re
		# split source string with either white spaces, line separators, or tabulations
		tokens = re.split(' |\n|\t', source)
		# filter the token list, remove all empty strings
		return filter(None, tokens)


	def parse_hierarchy(self):
		if self.tokens[self.token_index] != 'HIERARCHY':
			# print 'keyword HIERARCHY not found'
			return
		self.token_index += 1
		# parse all roots to support multiple hierarchy
		while self.tokens[self.token_index] == 'ROOT':
			joint = self.read_joint()
			if joint:
				self.root.append(joint)


	def parse_motion(self):
		if self.tokens[self.token_index] != 'MOTION':
			return
		self.token_index += 1
		if self.tokens[self.token_index] != 'Frames:':
			return
		self.token_index += 1
		try:
			self.frame_count = int(self.tokens[self.token_index])
		except ValueError:
			return
		self.token_index += 1
		if self.tokens[self.token_index] != 'Frame Time:':
			return
		self.token_index += 1
		try:
			self.frame_time = float(self.tokens[self.token_index])
		except ValueError:
			return
		self.token_index += 1
		

	# before reading a joint, the token index will be pointing to the keyword ROOT,
	# JOINT, or End
	#
	# after reading a joint, the token index will point to the token right after
	# the closing brace of the joint which has been read
	#
	# in case of invalid joint format, function will ignore this joint and return None
	# and the token index will point to the token that breaks joint format
	def read_joint(self):
		# print 'current token', self.tokens[self.token_index]
		# 0 for ROOT or JOINT, 1 for End Site
		joint_type = 0
		if self.tokens[self.token_index] == 'End':
			joint_type = 1
		self.token_index += 1
		# print 'current token', self.tokens[self.token_index]
		if joint_type == 0:
			joint_name = self.tokens[self.token_index]
		self.token_index += 1
		# print 'current token', self.tokens[self.token_index]
		if self.tokens[self.token_index] != '{':
			# print 'open brace not found'
			return None
		self.token_index += 1
		# print 'current token', self.tokens[self.token_index]
		if self.tokens[self.token_index] != 'OFFSET':
			# print 'keyword OFFSET not found'
			return None
		self.token_index += 1
		# print 'current token', self.tokens[self.token_index]		
		try:
			joint_offset = [float(self.tokens[self.token_index]), float(self.tokens[self.token_index + 1]), float(self.tokens[self.token_index + 2])]
		except ValueError:
			# print 'offset value error'
			return None
		self.token_index += 3
		if joint_type == 0:
			# print 'current token', self.tokens[self.token_index]
			if self.tokens[self.token_index] != 'CHANNELS':
				# print 'keyword CHANNELS not found'
				return None
			self.token_index += 1
			# print 'current token', self.tokens[self.token_index]
			try:
				joint_channel_count = int(self.tokens[self.token_index])
			except ValueError:
				# print 'channel count value error'
				return None
			self.token_index += 1
			# print 'current token', self.tokens[self.token_index]
			joint_channels = []
			for i in range(joint_channel_count):
				joint_channels.append(self.tokens[self.token_index])
				self.token_index += 1
				# print 'current token', self.tokens[self.token_index]
			joint_children = []
			while self.tokens[self.token_index] == 'JOINT' or self.tokens[self.token_index] == 'End':
				child_joint = self.read_joint()
				# print 'current token', self.tokens[self.token_index]
				if child_joint:
					joint_children.append(child_joint)
		if self.tokens[self.token_index] != '}':
			# print 'close brace not found : ', self.tokens[self.token_index]
			return None
		if joint_type == 0:
			joint = Joint(joint_name, joint_offset, joint_channels, joint_children)
		else:
			joint = EndSite(joint_offset)
		self.token_index += 1
		return joint


class Node(object):
	

	def __init__(self, offset):
		super(Node, self).__init__()
		self.offset = offset


	def __str__(self):
		return ''


class Joint(Node):
	

	def __init__(self, node_name, offset, channels, children):
		super(Joint, self).__init__(offset)
		self.name = node_name
		self.channels = channels
		self.children = children


	def __str__(self):
		res = self.name
		res += ' ['
		for joint in self.children:
			res += str(joint)
		res += '] '
		return res


class EndSite(Node):
	

	def __init__(self, offset):
		super(EndSite, self).__init__(offset)


	def __str__(self):
		return 'EndSite : ' + str(self.offset)