from agent import Agent
from config import *
from group_div import create_groups
import random
import math
import numpy as np
import time
from check_profile import check_profile_eligibility

'''
def gen_rankings_from_utils_np(utils):
	utils=np.array(utils)
	print(utils.shape)
	ranking = np.flip(np.argpartition(utils,utils.shape[1]-1),1)
	return ranking
'''

def gen_rankings_from_utils(utils):
	utils=list(utils)
	rankings = []
	u = utils.copy()
	utils.sort(reverse=True)
	for i in utils:
		rankings.append(u.index(i))
	return rankings

def classify_alternatives(init_opinions, approval):
	majority_ctr = [0 for i in range(num_alternatives)]
	minority_ctr = [0 for i in range(num_alternatives)]

	for i in range(num_agents):
		ranking = gen_rankings_from_utils(init_opinions[i])
		if i < majority*num_agents:
			for alts in ranking[:approval[i]]:
				majority_ctr[alts] += 1
		else:
			for alts in ranking[:approval[i]]:
				minority_ctr[alts] += 1
	majority_projects = []
	minority_projects = []
	for i in range(num_alternatives):
		if majority_ctr[i]/majority >= minority_ctr[i]/(1-majority):
			majority_projects.append(i)
		else:
			minority_projects.append(i)
	
	'''
	print(majority_ctr)
	print(minority_ctr)
	for i in zip(range(num_alternatives),majority_ctr,minority_ctr):
		print(i)
	print(majority_projects)
	print(minority_projects)
	'''

	return majority_projects,minority_projects

def get_reception_prob(group_size):
	#linear decay between lower (l) and upper (u); constant otherwise
	u = 200
	l = 10
	if group_size >= u:
		p = 0
	elif group_size > l:
		p = (u - group_size)/(u - l)
	else:
		p = 1
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

	log_bc_params = True
	if log_bc_params == True:
		ig_bias = [i.ingroup_bias for i in agents]
		og_bias = [i.outgroup_bias for i in agents]
		bounds = [i.delta for i in agents]

		for i in range(num_agents):
			print(ig_bias[i],og_bias[i],bounds[i])
		print(np.mean(ig_bias),np.mean(og_bias),np.mean(bounds))
		print('\n ==================== \n')

	#Check_profile_eligibility here
	if not check_profile_eligibility(init_utilities,approval):
		#print('Profile check failed...')
		return None, None


	#Create groups
	rounds = create_groups(agents,group_div)
	#print(rounds)

	#Deliberation
	for r in rounds:
		for g in r:
			for i in g:
				prob = 1 if group_div == 'large_group' else get_reception_prob(len(g))
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
	#approval = random.choices(approval_choices, k=num_agents)
	approval = np.random.normal(approval_mean, approval_std, num_agents)
	approval = [int(round(x)) for x in approval]
	ret = {}
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
	#print(seed_1,seed_0)
	ret['majority_projects'],ret['minority_projects'] = classify_alternatives(init_opinions,approval)
	ret['approval'] = approval
	return ret

#r = simulate_for_all_group_divs()
#print(r)
#print(get_reception_prob(2))