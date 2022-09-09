import numpy as np
import random
from config import *

golfer_rounds = np.load('golfer_10rounds.npy')

def get_cost(rounds):
    # create a dictionary of sets with keys as integers from 0 to 99 and values as empty sets
    cost_dict = {i: set() for i in range(100)}

    # iterate through the golfer_rounds array
    for k in range(num_iterations):
        for i in range(num_agents):
            group_idx = np.where(rounds[k] == i)[0]
            for element in rounds[k][group_idx][0]:
                cost_dict[i].add(element)
    
    # iterate through the cost_dict dictionary
    met = []
    for i in range(100):
        met.append(len(cost_dict[i]))
    print(np.mean(met))

print("\nAverage number of distinct people met over {} rounds:\n".format(int(num_iterations)))
print("Golfer")
get_cost(golfer_rounds[0])

groups = []
for i in range(num_iterations):
    l = list(range(num_agents))
    random.shuffle(l)
    g = [l[i:i+group_size] for i in range(0, num_agents, group_size)]
    groups.append(g)

print("\nRandom")
get_cost(np.array(groups))