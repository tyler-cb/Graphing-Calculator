
import pygame
import tkinter as tk
import os
import sys
import platform
import numpy
import math
from math import sqrt, log, sin, cos, tan, sinh, cosh, tanh
import sympy
import json

options = {
	"windowWidth": 1000, # Width of the window, in pixels.
	"gridWidth": 700, # Width of the grid inside the window in pixels
	"windowHeight": 600, # Height of window in pixels

	"axisThickness": 2, # Thickness of the axis guides in pixels
	"axisColour": (0,0,0), # Colour of the axis guides (R, G, B)

	"plottedColour": (180,0,0), # Colour of the plotted graphs (R, G, B)
	"plottedThickness": 1, # Thickness of the plotted graphs in pixels

	"backgroundColour": (255,255,255), # Colour of the background of the grid (R, G, B)

	"guidelines": 1, # Guidelines toggle on/off 
	"guidelineColour": (204, 204, 204), # Colour of the guidelines ( R, G, B )
	"guidelineFontSize": 11, # Font size of guideline markers
	"guidelineThickness": 1, # Thickness of guidelines in pixels
	"fontColour": (0, 0, 0), # Colour of the guideline marker font ( R, G, B )

	"noOfPlotsBase": 125, # Base sampling rate of plotted graphs ( Higher = More Accurate )
	"noOfPlots": 125 # Sampling rate adjusted for the amount of plotted graphs
}

class guiController():
	def __init__(self):

		self.windowWidth = options["windowWidth"]
		self.gridWidth = options["gridWidth"]
		self.windowHeight = options["windowHeight"]

		# Initialize the tkinter window
		self.root = tk.Tk()
		self.root.title("Maths Graphing Tool")
		self.root.resizable(False, False)

		# Initialize the frames for the grid and the menu
		self.gridFrame = tk.Frame(self.root, width = self.gridWidth, height = self.windowHeight)
		self.gridFrame.pack(side = tk.RIGHT, fill="both", expand=True)
		self.menuFrame = tk.Frame(self.root, width = self.windowWidth-self.gridWidth, height = self.windowHeight)
		self.menuFrame.pack(side = tk.LEFT, fill="both", expand=True)
		self.menuFrame.grid_propagate(0)

		# Initialize the graph entry box and 'plot' button
		self.graphEntryFrame = tk.Frame(self.menuFrame, relief=tk.RAISED, borderwidth=1)
		self.graphEntryFrame.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)

		self.graphEntry = tk.Text(self.graphEntryFrame, width = 10, height = 1, font=("Helvetica", 15))
		self.graphEntry.pack(side=tk.LEFT, fill=tk.X, expand=1)
		self.graphEntryButton = tk.Button(self.graphEntryFrame, text="Plot", command=self.newEquation)
		self.graphEntryButton.pack(side=tk.RIGHT)

		# Initalize the frame for the 'currently plotted' list
		self.plottedFrame = tk.Frame(self.menuFrame, relief=tk.RAISED, borderwidth=1)
		self.plottedFrame.grid(row=1,column=0, sticky=tk.N+tk.S+tk.E+tk.W)
		self.plottedHeader = tk.Label(self.plottedFrame, text="Currently Plotted:", font=("Helvetica", 16)).pack(side=tk.TOP)
		self.scrollable = tk.Frame(self.plottedFrame)

		# Initalize the scrollbar and canvas
		self.plottedScrollbar = tk.Scrollbar(self.scrollable, orient=tk.VERTICAL)
		self.plottedScrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=0)
		self.plottedCanvas = tk.Canvas(self.scrollable, yscrollcommand=self.plottedScrollbar.set) # The yscrollcommand attribute links the canvas to the scrollbar
		self.plottedCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		self.plottedScrollbar.config(command=self.plottedCanvas.yview)

		# Set the inital scroll values for the canvas
		self.plottedCanvas.xview_moveto(0)
		self.plottedCanvas.yview_moveto(0)

		# The interior frame is created in the canvas, and will contain the widgets which will be moved when the user scrolls
		self.interior = tk.Frame(self.plottedCanvas)
		self.interior_id = self.plottedCanvas.create_window(0, 0, window=self.interior, anchor=tk.NW)

		def configureInterior(event):
				# Changes the size of the interior frame and the scrollable region of the canvas
			size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
			self.plottedCanvas.config(scrollregion="0 0 %s %s" % size)
			if self.interior.winfo_reqheight() != self.plottedCanvas.winfo_width():
				self.plottedCanvas.config(width=self.interior.winfo_reqwidth())

		# The interior frame will call the function configureInterior whenever it changes size
		self.interior.bind('<Configure>', configureInterior)

		def configureCanvas(event):
				# Changes the interior frame's width to the width of the canvas
			if self.interior.winfo_reqwidth() != self.plottedCanvas.winfo_width():
				self.plottedCanvas.itemconfigure(self.interior_id, width=self.plottedCanvas.winfo_width())

		# The canvas will call configureCanvas whenever it changes size
		self.plottedCanvas.bind('<Configure>', configureCanvas)

		self.scrollable.pack(fill=tk.BOTH, expand=1)

		# The options, tutoiral, examples and clear buttons are initalized
		self.optionsFrame = tk.Frame(self.menuFrame, relief=tk.RAISED, borderwidth=1)
		self.optionsFrame.grid(row=2,column=0, sticky=tk.N+tk.S+tk.E+tk.W)

		self.tutorialButton = tk.Button(self.optionsFrame, text="Tutorial", command=self.openTutorial)
		self.examplesButton = tk.Button(self.optionsFrame, text="Examples", command=lambda path="./Graphs/Examples": self.loadGraphs(path))
		self.optionsButton = tk.Button(self.optionsFrame, text="Options", command=self.openSettings)
		self.saveButton = tk.Button(self.optionsFrame, text="Save Graphs", command=self.saveGraphs)
		self.loadButton = tk.Button(self.optionsFrame, text="Load Graphs", command=lambda path="./Graphs/": self.loadGraphs(path))

		self.tutorialButton.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W)	
		self.examplesButton.grid(row=0,column=1,sticky=tk.N+tk.S+tk.E+tk.W)	
		self.optionsButton.grid(row=2,column=0, columnspan=2,sticky=tk.N+tk.S+tk.E+tk.W)
		self.saveButton.grid(row=1,column=0,sticky=tk.N+tk.S+tk.E+tk.W)	
		self.loadButton.grid(row=1,column=1,sticky=tk.N+tk.S+tk.E+tk.W)

		self.menuFrame.columnconfigure(0, weight=1)
		self.menuFrame.rowconfigure(0, weight=1)
		self.menuFrame.rowconfigure(1, weight=10)
		self.menuFrame.rowconfigure(2, weight=3)

		for i in range(3):
			self.optionsFrame.rowconfigure(i, weight=1)

		for i in range(2):
			self.optionsFrame.columnconfigure(i, weight=1)

	def openTutorial(self):

		tutorialRoot = tk.Toplevel()
		tutorialRoot.title("Maths Graphing Tool Tutorial")
		tutorialRoot.resizable(False, False)

		tutorialText = tk.Label(tutorialRoot, wraplength=500, text = "To begin drawing graphs, enter an equation into the equation text box in the upper-left, using x and y as variables. Once you press the 'plot' button, the graph will be drawn onto the interactive grid to the right of the application. \n\nBy pressing and holding the left mouse button and moving the mouse, you can navigate the grid and by using the scroll wheel you can zoom in and out. All of your plotted graphs will appear onto the list on the left hand side of the screen, where you can toggle or delete each graph. \n\nAdditionally, the buttons in the bottom-left of the application allow access to the settings, to change aspects of the program, access to the example graph which are pre-generated graphs designed for learning, the tutorial and the 'clear' button to delete all graphs.")

		tutorialText.pack()

	def openSettings(self):

		settingsRoot = tk.Toplevel()
		settingsRoot.title("Maths Graphing Tool Settings")
		settingsRoot.resizable(False, False)

		titleLabel = tk.Label(settingsRoot, text = "Settings", font=("Helvetica", 16))
		titleLabel.pack()

		settingsFrame = tk.Frame(settingsRoot)
		self.settingsWidgets = []

		widthLabel = tk.Label(settingsFrame, text="Window Width")
		widthEntry = tk.Entry(settingsFrame)
		widthEntry.insert(0, options["windowWidth"])
		self.settingsWidgets.append([widthLabel, widthEntry])

		gridWidthLabel = tk.Label(settingsFrame, text="Grid Width")
		gridWidthEntry = tk.Entry(settingsFrame)
		gridWidthEntry.insert(0, options["gridWidth"])
		self.settingsWidgets.append([gridWidthLabel, gridWidthEntry])

		heightLabel = tk.Label(settingsFrame, text="Window Height")
		heightEntry = tk.Entry(settingsFrame)
		heightEntry.insert(0, options["windowHeight"])
		self.settingsWidgets.append([heightLabel, heightEntry])

		axisThicknessLabel = tk.Label(settingsFrame, text="Axis Thickness")
		axisThicknessEntry = tk.Entry(settingsFrame)
		axisThicknessEntry.insert(0, options["axisThickness"])
		self.settingsWidgets.append([axisThicknessLabel, axisThicknessEntry])

		axisColourLabel = tk.Label(settingsFrame, text="Axis Colour")
		axisColourEntry = tk.Entry(settingsFrame)
		axisColourEntry.insert(0, options["axisColour"])
		self.settingsWidgets.append([axisColourLabel, axisColourEntry])

		plottedColourLabel = tk.Label(settingsFrame, text="Graph Colour")
		plottedColourEntry = tk.Entry(settingsFrame)
		plottedColourEntry.insert(0, options["plottedColour"])
		self.settingsWidgets.append([plottedColourLabel, plottedColourEntry])

		plottedThicknessLabel = tk.Label(settingsFrame, text="Graph Thickness")
		plottedThicknessEntry = tk.Entry(settingsFrame)
		plottedThicknessEntry.insert(0, options["plottedThickness"])
		self.settingsWidgets.append([plottedThicknessLabel, plottedThicknessEntry])

		backgroundColourLabel = tk.Label(settingsFrame, text="backgroundColour")
		backgroundColourEntry = tk.Entry(settingsFrame)
		backgroundColourEntry.insert(0, options["backgroundColour"])
		self.settingsWidgets.append([backgroundColourLabel, backgroundColourEntry])

		self.guidelinesToggle = tk.IntVar()
		self.guidelinesToggle.set(options["guidelines"])
		guideLinesLabel = tk.Label(settingsFrame, text="Guidelines Toggle")
		guideLinesCheckbox = tk.Checkbutton(settingsFrame, variable = self.guidelinesToggle)
		self.settingsWidgets.append([guideLinesLabel, guideLinesCheckbox])

		guidelineColourLabel = tk.Label(settingsFrame, text="Guideline Colour")
		guidelineColourEntry = tk.Entry(settingsFrame)
		guidelineColourEntry.insert(0, options["guidelineColour"])
		self.settingsWidgets.append([guidelineColourLabel, guidelineColourEntry])

		guidelineFontSizeLabel = tk.Label(settingsFrame, text="Guideline Font Size")
		guidelineFontSizeEntry = tk.Entry(settingsFrame)
		guidelineFontSizeEntry.insert(0, options["guidelineFontSize"])
		self.settingsWidgets.append([guidelineFontSizeLabel, guidelineFontSizeEntry])

		guidelineThicknessLabel = tk.Label(settingsFrame, text="Guideline Thickness")
		guidelineThicknessEntry = tk.Entry(settingsFrame)
		guidelineThicknessEntry.insert(0, options["guidelineThickness"])
		self.settingsWidgets.append([guidelineThicknessLabel, guidelineThicknessEntry])

		fontColourLabel = tk.Label(settingsFrame, text="Grid Font Colour")
		fontColourEntry = tk.Entry(settingsFrame)
		fontColourEntry.insert(0, options["fontColour"])
		self.settingsWidgets.append([fontColourLabel, fontColourEntry])

		noOfPlotsBaseLabel = tk.Label(settingsFrame, text="Number of Plots")
		noOfPlotsBaseEntry = tk.Entry(settingsFrame)
		noOfPlotsBaseEntry.insert(0, options["noOfPlotsBase"])
		self.settingsWidgets.append([noOfPlotsBaseLabel, noOfPlotsBaseEntry])

		for row in range(len(self.settingsWidgets)):
			for i in range(2):
				self.settingsWidgets[row][i].grid(row=row, column=i)

		settingsFrame.pack(padx = 20)

		applyButton = tk.Button(settingsRoot, text="Apply", command=self.applySettings)
		applyButton.pack()

		defaultButton = tk.Button(settingsRoot, text="Restore Default", command = self.defaultOptions)
		defaultButton.pack()

	def applySettings(self):

		# Initalize settings dictionary
		settings = {}

		# Names of the settings; they will always be in this order
		settingNames = ("windowWidth", "gridWidth", "windowHeight", "axisThickness",
		 "axisColour", "plottedColour", "plottedThickness", "backgroundColour", "guidelines",
		"guidelineColour", "guidelineFontSize", "guidelineThickness", "fontColour", "noOfPlotsBase", "noOfPlots")

		for settingNum in range(14):
			
			# If the widget is a text entry, it reads the text.
			if type(self.settingsWidgets[settingNum][1]) is tk.Entry:
				settings[settingNames[settingNum]] = self.settingsWidgets[settingNum][1].get()

			# If the widget is a checkbox, it reads the status of the checkbox variable.
			elif type(self.settingsWidgets[settingNum][1]) is tk.Checkbutton:
				settings[settingNames[settingNum]] = self.guidelinesToggle.get()

		validatedSettings = self.validateSettings(settings)

		if validatedSettings != False:
			with open('options.json', 'w') as optionsFile:
				json.dump(validatedSettings, optionsFile)

			dialogBox = tk.Toplevel()
			dialogBox.title("Maths Graphing Tool")

			dialog = tk.Label(dialogBox, text="Settings Applied\n\nPlease Restart the program for the options to take effect.")
			dialog.pack()

	def validateSettings(self, settings):
		
		valid = True

		try:
			settings["windowWidth"] = int(settings["windowWidth"])
			settings["gridWidth"] = int(settings["gridWidth"])
			settings["windowHeight"] = int(settings["windowHeight"])
			settings["axisThickness"] = int(settings["axisThickness"])
			settings["plottedThickness"] = int(settings["plottedThickness"])
			settings["guidelines"] = int(settings["guidelines"])
			settings["guidelineFontSize"] = int(settings["guidelineFontSize"])
			settings["guidelineThickness"] = int(settings["guidelineThickness"])
			settings["noOfPlotsBase"] = int(settings["noOfPlotsBase"])

			settings["axisColour"] = tuple([int(x) for x in settings["axisColour"].split(" ")])
			settings["plottedColour"] = tuple([int(x) for x in settings["plottedColour"].split(" ")])
			settings["backgroundColour"] = tuple([int(x) for x in settings["backgroundColour"].split(" ")])
			settings["guidelineColour"] = tuple([int(x) for x in settings["guidelineColour"].split(" ")])
			settings["fontColour"] = tuple([int(x) for x in settings["fontColour"].split(" ")])

		except ValueError:
			valid = False

		else:
			if settings["windowWidth"] < 100:
				valid = False

			elif settings["gridWidth"] > settings["windowWidth"]:
				valid = False

			elif settings["windowHeight"] < 100:
				valid = False

			elif settings["axisThickness"] < 1:
				valid = False

			elif settings["plottedThickness"] < 1:
				valid = False

			elif settings["guidelineFontSize"] < 1:
				valid = False

			elif settings["guidelineThickness"] < 1:
				valid = False

			elif settings["noOfPlotsBase"] < 1:
				valid = False

			for colourSetting in ("axisColour", "plottedColour", "backgroundColour", "guidelineColour", "fontColour"):
				for value in settings[colourSetting]:
					if value > 255 or value < 0:
						valid = False

		if valid == False:
			warningRoot = tk.Toplevel()
			warningRoot.title("Invalid Setting")
			warningRoot.resizable(False, False)

			warningLabel = tk.Label(warningRoot, text="One or more of your entered settings are invalid.\n\nPlease ensure that:\n- Size settings are numbers greater than 99.\n- Colours are three numbers between 0 and 255, seperated by a space (eg. 50 50 50).\n- Font sizes are above 0.\n- Thickness sizes are above 0.\n- Number of plots is above 0.\n- All settings are whole numbers, not decimals.")
			warningLabel.pack()
			return False

		elif valid == True:
			return settings

	def defaultOptions(self):

		with open('optionsDefault.json') as optionsFile:
			default = json.load(optionsFile)

		with open('options.json', 'w') as optionsFile:
			json.dump(default, optionsFile)

		dialogBox = tk.Toplevel()
		dialogBox.title("Maths Graphing Tool")

		dialog = tk.Label(dialogBox, text="Settings Applied\n\nPlease Restart the program for the options to take effect.")
		dialog.pack()

	def loadGraphs(self, path):

		examplesRoot = tk.Toplevel()
		examplesRoot.title("Maths Graphing Load Graphs")
		examplesRoot.resizable(False, False)

		titleLabel = tk.Label(examplesRoot, text = "Load Graphs", font=("Helvetica", 16))
		titleLabel.pack()

		examplesFrame = tk.Frame(examplesRoot, borderwidth=1, width=500, height=400)
		examplesFrame.pack_propagate(0)
		examplesFrame.pack(fill="both", expand=True)
		scrollable = tk.Frame(examplesFrame)

		# Initalize the scrollbar and canvas
		examplesScrollbar = tk.Scrollbar(scrollable, orient=tk.VERTICAL)
		examplesScrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=0)
		examplesCanvas = tk.Canvas(scrollable, yscrollcommand=examplesScrollbar.set) # The yscrollcommand attribute links the canvas to the scrollbar
		examplesCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		examplesScrollbar.config(command=examplesCanvas.yview)

		# Set the inital scroll values for the canvas
		examplesCanvas.xview_moveto(0)
		examplesCanvas.yview_moveto(0)

		# The interior frame is created in the canvas, and will contain the widgets which will be moved when the user scrolls
		interior = tk.Frame(examplesCanvas)
		interior_id = examplesCanvas.create_window(0, 0, window=interior, anchor=tk.NW)

		def configureInterior(event):
			# Changes the size of the interior frame and the scrollable region of the canvas
			size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
			examplesCanvas.config(scrollregion="0 0 %s %s" % size)
			if interior.winfo_reqheight() != examplesCanvas.winfo_width():
				examplesCanvas.config(width=interior.winfo_reqwidth())

		# The interior frame will call the function configureInterior whenever it changes size
		interior.bind('<Configure>', configureInterior)

		def configureCanvas(event):
			# Changes the interior frame's width to the width of the canvas
			if interior.winfo_reqwidth() != examplesCanvas.winfo_width():
				examplesCanvas.itemconfigure(interior_id, width=examplesCanvas.winfo_width())

		# The canvas will call configureCanvas whenever it changes size
		examplesCanvas.bind('<Configure>', configureCanvas)

		scrollable.pack(fill=tk.BOTH, expand=1)

		# Get a list of only the files in the current directory.
		fileNames = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]

		for fileName in fileNames:
			# The full path of the file
			filePath = os.path.join(path , fileName)

			with open(filePath) as graphFile:
				# Reading the contents of the file
				graphData = json.load(graphFile)

			# Create the gui for the file in the interior frame
			graphFrame = tk.Frame(interior, borderwidth=1, relief="solid", width = 400, height = 50)
			graphFrame.pack_propagate(0)
			graphFrame.grid_propagate(0)
			graphEquationLabel = tk.Label(graphFrame, text=graphData["equation"], font=("Consolas", 12))
			graphDescriptionLabel = tk.Label(graphFrame, text=graphData["description"], font=("Helvetica", 11))
			graphButton = tk.Button(graphFrame, text="Select", command=lambda equation=graphData["equation"]: self.getEquationInput(equation))

			graphEquationLabel.grid(row=0,column=0, padx=5)
			graphDescriptionLabel.grid(row=0,column=1, padx=5)
			graphButton.grid(row=0,column=2, padx=5, sticky=tk.E)
			graphFrame.pack()

	class equationFrame():
		# Class that stores the equation object and the equation frame so that they are linked
		def delete(self):
			# Deletes the equation object and removes it's corrosponding frame
			self.frame.pack_forget()
			self.frame.destroy()

			equations.equationList.remove(self.linkedEquation)

			if len(equations.equationList) > 0:
				equations.calculateNoOfPlots( len(equations.equationList ) )

		def toggle(self):
			# Toggle the visibility of the equation
			self.linkedEquation.visible = not self.linkedEquation.visible

	def newEquation(self):
		self.getEquationInput(self.graphEntry.get("1.0", tk.END))

	def getEquationInput(self, equation):
		#Get the user's equation input and create the frame for the 'currently graphed' 
		try:
			eqFrame = gui.equationFrame()
			newEquation = equations.createEquation(equation, eqFrame)
			newEquation.solve(0)
		except (NameError, sympy.SympifyError, SyntaxError):
			warningRoot = tk.Toplevel()
			warningLabel = tk.Label(warningRoot, text = "Invalid Graph\n\nPlease refer to the tutorial", font=("Helvetica", 15))
			warningLabel.pack()

			equations.equationList.remove(newEquation)
			del eqFrame
		else:
			eqFrame.frame = tk.Frame(self.interior, height=200, borderwidth=1, relief="solid")
			eqFrame.text = tk.Text(eqFrame.frame, width = 12, height = 1, font=("Helvetica", 15))

			eqFrame.text.insert('end', equation)
			eqFrame.text.configure(state='disabled')
			eqFrame.text.pack(side=tk.LEFT)

			eqFrame.equationDeleteButton = tk.Button(eqFrame.frame, text="Delete", command=eqFrame.delete)
			eqFrame.equationCheckbox = tk.Button(eqFrame.frame, text="Toggle", command=eqFrame.toggle)

			eqFrame.equationDeleteButton.pack(side=tk.RIGHT)
			eqFrame.equationCheckbox.pack(side=tk.RIGHT, ipadx=3)

			eqFrame.frame.pack(fill=tk.X, expand=False, ipadx=1, ipady=5, pady=1)

	def saveGraphs(self):

		bannedCharacters = ["<", ">", ":", '"', "/", "\"", "|", "?" ,"*"]

		for graph in equations.equationList:
			graphData = {}

			graphData["equation"] = graph.equationString

			nameWindow = tk.Toplevel()

			nameLabel = tk.Label(nameWindow, text="What do you wish to save {} as?".format(graphData["equation"]), font=("Helvetica", 16))
			nameLabel.pack()

			nameEntry = tk.Entry(nameWindow, font=("Helvetica", 11))
			nameEntry.pack()

			wait = tk.IntVar()
			name = None

			# Functions for the buttons
			def assignName():
				nonlocal name, wait
				name = nameEntry.get()
				#Changes the wait variable, so the program continues
				if any(character in bannedCharacters for character in name):
					warningRoot = tk.Toplevel()
					warningLabel = tk.Label(warningRoot, text = 'Invalid Input\n\nA filename cannot contain the following characters: < > : " / \ | ? *', font = ("Helvetica", 16))
					warningLabel.pack()
				else:
					wait.set(1)

			def assignDescription():
				nonlocal graphData, wait
				graphData["description"] = nameEntry.get()
				wait.set(2)

			nameEntryButton = tk.Button(nameWindow, text="Save", command=assignName)
			nameEntryButton.pack()

			# This will make the program wait until the variable 'wait' changes, so in this case, when the user presses 'Save'
			nameWindow.wait_variable(wait)

			nameLabel.configure(text="Please write a short description of the graph {}".format(graphData["equation"], font=("Helvetica", 16)))
			nameEntry.delete(0, "end")

			nameEntryButton.configure(command=assignDescription)

			nameWindow.wait_variable(wait)

			# Writing the dictionary to the file name specified, using a json format.
			with open("./Graphs/{}.json".format(name), 'w') as graphFile:
				json.dump(graphData, graphFile)

			nameWindow.destroy()

class gridController():
	def __init__(self):
		self.cameraX, self.cameraY = (0, 0) #Initalize the camera starting coordinates
		self.cameraWidth, self.cameraHeight = (20, 20) #Initalize the width and height the camera can see.
		self.graphSurface = pygame.display.set_mode( (options["windowWidth"],options["windowHeight"]) )
		self.graphSurface.fill( (255, 255, 255 ) )

		self.pixelDX = (self.cameraWidth/ options["gridWidth"])
		self.pixelDY = (self.cameraHeight/ options["windowHeight"])

		self.numXMarkers = 10
		self.numYMarkers = 10

		self.gridFont = pygame.font.SysFont("monospace", options["guidelineFontSize"])

	def getGridCoordinate(self, coordsTuple):
		# Take an (x, y) tuple on the screen and return it's x, y value on the cartesian grid
		x, y = coordsTuple #Unpack tuple
		gridX = self.pixelDX*(x - options["windowWidth"]/2) + self.cameraX
		gridY = self.pixelDY*(y - options["windowHeight"]/2) - self.cameraY
		return ( gridX, gridY )

	def getScreenCoordinate(self, coordsTuple):
		# Take an (x, y) tuple on the grid and return it's x, y value on the screen
		x, y = coordsTuple
		screenX = ((x-self.cameraX)/self.pixelDX) + options["gridWidth"]/2
		screenY = ((-y-self.cameraY)/self.pixelDY) + options["windowHeight"]/2
		return ( screenX, screenY )

	def drawGrid(self):
				# Draws the entire grid

				# graphSurface is cleared
		self.graphSurface.fill(options["backgroundColour"])

		# Finds where the screen coordinate of where (0, 0) is
		screenXZero, screenYZero = self.getScreenCoordinate( (0, 0) )

		# Calls the calculate markers function to calulate the coordinates of the x and y markers
		xMarkers = self.calculateMarkers( (self.cameraX - 0.5*self.cameraWidth), (self.cameraX + 0.5*self.cameraWidth), self.numXMarkers)
		yMarkers = self.calculateMarkers( (self.cameraY - 0.5*self.cameraHeight), (self.cameraY + 0.5*self.cameraHeight), self.numYMarkers)

		
		for x in xMarkers:
			if x != 0:
				# Find the screen coordinate of the marker
				screenX, screenY = self.getScreenCoordinate( (x, 0) )

				# Draws the guidelines for the marker if toggled on
				if options["guidelines"] == 1:
					pygame.draw.line(self.graphSurface, options["guidelineColour"], (screenX,0), (screenX, options["windowHeight"]), 1)

				markerLabel = self.gridFont.render(str(x), 1, options["fontColour"])
				textWidth, textHeight = self.gridFont.size(str(x))

				self.graphSurface.blit(markerLabel, (screenX-textWidth//2, screenY) )

		for y in yMarkers:
			if y != 0:
				screenX, screenY = self.getScreenCoordinate( (0, -y) )
				if options["guidelines"] == 1:
					pygame.draw.line(self.graphSurface, options["guidelineColour"], (0,screenY), (options["gridWidth"], screenY), 1)

				markerLabel = self.gridFont.render(str(y), 1, options["fontColour"])
				textWidth, textHeight = self.gridFont.size(str(y))

				self.graphSurface.blit(markerLabel, (screenX, screenY-textHeight//2) )

		# Draw the axis lines onto the grid
		pygame.draw.line(self.graphSurface, options["axisColour"], (screenXZero,0), (screenXZero,options["windowHeight"]), options["axisThickness"] )
		pygame.draw.line(self.graphSurface, options["axisColour"], (0,screenYZero), (options["gridWidth"],screenYZero), options["axisThickness"] )

		self.drawEquations()

				# Updates the display
		pygame.display.flip()
		gui.root.update()

	def calculateMarkers(self, min, max, numOfMarkers):
				# Calculates where the markers should be placed
		Range = self.round( max - min )
		markerInterval = self.round( (Range / (numOfMarkers)))
		roundedMin = math.floor(min/markerInterval) * markerInterval
		roundedMax = math.ceil(max/markerInterval) * markerInterval

		markerCoords = []
		for i in numpy.arange(roundedMin, roundedMax+markerInterval, markerInterval):
			# Round the result to the same order of magnitude as the marker interval to prevent floating point errors
			markerCoords.append( round(i, -int(math.floor(math.log10(markerInterval)))))

		return markerCoords

	def round(self, number):
		# Round the number given to the nearest 1, 2 or 5 and their power of ten multiples

		# Finds the order of magnitude of the number
		exponent = math.floor(math.log10(number))
		fraction = number/(10**exponent)

		if fraction < 1.5:
			fraction = 1
		elif fraction < 3:
			fraction = 2
		elif fraction < 7:
			fraction = 5
		else:
			fraction = 10

		return (fraction * (10**exponent))

	def drawEquations(self):
		# Draw every equation

		for equation in equations.equationList:

			if equation.visible:

				# Generate a list of evenly spaced numbers from the left side of the screen to the right side.
				xValues = numpy.linspace( (grid.cameraX - grid.cameraWidth//2)-1 , (grid.cameraX + grid.cameraWidth//2)+1, options["noOfPlots"]).tolist()
				yValues = []

				for xValue in xValues:

					solution = equation.solve(xValue)

					if solution == [sympy.zoo] or solution == [] or solution == None:
						# sympy.zoo is the result of dividing something by zero, when this happens
						# the solution at that x-value is undefined and cannot be plotted.
						pass

					else:

						yValues.append(solution[0])

				# This is outside the loop to avoid unnecessary calculations.
				x, y = grid.getScreenCoordinate( (xValues[0], yValues[0]) )

				for i in range(len(xValues)-1):

					if i+1 >= len(yValues):
						break

					nextX, nextY = grid.getScreenCoordinate( (xValues[i+1], yValues[i+1]) )

					if nextY > 10000:
						nextY = 10000
					elif nextY < -10000:
						nextY = -10000

					pygame.draw.line(grid.graphSurface, options["plottedColour"], (x, y), (nextX, nextY), options["plottedThickness"])


					x, y = nextX, nextY

class inputHandler():
	def __init__(self):
		self.keys = {
			"m1": 0, #left
			"m2": 0, #right
			"m3": 0 #middle
		}

	def handleInput(self):
				# Checks for user input inside of the grid and responds accordingly

				# Get the list of user inputs
		eventList = pygame.event.get()

				# Get the current state of the mouse
		(self.keys["m1"], self.keys["m2"], self.keys["m3"]) = pygame.mouse.get_pressed()

		for event in eventList:

			if event.type == pygame.QUIT:
				pygame.quit()
				gui.root.destroy()
				sys.exit(0)

			if event.type == pygame.MOUSEBUTTONDOWN:
								# If the user has the left mouse button pressed, it will call get_rel()
								# which calculates the difference in the position of the mouse since the
								# last time it has been called.
				if event.button == 1:
					pygame.mouse.get_rel()

								# If the user scrolls up or down, the zoom method is called with the corrosponding input
				if event.button == 5:
					self.zoom("out")

				if event.button == 4:
					self.zoom("in")

		if self.keys["m1"] == 1:
			self.moveGraph()

	def moveGraph(self):
		(x, y) = pygame.mouse.get_rel()

				# Converts the screen coordinates of the mouse movement to graph coordinates.
		xMovement = x*grid.pixelDX
		yMovement = y*grid.pixelDY

		grid.cameraX -= xMovement
		grid.cameraY -= yMovement

	def zoom(self, direction):
				# Adjusts the width and height of the camera and adjusts the pixelDX and pixelDY accordingly.
		if direction == "in":

			grid.cameraWidth -= 0.1* grid.cameraWidth
			grid.cameraHeight -= 0.1* grid.cameraHeight

		else:

			grid.cameraWidth += 0.1* grid.cameraWidth
			grid.cameraHeight += 0.1* grid.cameraHeight

		grid.pixelDX = grid.cameraWidth / options["gridWidth"]
		grid.pixelDY = grid.cameraHeight / options["windowHeight"]

class equationController():
	def __init__(self):
		self.equationList = []

	def createEquation(self, function, frame):
		# Create a new equation object and links the frame parameter to the equation
		newEquation = equation(function)
		frame.linkedEquation = newEquation
		newEquation.frame = frame
		self.equationList.append(newEquation)
		self.calculateNoOfPlots( len(self.equationList ) )

		return newEquation

	def calculateNoOfPlots(self, equations):
		# Update the amount of calculations to make for each equation, when there are n equations

		options["noOfPlots"] = (options["noOfPlotsBase"] * (math.log(equations) + 0.5772156649 + 1/(2*equations) - 1/(12*equations**2) )) / equations
		options["noOfPlots"] = round(options["noOfPlots"])

class equation():
	def __init__(self, function):
		# Split the equation into the left-hand side and the right-hand side
		self.visible = True

				# Initalize the sympy symbols
		self.x = sympy.symbols("x")
		self.y = sympy.symbols("y")

		self.equationString = str(function).rstrip()

		sides = function.replace(" ", "").lower().split("=")
		self.leftSide = sides[0]
		self.rightSide = sides[1]

				# Create a sympy equation and solve it for y.
		self.fx = sympy.Eq( sympy.sympify(self.leftSide), sympy.sympify(self.rightSide) )
		self.fx = sympy.solve(self.fx, self.y)

		for i in range(len(self.fx)):
			self.fx[i] = str(self.fx[i]).replace("-x**2", "-(x**2)")

	def solve(self, xValue):
		#Solve the equation for some x value.
		solutions = []

		for equation in self.fx:
			x = xValue

			try:
				solutions.append( eval( str(equation) ) )
			except ValueError:
				pass

		if solutions != []:
			return solutions

def readOptions():
	global options

	with open('options.json') as optionsFile:
		data = json.load(optionsFile)
		options = data

def initApplication():
	global grid, gui, input, equations

	readOptions()

	gui = guiController()

	os.environ['SDL_WINDOWID'] = str(gui.gridFrame.winfo_id())
	if platform.system() == "Windows":
		os.environ['SDL_VIDEODRIVER'] = 'windib'
	pygame.init()

	grid = gridController()
	input = inputHandler()
	equations = equationController()
	mainLoop()

def mainLoop():

	while True:
		grid.drawGrid()

		gui.root.update_idletasks()
		gui.root.update()

		input.handleInput()

	pygame.quit()
	sys.exit(0)

initApplication()

