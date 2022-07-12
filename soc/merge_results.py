import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from config import *

gd = ['initial', 'homo_demo', 'random', 'hetero_demo']
metrics = ['Utilitarian Ratio', 'Representation Ratio', 'Voter Satisfaction', 'EJR Score']

for metric in metrics:
    width = 0.75
    plt.figure(figsize=(20,10))
    ax = plt.gca()
    xticks = np.arange(len(rules))
    ax.set_ylabel(metric)
    ax.set_xlabel('Rule')
    ax.set_xticks(xticks, rules)
    if metric!='Voter Satisfaction':
        ax.set_ylim([0.7, 1.0])
    if metric=='EJR Score':
        ax.set_ylim([0, 1])

    for i,file in enumerate(gd):
        if file=='initial':
            file_name = str.format("results/nC{}_nW{}_nV{}_nS{}_{}", num_alternatives, num_winners, num_agents, num_simulations, file+".csv")
        else:
            file_name = str.format("results/nC{}_nW{}_nV{}_nS{}_{}", num_alternatives, num_winners, num_agents, num_simulations, 'final_'+file+".csv")
        df = pd.read_csv(file_name)
        offset = width*(i-2)/4
        ax.bar(xticks+offset, list(df[metric]), width=width/4, label=file)

    ax.legend(loc='upper right')
    ax.set_title(metric+' across group splits')
    plt.savefig(str.format("results/nC{}_nW{}_nV{}_nS{}_{}.png", num_alternatives, num_winners, num_agents, num_simulations, metric))