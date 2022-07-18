from config import *
from golfer import social_golfer
import random


def create_groups(agents, group_div='random'):
	if group_div == 'homo_demo':
		majority = [i.id for i in agents if i.demo == 1]
		minority = [i.id for i in agents if i.demo == 0]

		random.shuffle(majority)
		groups_1 = [majority[i:i+group_size] for i in range(0, len(majority), group_size)]

		random.shuffle(minority)
		groups_0 = [minority[i:i+group_size] for i in range(0, len(minority), group_size)]

		groups = groups_1 + groups_0
		groups = [groups]
	elif group_div == 'hetero_demo':
		majority = [i.id for i in agents if i.demo == 1]
		minority = [i.id for i in agents if i.demo == 0]

		random.shuffle(majority)
		random.shuffle(minority)

		min_proportion = int(len(minority)/num_agents * group_size)
		maj_proportion = group_size - min_proportion
		groups = [majority[i:i+maj_proportion] for i in range(0, len(majority), maj_proportion)]
		for i in groups:
			for j in range(min_proportion):
				x = minority.pop(0)
				i.append(x)
		groups = [groups]
	elif group_div == 'iterative_golfer':
		num_groups = num_agents//group_size
		groups, _ = social_golfer(num_groups,group_size,num_iterations)
		#print(groups)
		assert len(groups) == num_iterations
		assert len(groups[0]) == num_groups
	elif group_div == 'iterative_random':
		groups = []
		for i in range(num_iterations):
			l = list(range(num_agents))
			random.shuffle(l)
			g = [l[i:i+group_size] for i in range(0, num_agents, group_size)]
			groups.append(g)
		assert len(groups) == num_iterations
		assert len(groups[0]) == num_agents//group_size
	elif group_div == 'large_group':
		l = list(range(num_agents))
		random.shuffle(l)
		groups = [[l]]
		assert len(groups) == 1 and len(groups[0]) == 1
	else:
		l = list(range(num_agents))
		random.shuffle(l)
		groups = [l[i:i+group_size] for i in range(0, num_agents, group_size)]
		groups = [groups]
	#print(groups)
	return groups