from agent import Agent
from config import *
from group_div import create_groups
import random
import math
import numpy as np
import time

def get_reception_prob(group_size):
	return 1

	#exponential
	lamda = 0.5
	p = lamda*math.exp(-lamda*group_size)

	#linear decay
	u = 20
	if group_size >= u:
		p = 0
	else:
		p = (u - group_size)/(u-1)
	return p

def simulate(group_div,seed_0,seed_1,init_opinions):
	start = time.time()
	#Agent creation
	agents = []
	for i in range(num_agents):
		demo = 1 if i < majority*num_agents else 0
		init_ops = None if init_opinions is None else init_opinions[i]
		a = Agent(i,demo,seed_0,seed_1,init_ops)
		agents.append(a)

	#Create groups
	groups = create_groups(agents,group_div)
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
		final_opinions.append(i.opinions)
		init_opinions.append(i.init_opinions)

	final_opinions = np.array(final_opinions)
	init_opinions = np.array(init_opinions)
	
	simul_time = time.time() - start
	#print(simul_time)
	return init_opinions, final_opinions



def simulate_for_all_group_divs():
	seed_0 = list(range(num_alternatives))
	random.shuffle(seed_0)

	seed_1 = list(range(num_alternatives))
	random.shuffle(seed_1)

	init_opinions = None
	ret = {}
	for gd in group_divisions:
		init_opinions, final_opinions = simulate(gd,seed_0,seed_1,init_opinions)
		print(init_opinions)
		ret['initial_opinions'] = init_opinions
		ret['final_'+gd] = final_opinions
	print(ret)
	return ret

simulate_for_all_group_divs()
#print(get_reception_prob(2))