import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import *

gd = ['initial', 'homo_demo', 'random', 'hetero_demo', 'large_group_wrp', 'iterative_random', 'iterative_golfer', 'large_group']
metrics = ['Utilitarian Ratio', 'Representation Ratio', 'Voter Satisfaction', 'Minority Representation', 'Majority Representation', 'EJR Score']

for metric in metrics:
    width = 0.75
    plt.figure(figsize=(20,10))
    ax = plt.gca()
    xticks = np.arange(len(rules))
    ax.set_ylabel(metric)
    ax.set_xlabel('Rule')
    ax.set_xticks(xticks, rules)
    
    if metric not in ['Voter Satisfaction', 'Minority Representation', 'Majority Representation']:
        ax.set_ylim([0.6, 1.0])
    if metric=='EJR Score':
        ax.set_ylim([0, 1])

    for i,file in enumerate(gd):
        if file=='initial':
            file_name = str.format("{}/tables/nC{}_nW{}_nV{}_nS{}_{}.csv", RESULT_PATH, num_alternatives, num_winners, num_agents, num_simulations, file)
        else:
            file_name = str.format("{}/tables/nC{}_nW{}_nV{}_nS{}_{}.csv", RESULT_PATH ,num_alternatives, num_winners, num_agents, num_simulations, 'final_'+file)
        df = pd.read_csv(file_name)
        offset = width*(i-2)/len(gd)
        ax.bar(xticks+offset, list(df[metric]), width=width/len(gd), label=file)

    ax.legend(loc='upper right')
    ax.set_title(metric)
    plt.savefig(str.format("{}/charts/nC{}_nW{}_nV{}_nS{}_{}.png", RESULT_PATH, num_alternatives, num_winners, num_agents, num_simulations, metric))