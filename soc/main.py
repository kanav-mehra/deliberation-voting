from agent import Agent
from config import *
from group_div import create_groups
import random
import math
import numpy as np
import time


def get_reception_prob(group_size):
	lamda = 0.5
	p = lamda*math.exp(-lamda*group_size)

	u = 20
	if group_size >= u:
		p = 0
	else:
		p = (u - group_size)/(u-1)
	return p

def simulate(group_div='random'):
	start = time.time()
	#Agent creation
	agents = []
	for i in range(num_agents):
		demo = 1 if i < 0.8*num_agents else 0
		a = Agent(i,demo,ingroup_bias,outgroup_bias,delta)
		agents.append(a)

	#Create groups
	groups = create_groups(agents,'random')
	#print(groups)

	#Deliberation
	for g in groups:
		for i in g:
			prob = get_reception_prob(len(g))
			#print(prob)
			for j in g:
				if j == i:
					continue
				agents[j].update(agents[i].opinions,src_demo=agents[i].demo,prob=prob)


	#Profile Creation
	final_opinions = []
	init_opinions = []

	for i in agents:
		#print(i.opinions)
		#print(i.ops_heard)
		#print(i.ops_listened)
		#print(i.ops_updated)
		if i.debug:
			print(i.init_opinions,i.opinions)
		final_opinions.append(i.opinions)
		init_opinions.append(i.init_opinions)

	final_opinions = np.array(final_opinions)
	init_opinions = np.array(init_opinions)
	
	#print(final_opinions - init_opinions)
	final_var = np.var(final_opinions,axis=0)
	init_var = np.var(init_opinions,axis=0)
	#print(init_var,final_var)
	
	print(final_opinions.shape,init_opinions.shape)

	#Voting

	#Metrics

	simul_time = time.time() - start
	print(simul_time)

simulate()
#print(get_reception_prob(2))