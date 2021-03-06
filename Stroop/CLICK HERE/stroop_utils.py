stroop_utils.py

import os, glob, pickle, copy

def generateWords():
	abuse = []
	positive = []	
	neutral = []
	Ns = []	
	fakeabuse = []
	fakepositive = []	
	fakeneutral = []
	fakeNs = []	

	f = open(os.path.join(os.getcwd(), "data", "abuse.txt"), 'r')
	for lines in f.readlines():
		abuse.append(lines.strip())
	f.close()

	f = open(os.path.join(os.getcwd(), "data", "positive.txt"), 'r')
	for lines in f.readlines():
		positive.append(lines.strip())
	f.close()	

	f = open(os.path.join(os.getcwd(), "data", "neutral.txt"), 'r')
	for lines in f.readlines():
		neutral.append(lines.strip())
	f.close()	
			
	f = open(os.path.join(os.getcwd(), "data", "Ns.txt"))
	for lines in f.readlines():
		Ns.append(lines.strip())
	f.close()	

	f = open(os.path.join(os.getcwd(), "data", "fakeabuse.txt"), 'r')
	for lines in f.readlines():
		fakeabuse.append(lines.strip())
	f.close()

	f = open(os.path.join(os.getcwd(), "data", "fakepositive.txt"), 'r')
	for lines in f.readlines():
		fakepositive.append(lines.strip())
	f.close()	

	f = open(os.path.join(os.getcwd(), "data", "fakeneutral.txt"), 'r')
	for lines in f.readlines():
		fakeneutral.append(lines.strip())
	f.close()	
			
	f = open(os.path.join(os.getcwd(), "data", "fakeNs.txt"))
	for lines in f.readlines():
		fakeNs.append(lines.strip())
	f.close()	

	return abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs

def classify(word, abuse, positive, neutral, Ns, fakeabuse, fakepositive, fakeneutral, fakeNs):
	if word in abuse:
		return "a"
	elif word in positive:
		return "p"
	elif word in neutral:
		return "n"
	elif word in Ns:
		return "f"
	elif word in fakeabuse:
		return "aD"
	elif word in fakepositive:
		return "pD"
	elif word in fakeneutral:
		return "nD"
	elif word in fakeNs:
		return "fD"	
