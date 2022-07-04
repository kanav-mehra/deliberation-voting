from config import *
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
	else:
		l = list(range(num_agents))
		random.shuffle(l)
		groups = [l[i:i+group_size] for i in range(0, num_agents, group_size)]

	return groups