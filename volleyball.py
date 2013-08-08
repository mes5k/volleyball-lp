#!/usr/bin/python

import math
import sys

if len(sys.argv) != 5:
	print "USAGE: volleyball.py <teams.csv> <gyms.csv> <exclusions.cvs> <linkages.csv>"
	exit(1)

# read teams.csv
f = open(sys.argv[1])
teamlines = f.readlines()
f.close()

teamList = []

for l in teamlines:
	teamList.append( l.split(',') )

# read gyms.csv
f = open(sys.argv[2])
gymlines = f.readlines()
f.close()

gymMatrix = []
for l in gymlines:
	gymMatrix.append( l.split(',') )

# read exclusions.csv
f = open(sys.argv[3])
exlines = f.readlines()
f.close()

exclusionMap = {} 
for l in exlines:
	a = l.split(',')
	exclusionMap[a[0]] = a[1]

# read linkages.csv
f = open(sys.argv[4])
linkages = f.readlines()
f.close()

def getHomePairs():
	pairs = []
	for l in linkages:
		ll = l.strip().split(',')
		pairs.append( (ll[0],ll[1]) )
	return pairs

def getGyms():
	x = gymMatrix[5]
	y = x[1:-1] 
	z = [int(i) for i in y]
	return z 

def getDivisions():
	divs = []
	numDivs = int(teamList[0][0])
	teams = teamList[2:]
	for d in range(1,numDivs+1):
		div = []
		for t in teams:
			if t[2] == "division " + str(d):
				div.append(int(t[0]))
		divs.append(div)
	return divs

def getTeams():
	tl = teamList[2:]
	return [int(t[0]) for t in tl]

# index sets
weeks = [i+1 for i in xrange(10)] 

teams = getTeams() 
divisions = getDivisions() 

gyms = getGyms() 

homePairs = getHomePairs() 
homeTeamWeek = [] #[(1,4),(2,5)] # (team,week)
specificMatches = [] #[(1,2,3)] # (team,team,week)

# decision variables
def game(i,j,t):
	return "game_team" + str(i) + "_team" + str(j) + "_week" + str(t);

def gymSelection(t,i,g):
	return "gymSelection_week" + str(t) + "_team" + str(i) + "_gym" + str(g);

def z(i,j):
	return "z_" + str(i) + "_" + str(j) 

def m_p(i,j):
	return "m_p_" + str(i) + "_" + str(j)

def m_pp(i,j):
	return "m_pp_" + str(i) + "_" + str(j)

def m(i,j):
	return m_p(i,j) + " - " + m_pp(i,j) 

def abs_m(i,j):
	return m_p(i,j) + " + " + m_pp(i,j) 

# parameters
def homeGym(t,i,g):
	if g in exclusionMap and exclusionMap[g] == t:
		return 0
	else:
		return int(gymMatrix[i+7][g])

def expectedGames(i,j):
	if teamList[i+1][2] == teamList[j+1][2]:
		return 1
	else:
		return 0

# objective

def objectiveFunction():
	g = []
	for i in teams:
		for j in teams:
			if ( i != j ):
				g.append( abs_m(i,j) )
				#g.append( m_pp(i,j) )
	#print "max: " + " + ".join(g) + ";"
	print "min: + " + " + ".join(g) + ";"

# constraints
def playAllGames():
	print "// playAllGames"
	# enumerate the combinations
	for i in teams:
		for j in teams:
			# create the inequality sum for each combination
			if (i != j):
				tgames = []
				for t in weeks:
					tgames.append( game(i,j,t) ) 
				print " + ".join(tgames) + " = " + str(expectedGames(i,j)) + ";"

def eitherHomeOrAway():
	print "// eitherHomeOrAway"
	# enumerate the combinations
	for j in teams:
		for t in weeks:
			# create the inequality for each combination
			lhs = []
			rhs = []
			for i in teams:
				if ( i != j ):
					lhs.append(game(i,j,t))
					rhs.append(game(j,i,t))
			print " + ".join(lhs) + " <= 1 - " + " + ".join(rhs)	 + ";"

def useOneHomeGym():
	print "// useOneHomeGym"
	for g in gyms:
		for t in weeks:
			sel = []
			for i in teams:
				sel.append( gymSelection(t,i,g) )
			print " + ".join(sel) + " <= 1" + ";"


def gymSelectionMaxRequirement():
	print "// gymSelectionMaxRequirement"
	for g in gyms:
		for t in weeks:
			for i in teams:
				jsum = []
				for j in teams:
					if (i != j):
						jsum.append(game(i,j,t) + " " + str(homeGym(t,i,g)))
				print  gymSelection(t,i,g) + " <= " + " + ".join(jsum) + ";"

def allGameMustHaveGym():
	print "// allGameMustHaveGym"
	for t in weeks:
		for i in teams:
			games = []
			gymSels = []
			for j in teams:
				if ( i != j ):
					games.append(game(i,j,t))
			for g in gyms:
				gymSels.append(gymSelection(t,i,g));
			print " + ".join(games) + " = " + " + ".join(gymSels) + ";"

def noConsecutiveHomeGames():
	print "// noConsecutiveHomeGames"
	for x in range(len(weeks)):
		if ( x < 2 ):
			continue
		for i in teams:
			thisWeek = []
			previous = []
			for j in teams:
				if (i != j):
					thisWeek.append(game(i,j,weeks[x]))
					previous.append(game(i,j,weeks[x-1]))
					previous.append(game(i,j,weeks[x-2]))
			print " + ".join(thisWeek) + " <= 2 - " + " - ".join(previous)  + ";"

def noConsecutiveAwayGames():
	print "// noConsecutiveAwayGames"
	for x in range(len(weeks)):
		if ( x < 2 ):
			continue
		for j in teams:
			thisWeek = []
			previous = []
			for i in teams:
				if (i != j):
					thisWeek.append(game(i,j,weeks[x]))
					previous.append(game(i,j,weeks[x-1]))
					previous.append(game(i,j,weeks[x-2]))
			print " + ".join(thisWeek) + " <= 2 - " + " - ".join(previous)  + ";"

def consecutiveHomeWithBye():
	print "// consecutiveHomeWithBye"
	for x in range((len(weeks)-3)):
#		if ( x >= len(weeks) - 3 ):
#			continue
		for i in teams:
			g = []
			for j in teams:
				if (i != j):
					g.append(game(i,j,weeks[x]))
					g.append(game(i,j,weeks[x+1]))
					g.append(game(i,j,weeks[x+2]))
					g.append(game(i,j,weeks[x+3]))
			print " + ".join(g) + " >= 1" + ";"

def consecutiveAwayWithBye():
	print "// consecutiveAwayWithBye"
	for x in range((len(weeks)-3)):
#		if ( x >= len(weeks) - 3 ):
#			continue
		for j in teams:
			g = []
			for i in teams:
				if (i != j):
					g.append(game(i,j,weeks[x])) 
					g.append(game(i,j,weeks[x+1]))
					g.append(game(i,j,weeks[x+2]))
					g.append(game(i,j,weeks[x+3]))
			print " + ".join(g) + " >= 1"  + ";"

def oneByeInARow():
	print "// oneByeInARow"
	for x in range(len(weeks)):
		if ( x >= len(weeks) - 1 ):
			continue
		for i in teams:
			g = []
			for j in teams:
				if (i != j):
					g.append(game(i,j,weeks[x]))
					g.append(game(i,j,weeks[x+1]))
					g.append(game(j,i,weeks[x]))
					g.append(game(j,i,weeks[x+1]))
			print " + ".join(g) + " >= 1" + ";"

#
# Note that this is my interpretation of bothPlayHome, because I believe
# that the document contains a typo and mistakenly duplicates oneByeInARow. 
#
def bothPlayHome():
	print "// bothPlayHome"
	for t in weeks:
		for g in gyms:
			for p in homePairs:
				i = p[0]
				j = p[1]
				print gymSelection(t,i,g) + " = " + gymSelection(t,j,g) + ";"
def mustPlayHome():
	print "// mustPlayHome"
	g = []
	for j in teams:
		for h in homeTeamWeek:
			i = h[0]
			t = h[1]
			g.append(game(i,j,t))
	if len(g) > 0:
		print " + ".join(g) + " = 1" + ";"

def mustSchedules():
	print "// mustSchedules"
	for s in specificMatches:
		i = s[0]
		j = s[1]
		t = s[2]
		if (i != j):
			print game(i,j,t) + " = 1" + ";"

def maxGamesForDivisions():
	for x in range(len(divisions)):
		d = divisions[x]
		print "// maxGamesForDivision" + str(x+1)
		maxGames = len(d) * (len(d)-1)
		g = []
		for i in d:
			for j in d:
				if (i != j):
					for t in weeks:
						g.append(game(i,j,t))
		print " + ".join(g) + " = " + str(maxGames) + ";"


def zij():
	print "// zij"
	for i in teams:
		for j in teams:
			if ( i != j ):
				g = []
				for t in weeks:
					g.append( game(i,j,t) + " " + str(t) )
				print z(i,j) + " = " + " + ".join(g) + ";"

def mij():
	print "// mij"
	for i in teams:
		for j in teams:
			if ( i != j ):
				print m(i,j) + " = " + z(i,j) + " - " + z(j,i) + ";"

def bound_gameSpread():
	print "// bound gameSpread"
	for i in teams:
		for j in teams:
			if ( i != j ):
				print m_p(i,j) + " >= 0;"
				print m_pp(i,j) + " >= 0;"
				print z(i,j) + " >= 0;"

def declare_games():
	print "// declare games"
	for i in teams:
		for j in teams:
			if ( i != j ):
				for t in weeks:
					print "bin " + game(i,j,t) + ";"

def declare_gymSelection():
	print "// declare gymSelection"
	for t in weeks:
		for i in teams:
			for g in gyms:
				print "bin " + gymSelection(t,i,g) + ";"

def declare_gameSpread():
	print "// declare gameSpread"
	for i in teams:
		for j in teams:
			if ( i != j ):
				print "int " + m_p(i,j) + ";"
				print "int " + m_pp(i,j) + ";"
				print "int " + z(i,j) + ";"

objectiveFunction()
playAllGames()
eitherHomeOrAway()
useOneHomeGym()
gymSelectionMaxRequirement()
allGameMustHaveGym()
noConsecutiveHomeGames()
noConsecutiveAwayGames()
consecutiveHomeWithBye()
consecutiveAwayWithBye()
oneByeInARow()
bothPlayHome()
mustPlayHome()
mustSchedules()
maxGamesForDivisions()
zij()
mij()
bound_gameSpread()
declare_games()
declare_gymSelection()
declare_gameSpread()

#print teams
#print divisions
#print gyms
#print gymMatrix
#def asdf():
#	for g in gyms:
#		for t in weeks:
#			for i in teams:
#				print gymSelection(t,i,g) + "  " + str(homeGym(t,i,g))
#asdf()
