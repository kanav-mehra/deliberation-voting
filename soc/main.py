from agent import Agent
from config import *
from group_div import create_groups
import random
import math
import numpy as np
import time
from check_profile import check_profile_eligibility

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

def simulate(group_div,seed_0,seed_1,init_opinions,approval):
	start = time.time()
	#Agent creation
	agents = []
	init_utilities = []
	for i in range(num_agents):
		demo = 1 if i < majority*num_agents else 0
		init_ops = None if init_opinions is None else init_opinions[i]
		a = Agent(i,demo,seed_0,seed_1,init_ops)
		init_utilities.append(a.init_opinions)
		agents.append(a)

	log_bc_params = False
	if log_bc_params == True:
		ig_bias = [i.ingroup_bias for i in agents]
		og_bias = [i.outgroup_bias for i in agents]
		bounds = [i.delta for i in agents]

		print(np.mean(ig_bias),np.mean(og_bias),np.mean(bounds))

	#Check_profile_eligibility here
	if not check_profile_eligibility(init_utilities,approval):
		print('Profile check failed...')
		return None, None


	#Create groups
	rounds = create_groups(agents,group_div)
	#print(rounds)

	#Deliberation
	for r in rounds:
		for g in r:
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
	approval = random.choices(approval_choices, k=num_agents)
	ret = {}
	ret['approval'] = approval
	#print(approval)
	for gd in group_divisions:
		init_opinions, final_opinions = simulate(gd,seed_0,seed_1,init_opinions,approval)
		#print(init_opinions)
		if init_opinions is None:
			return simulate_for_all_group_divs()
		ret['initial_opinions'] = init_opinions
		ret['final_'+gd] = final_opinions
		#print(init_opinions,final_opinions)
	#print(ret)
	return ret

#r = simulate_for_all_group_divs()
#print(r)
#print(get_reception_prob(2))