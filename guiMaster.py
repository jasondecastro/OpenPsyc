#guiMaster.py
import wx
import inspect
from gmHelpers import *

class objApp:
	"""app the target object (this is what you call first)"""
	def __init__(self, targetClass):
		self.app = wx.App(False)
		objMaker(None, targetClass)

	def go(self):
		self.app.MainLoop()

class objMaker:
	"""place a target object in either a frame or not a frame"""
	def __init__(self, parent, target, name="", *args, **kwargs):
		if inspect.isclass(target) or inspect.isfunction(target):
			frame = wx.Frame(parent)
			self.frame = frame
			sizer = objSizer(frame, target)
			self.sizer = sizer
			self.sizer.name = name
			self.frame.SetSizerAndFit(sizer)
			self.frame.Show()
		elif inspect.ismethod(target):
			self.frame = None
			self.sizer = objSizer(parent, target)
			self.sizer.name = name
		elif inspect.ismodule(target):
			for name, obj in inspect.getmembers(target):
				if inspect.isclass(obj):
					print name, obj
					objMaker(None, obj, name)
		else:
			pass
			

class objSizer(wx.GridBagSizer):
	"""Main Sizer for object visualization
	objSizer will take a target object (class, function or method) and 
	construct a gui based on its properties
	"""
	def __init__(self, parent, target, recurse=True, *args, **kwargs):
		"""get the attributes of a target object, 
		see what the default values to ascertain what type of gui component it should be
		"""
		wx.GridBagSizer.__init__(self, *args, **kwargs)
		
		print target

		#get the args from the right places
		if inspect.isclass(target):
			self.args = inspect.getargspec(target.__init__)
		elif inspect.isfunction(target) or inspect.ismethod(target):
			self.args = inspect.getargspec(target)
			
		else:
			raise Exception("I only work with functions, classes and methods, dick.")


		self.title = inspect.getfile(target)
	
		self.target = target
		self.recurse = recurse
		self.parent = parent

		#get the arguments and the default values
		self.argnames = self.args[0]
		if 'self' in self.argnames:
			self.argnames.remove('self')
		self.defaults = self.args[3]
		if not self.defaults:
			self.defaults = ()

		if self.argnames:
			self.nondefaults = len(self.argnames) - len(self.defaults)
			while len(self.defaults) != len(self.argnames):
				d = list(self.defaults)
				d.insert(0, None)
				self.defaults = tuple(d)
		else:
			self.nondefaults = 0

		#make the thing
		self.construct()

	def construct(self):
		"""create widgets from argument/attributes and values"""		
		self.widgets = []

		self.items = {}
		self.classes = {}
		self.classNames = {}

		self.items['args'] = []
		self.items['init'] = None
		self.items['done'] = None
		self.items['return'] = None
		self.items['methods'] = []
		self.codeboxes = {}

		#get the arguments, create GUI components out of them, store them for later
		for arg in self.argnames:
			i = self.argnames.index(arg)
			if len(self.defaults) > i:
				value = self.defaults[i]
			else:
				value = None

			p = wx.Panel(self.parent, -1, style = wx.RAISED_BORDER)
			widget = objWidget(p, arg, value, self)
			if hasattr(widget, "btn"):
				btn = widget.btn
				self.classes[str(btn.GetId())] = btn.the_class
				self.classNames[str(btn.GetId())] = btn.arg
				if btn.the_instance == None:
					p.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
			if hasattr(widget, "cb"):
				cb = widget.cb
				self.codeboxes[str(cb.GetId())] = cb

			p.SetSizer(widget)
			self.widgets.append(widget)
			self.items['args'].append(p)
		
		#create the 'init' function button - this one is special because its args are already listed
		if inspect.isclass(self.target):
			init = wx.Button(self.parent, 1, 'Initialize')
			self.items['init'] = init
			done = wx.Button(self.parent, 2, 'Return')
			self.items['done'] = done
			done.Disable()
			done.Hide()

		b_id = 2

		self.functions = []
		self.buttons = []

		if self.recurse:
			for f in inspect.getmembers(self.target):
				#if this is a user defined, public function, create a frame for its arguments
				if inspect.isbuiltin(f[0]) or f[0].startswith('_'):
					pass
				else:
					b_id += 1
					self.functions.append(f[1])
					button = wx.Button(self.parent, b_id, f[0])
					button.Disable()
					self.buttons.append(button)
					functionFrame = objSizer(self.parent, f[1], recurse=False)
					self.items['methods'].append(functionFrame)

		self.parent.Bind(wx.EVT_BUTTON, self.onButton)
		self.parent.Bind(wx.EVT_TEXT, self.onText)
		
		self.layout()


	def layout(self):
		"""do the positioning of the contents of self.items"""
		args = self.items['args']
		init = self.items['init']
		done = self.items['done']
		methods = self.items['methods']

		numitems = len(args)

		#if we're assembling the top level args
		if self.recurse:
			#we want a nice grid of args
			if numitems % 5 == 0:
				cols = numitems/5
				rows = numitems/cols
			elif numitems % 4 == 0:
				cols = numitems/4
				rows = numitems/cols						
			elif numitems % 3 == 0:
				cols = numitems/3
				rows = numitems/cols			
			elif numitems % 2 == 0:
				cols = numitems/2
				rows = numitems/cols
			else:
				rows = numitems/3
				cols = numitems/3 + 1 

		#otherwise we just want a line of args
		else:
			cols = numitems
			rows = 1

		self.SetRows(rows)
		self.SetCols(cols)

		index = 0

		for r in range(0, rows):
			for c in range(0, cols):
				if len(args) > index:
					a = args[index]
					if index <= self.nondefaults-1:
						a.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
					self.Add(a, [r, c], flag = wx.EXPAND | wx.ALL, border = 5)
					#colours.reverse()

				index += 1

		if init:
			
			self.SetCols(cols)
			if self.parent.Parent:
				cols += 1
				self.Add(init, [0, cols-1], span=[rows-1, 1], flag = wx.EXPAND)
				done.Show()
				self.Add(done, [rows-1, cols-1], flag=wx.EXPAND)
			else:
				cols += 1
				self.Add(init, [0, cols-1], span=[rows, 1], flag = wx.EXPAND)

		count = rows + 1
		if len(methods):
			rows += len(methods) * 2
			self.SetRows(rows + 1)

		for b, m in zip(self.buttons, methods):
			#we want to place these at the start of each new row
			self.Add(wx.StaticLine(self.parent), pos=[count, 0], span=[1, cols], flag=wx.EXPAND)
			count += 1
			self.Add(m, [count, 0], span=[1, cols - 1], flag=wx.EXPAND)	
			self.Add(b, [count, cols-1], flag=wx.EXPAND)
		
			count += 1

	def initialize(self):
		"""create an instance of the target class (as self.obj)
		from values provided in the gui
		also enable class method buttons
		"""
		values = self.deconstruct()
		#now create an object from the values
		argString = "self.target("
		for a in self.argnames:
			argString += "%s=values[%s]," % (a, self.argnames.index(a))
		argString = argString.rstrip(",")
		argString += ")"
		
		self.obj = eval(argString)

		for b in self.buttons:
			b.Enable()

		if self.parent.Parent:
			self.items['done'].Enable()

	def setDefault(self, value, arg):
		"""sets a default value for a given arg"""
		index = self.argnames.index(arg)
		defaults = list(self.defaults)
		defaults[index] = value
		defaults = tuple(defaults)
		self.defaults = defaults

	def onText(self, event):
		for cb in self.codeboxes.values():
			if cb.GetTextId() == event.GetId():
				try: 
					cb.Eval()
					if cb.Eval():
						cb.btn.Enable()
				except:		
					cb.btn.Disable()


	def onButton(self, event):
		"""button handler, calling one of target's methods"""
		if event.GetId() == 1:
			self.initialize()

		elif event.GetId() == 2:
			if self.parent.Parent:
				s = self.parent.Parent.GetSizer()
				s.items['init'].Enable()
				#self obj is the value of the initialized thing
				s.setDefault(self.obj, self.name)
				s.Clear(1)
				s.construct()				
				self.parent.Parent.Layout()
				s.initialize()
				self.parent.Destroy()				


		elif self.classes.has_key(str(event.GetId())):
			objMaker(self.parent, self.classes[str(event.GetId())], name=self.classNames[str(event.GetId())])
		elif self.codeboxes.has_key(str(event.GetId())):
			cb = self.codeboxes[str(event.GetId())]
			self.parent.GetSizer().setDefault(cb.Eval(), cb.arg)
			self.parent.GetSizer().Clear(1)
			self.parent.GetSizer().construct()
			self.parent.Layout()
		else:
			function = self.functions[event.GetId() - 3]
			ff = self.items['methods'][event.GetId() - 3]
			values = ff.deconstruct()
			argString = ""
			for a, v in zip(ff.argnames, values):
				if type(v) == str:
					v = "\"%s\"" % v
				argString += ", %s=%s" % (a, v)
			exec("function(self.obj%s)" % argString)

	def deconstruct(self):
		"""get the values for each of the fields"""
		values = []
		for w in self.widgets:
			value = w.read()
			value = value[1]

			#check if it's a string that wants to be a dict
			if type(value) == list:
				isDict = False
				v = value[0]
				if type(v) == list:
					if len(v) == 2:
						if v[0].startswith('{'):
							isDict = True

				if isDict:
					d = {}
					for v in value:
						key = v[0].lstrip('{')
						val = v[1]
						d[key] = val
					value = d 

			values.append(value)

		return values

class objWidget(wx.BoxSizer):
	"""widget displaying an argument/attribute and a value
	can handle nested items like lists and dictionaries
	"""
	def __init__(self, parent, arg, value, orient = wx.VERTICAL, *args, **kwargs):
		"""on init objWidget examines the arg-value pair it 
		receives and builds the appropriate gui component
		"""
		wx.BoxSizer.__init__(self, *args, **kwargs)
		self.parent = parent
		if type(value) == str:
			widget = wx.TextCtrl(self.parent, -1, value)
		elif type(value) == int:
			widget = wx.SpinCtrl(self.parent, -1, str(value))
		elif type(value) == float:
			widget = FloatCtrl(self.parent, -1)
			widget.SetFloat(value)
		elif type(value) == list:
			widget = wx.BoxSizer(wx.VERTICAL)
			for v in value:
				item = objWidget(self.parent, None, v)
				widget.Add(item)
		elif type(value) == bool:
			widget = wx.CheckBox(self.parent, -1)
			widget.SetValue(value)
			orient = wx.HORIZONTAL
		elif type(value) == dict:
			widget = wx.BoxSizer(wx.VERTICAL)

			for k in value.keys():
				item = objWidget(self.parent, k, value[k], wx.HORIZONTAL)
				widget.Add(item)
		elif str(type(value)) == "<type 'NoneType'>":
			#just make a box for code that will be executed
			widget = CodeBox(self.parent, arg)
			self.cb = widget
		else:
			"""what to do when it's just some random friggin object?
			make a button with the object's name and give the dang
			thing a target attribute
			"""
			widget = ClassBox(self.parent, value, arg)
			self.btn = widget.btn
		if arg:
			self.Add(wx.StaticText(self.parent, -1, arg), flag=wx.ALIGN_CENTER)

		self.Add(widget)
				
	def read(self, w=None):
		"""method read provides the value that item was storing, 
		with the necessary unpackers to reconstruct nested items
		"""

		if w==None:
			w = self

		wt = str(type(w))
		wt = wt.split('.')[-1]
		wt = wt.strip("'>")

		value = wt
		w_dict = {}
		w_dict['TextCtrl'] = "w.GetValue()"
		w_dict['SpinCtrl'] = "int(w.GetValue())"
		w_dict['FloatCtrl'] = "w.GetFloat()"
		w_dict['CheckBox'] = "w.GetValue()"
		w_dict['StaticText'] = "\"{\" + w.GetLabel()"
		w_dict['BoxSizer'] = "unpackSizer(w, self)"
		w_dict['objWidget'] = "unpackSizer(w, self)"
		w_dict['SizerItem'] = "unpackItem(w, self)"
		w_dict['Button'] = "w.value"
		w_dict['CodeBox'] = "w.Eval()"
		w_dict['ClassBox'] = "w.GetValue()"
		if w_dict.has_key(wt):
			value = eval(w_dict[wt])

		return value


