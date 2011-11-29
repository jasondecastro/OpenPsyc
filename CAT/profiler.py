#! /usr/env/python

#assessment.py
import VisionEgg
#VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport
from VisionEgg.FlowControl import Presentation, FunctionController, TIME_SEC_ABSOLUTE, FRAMES_ABSOLUTE
from VisionEgg.Textures import *
import pickle
import time
import random

from pygame.locals import *

import sys
import os
import copy
import adder

sys.path.append(os.path.split(os.getcwd())[0])

from problem import *
import shuffler
from handlers import *
import subject
from experiments import printWord, printText
from mongoTools import MongoAdmin

"""
phase 1 - go up until we get to operands of size > 35, then go back down
phase 2 - determine mem/calc line and count the problems we have
phase 3 - use mem/calc line to fill in the missing problems (select a few more in case verification doesn't work out)
phase 4 - verify all problems we have

return to phase 2 if phase 3 doesn't completed sucessfully
"""

#FUNCTIONS
#strat control, mouse clicks
def diff_handler(event):
	global strat

	key = event.key	
	
	if key == pygame.locals.K_SPACE:
		strat = 'mem'
		p2.parameters.go_duration = (0, 'frames')

	
def key_handler(event):
	global correct 
	global ACC
	global RT
	key = event.key

	print event.key

	RT = p.time_sec_since_go
	
	if key == 308:
		if correct == "left":
			ACC = 1
		else:
			ACC = 0
		p.parameters.go_duration=(0, 'frames')
	elif key == 307:
		if correct == "right":
			ACC = 1
		else:
			ACC = 0
		p.parameters.go_duration=(0, 'frames')


def pause_handler(event):
	global pause
	if event.key == K_SPACE:
		print "LET'S DO SOME MATH"
		pause.parameters.go_duration = (0, 'frames')

###COLLECT EXPERIMENT INFO
myArgs = sys.argv

try:
	sid = str(myArgs[1])
except:
	sid = 666

#create subject
subject = subject.Subject(sid, 1, 1, "Assessment")

try:
	low = int(myArgs[2])
	high = int(myArgs[3])
except:
	n1 = 2
	n2 = 3

try:
	operation = str(myArgs[4])
except:
	operation = '+'

###VARIABLES

#settings variables
problemTime = 1.25 #how long the program stays on the screen
blankTime = 1 #pause between strategy report and next problem
diffTime = 2.5 #how long the strategy response appears for
stepSize = [1,2,3,4] #size of step to take in problem space

#state variables
done = False
trial = 0 #trial number
phase = 1 #phase of the experiment
direction = "up" #direction of operands
maxOp = 35 #maximum operand size
memCount = 20
calcCount = 40

###SET SCREEN
screen = get_default_screen()
screen.parameters.bgcolor = (0, 0, 0)
pygame.font.init()

###UNCHANGING STIMULI

#strat selection
fixText, fixCross = printWord(screen, '', 60, (255, 255, 255))

#generate texts
strat2 = "\n\nDescribe your strategy"
stratText, stratPort = printText(screen, strat2, 60, (255, 255, 255))

db = "mri_test"

problems = Problems(db, sid, "addition")

#strat selection
startText, startCross = printWord(screen, 'Press the SPACEBAR to start', 60, (255, 255, 255))

pause = Presentation(go_duration=('forever', ), viewports=[startCross])
pause.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, pause_handler)]  
pause.go()

while not done:
	trial += 1
	strat = 'calc'

	#select operands based on phase
	if trial != 1:
		if phase == 1:
			if direction == "up":
				n1 += random.choice(stepSize)
				n2 += random.choice(stepSize)
				#if we've reached our maximum operand size
				if n1 >= maxOp and n2 >= maxOp:
					direction = "down"
			else:
				n1 -= random.choice(stepSize)
				n2 -= random.choice(stepSize)
				if n1 <= 4 and n2 <= 4:
					phase = 2

		elif phase == 2:
			#update current counts
			mo, ms = problems.stratReport('mem')
			co, cs = problems.stratReport('calc')
			
		elif phase == 3:
			counts = problems.getCounts()
			while phase == 3:
				needMem = memCount - counts['tmem'] + 5
				needCalc = memCount - count['tcalc'] + 5
				if needMem > 0 and needCalc > 0:
					#pick which strat to search for				
					s = random.choice(['mem', 'calc'])
					p = problems.suggestProblem(s)
				elif needMem > 0:
					#search for mems
					p = problems.suggestProblem('mem')
				elif needCalc > 0:
					#search for calcs
					p = problems.suggestProblem('calc')
				else:
					phase = 4

		elif phase == 4:
			temp = problems.getTemp()
			if temp:
				p = temp
			else:
				phase = 5
		#probably should do some last check here and redirect if necessary
		elif phase == 5:
			print "Experiment Complete :)"
			done = True
		else:
			raise Exception("Phase %s WTF man, that ain't right (should be 1-4)" % phase)


	#get problem info and data
	problem = Problem([n1, n2], operation = operation)
	ns = problem.row['ns']
	n1 = ns[0]
	n2 = ns[1]
	soln = problem.row['solution']	
	lastSoln = copy.deepcopy(soln)

	#record problem operands, solution, and id
	subject.inputData(trial, "n1", n1)
	subject.inputData(trial, "n2", n2)
	subject.inputData(trial, "problem", "%s" % problem)
	subject.inputData(trial, "solution", soln)

	#prep the problem for display
	random.shuffle(ns)
	problem_string = "%s %s %s = ?" % (ns[0], operation, ns[1])

	#select the distractor
	distractor = problem.getDistractor()
	side = random.choice(['l', 'r'])
	if side == "l":
		correct = "left"
		L = str(soln)
		R = distractor
	elif side == "r":
		correct = "right"
		L = distractor
		R = str(soln)
	
	#record distractor info
	subject.inputData(trial, "distractor", distractor)
	subject.inputData(trial, "dist_side", side)

	#vision egg display stuff
	probText, probPort = printWord(screen, problem_string, 60, (255, 255, 255))
	vp, vr = printText(screen, "%s                                                 %s" % (L, R), 60, (255, 255, 255))
	fixText, fixCross = printText(screen, '', 60, (255, 255, 255))

	#experimenter info on the terminal
	print "-------------------------------------"
	print "PROBLEM : %s" % problem
	print "SOLUTION : %s" % soln
	print "-------------------------------------"

	#BLOCK 1 - PROBLEM, BLANK & POSSIBLE SOLUTIONS
	p4 = Presentation(go_duration=(problemTime, 'seconds'), viewports=[probPort])
	p4.go()

	p3 = Presentation(go_duration=(blankTime, 'seconds'), viewports=[fixCross])
	p3.go()

	p = Presentation(go_duration=('forever', ), viewports=[vr])
	p.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, key_handler)]  
	p.go()

	
	subject.inputData(trial, "RT", RT)
	subject.inputData(trial, "ACC", ACC)
	
	if diffTime > 1.5:
		diffTime -= .1

	#BLOCK 2 - strat SELECTION
	p2 = Presentation(go_duration=(diffTime, 'seconds'), viewports=[stratPort])
	p2.parameters.handle_event_callbacks=[(pygame.locals.KEYDOWN, diff_handler)]        
	p2.go()
	
	#BLOCK 3 - BLANK SCREEN
	p3 = Presentation(go_duration=(0.5, 'seconds'), viewports=[fixCross])
	p3.go()

	subject.inputData(trial, 'strat', strat)
	
	response = {'trial': trial, 'RT' : RT, 'ACC' : ACC, 'strat' : strat}

	problem.addResponse(response)
	problems.append(problem)
	
	subject.printData()

#save sub
subject.printData()

subject.preserve()
