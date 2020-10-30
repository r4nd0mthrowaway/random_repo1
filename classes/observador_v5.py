#!/usr/bin/python
#coding: utf-8

# Autor: Carlos Henrique Ritzmann
# Data: 11/09/2020

from copy import copy as cp, deepcopy as dcp

# Transition function of an nondeterministic automaton
def Fnd (R, x, e):
	choices = []

	for t in R[3]:
		if (t[0] == x and t[1] == e):
			choices.append(t[2])

	return choices

# ε-reach of a state x to be the set of all states that can be reached
# from x by following transitions labeled by ε in the state transition
# diagram
def Reach (R, x, e, choices=None, isSet=False):
	if (choices is None):
		choices = []

		if (isSet):
			for s in x:
				choices.append(s)
		else:
			choices.append(x)


	if (isSet):
		for s in x:
			for target in Fnd(R, s, e):
				if (target not in choices):
					choices.append(target)
					Reach(R, target, e, choices)
	else:
		for target in Fnd(R, x, e):
			if (target not in choices):
				choices.append(target)
				Reach(R, target, e, choices)

	return choices

def GetInitState (R):
	for s in R[1]:
		if (s[2] == 'inicial'):
			return s[0]

	return None

def Cmp (l1, l2):
	if (len(l1) == len(l2)):

		for o in l1:
			if (o not in l2):
				return False

		return True
	else:
		return False

def inside (elem, ls):
	# print '\n\n----------------------------------'
	# print 'Cmp: ', elem, '\n'
	for e in ls:
		# print '  -> ', e
		if (Cmp(elem, e)):
			# print '    => TRUE'
			return True

	# print '    => FALSE'
	return False

def isTransInside (trans, ls):
	for t in ls:
		if (Cmp(trans[0], t[0]) and Cmp(trans[2], t[2]) and trans[1] == t[1]):
			return True
	return False

def Observer (R, ue):
	O = ['Observer('+str(R[0])+')', [], [], []]
	x0 = GetInitState(R)

	# Step 1
	O[1] = [ Reach(R, x0, ue) ]

	for e in R[2]:
		if (e[2] != 'nobs'):
			O[2].append( e )

	# print 'FND: ', Fnd(R, '0', 'a')
	# print Reach(R, Fnd(R, '1', 'b'), 'f', None, True) #= destino, para o evento 'b', vindo do estado B


	# Step 2
	old = None
	last = 0
	while True:
		B = O[1][last]

		# print '\033[38;5;220mB: ', B, '\033[0m'
		for ev in O[2]:
			e = ev[0]
			# print '  e: ', e
			destino = []
			for xe in B:
				x_set = Fnd(R, xe, e)
				# print '    x_set<', xe,'> ', x_set

				for d in Reach(R, x_set, ue, None, True):
					if (d not in destino):
						# print '      append: ', d
						destino.append(d)

			if (destino):
				if not inside(destino, O[1]):
					O[1].append(destino)
				# 	print '      \033[38;5;196mAcresenctando estado: \033[0m', destino
				# else:
				# 	print '      \033[38;5;33mNao acresecntando estado: \033[0m', destino


				# print '      Adding transition with event: ', e, ' e destino: ', destino
				if (not isTransInside ([B, e, destino], O[3])):
					O[3].append([B, e, destino])
				# else:
				# 	print '      \033[38;2;180;0;50mNao acresecntando trans:\033[0m', [B, e, destino]
				# 	# break

		last += 1
		if (last >= len(O[1])):
			break

		# print
		# print

	for i in range(len(O[1])):
		O[1][i] = [ O[1][i], 'nao', 'nao' ]
	return O

# def main ():

# 	R = ['R',
# 		[ ['0', 'marcado', 'inicial'], ['1', 'nao', 'nao'], ['2', 'nao', 'nao'], ['3', 'nao', 'nao'] ],
# 		[ ['a', 'con', 'obs'], ['b', 'con', 'obs'], ['f', 'ncon', 'nobs'] ],
# 		[ ['0', 'a', '1'], ['1', 'b', '0'], ['1', 'b', '1'], ['1', 'f', '2'],
# 		  ['2', 'a', '0'], ['2', 'f', '3'], ['3', 'b', '0'] ]
# 	]


# 	O = Observer(R, 'f')

# 	print '----------------------------'
# 	print 'states: '	
# 	for s in O[1]:
# 		print s

# 	print
# 	print 'transitions: '
# 	for t in O[3]:
# 		print t
# 	print '----------------------------'

# 	print 'S: ', len(O[1])
# 	print 'E: ', len(O[2])
# 	print 'T: ', len(O[3])

# if __name__ == '__main__':
# 	main()
