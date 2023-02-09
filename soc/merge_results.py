import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from config import *

plt.rcParams.update({'font.size': 72})

gd = ['initial', 'homo_demo', 'random', 'hetero_demo', 'iterative_random', 'iterative_golfer', 'large_group']
gd_names = ['initial', 'homogeneous', 'random', 'heterogeneous', 'iterative random', 'iterative golfer', 'large group']
metrics = ['Utilitarian Ratio', 'Representation Ratio', 'Utility Representation Aggregate', 'Voter Satisfaction', 'EJR Score', 'PJR Score', 'ViolationsX', 'ViolationsY']
colors = ['blue', 'orange', 'green', 'red', 'hotpink', 'purple', 'brown']

for metric in metrics:
    width = 0.75
    plt.figure(figsize=(50,30))
    ax = plt.gca()
    xticks = np.arange(len(rules))
    ax.set_ylabel(metric)
    ax.set_xlabel('Voting Rule')
    ax.set_xticks(xticks, ['AV', 'MES', 'PAV', 'CC'])
    
    if metric not in ['Voter Satisfaction', 'Minority Representation', 'Majority Representation', 'Nash Welfare']:
        ax.set_ylim([0.6, 1.0])
    if metric in ['EJR Score', 'PJR Score', 'ViolationsX', 'ViolationsY']:
        ax.set_ylim([0, 1])
    

    for i,file in enumerate(gd):
        if file=='initial':
            file_name = str.format("{}/tables/nC{}_nW{}_nV{}_nS{}_{}.csv", RESULT_PATH, num_alternatives, num_winners, num_agents, num_simulations, file)
        else:
            file_name = str.format("{}/tables/nC{}_nW{}_nV{}_nS{}_{}.csv", RESULT_PATH ,num_alternatives, num_winners, num_agents, num_simulations, 'final_'+file)
        df = pd.read_csv(file_name)
        offset = width*(i-2)/len(gd)
        if i>3:
            ax.bar(xticks+offset, list(df[metric]), width=width/len(gd), label=gd_names[i], color=colors[i], edgecolor='black')
        else:
            ax.bar(xticks+offset, list(df[metric]), width=width/len(gd), label=gd_names[i], edgecolor='black')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=4, prop={'size': 48})
    plt.tight_layout(pad=1.0)
    plt.savefig(str.format("{}/charts/nC{}_nW{}_nV{}_nS{}_{}.png", RESULT_PATH, num_alternatives, num_winners, num_agents, num_simulations, metric))