import sys
class Child:
	def __init__(self):
		pass
	
	def read(self):
		print('here')
		print(sys.stdin.readline())
		print('heree')

class Parent:
	def __init__(self):
		self.child = Child()

		sys.stdout.write('bla')
		sys.stdout.flush()
		self.child.read()	

a = Parent()
