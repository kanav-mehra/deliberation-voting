from abcvoting import abcrules, properties
from abcvoting.output import output, INFO, DETAILS, WARNING
from svvamp import GeneratorProfileCubicUniform, Profile
import numpy as np
import csv
import random
from abcvoting.preferences import Profile as abcpf
from tqdm import tqdm
from approval_profile import ApprovalProfile
from objectives import utilitarian_score, representation_score, satisfaction_score, project_representation_score
from main import simulate_for_all_group_divs
from significance import test_significance
import matplotlib.pyplot as plt
from config import *

def compute_mean(objectives_):
    '''
    Computes mean of all objectives.
    '''
    # initialize objectives
    objectives_means = {'representation_ratio': {}, 'utilitarian_ratio': {}, 'voter_coverage': {}, 'voter_satisfaction': {}, 
    'minority_representation': {}, 'majority_representation':{}, 'jr_scores': {}, 'pjr_scores': {}, 'ejr_scores': {}}

    for obj in objectives_means:
        for rule_id in rules:
            objectives_means[obj][rule_id] = []
    
    for obj in objectives_:
        for rule_id in rules:
            objectives_means[obj][rule_id] = np.round(np.mean(objectives_[obj][rule_id]), 3)
    return objectives_means

def save_boxplots(objectives_, setup):
    '''
    Saves boxplots for all objectives.
    '''
    for obj in objectives_:
        plt.figure(figsize=(20,10))
        plt.boxplot(objectives_[obj].values())
        plt.xticks(np.arange(1, len(rules)+1), rules)
        plt.ylabel(obj)
        plt.xlabel('Rule')
        plt.savefig(str.format("results/boxplots/{}_{}.png", setup, obj))
        plt.close()

def compute_objectives(approval_sizes, utilities, minority_projects, majority_projects, setup):
    '''
    Computes objectives for a given set of voting rules given the setup, profile utilities, and approvals.
    Opinions and utilities are used interchangebly.
    '''
    output.set_verbosity(WARNING)
    file_name = str.format("results/nC{}_nW{}_nV{}_nS{}_{}", num_alternatives, num_winners, num_agents, num_simulations, setup+".csv")

    # initialize objectives
    objectives = {'representation_ratio': {}, 'utilitarian_ratio': {}, 'voter_coverage': {}, 'voter_satisfaction': {},
    'minority_representation': {}, 'majority_representation': {}, 'jr_scores': {}, 'pjr_scores': {}, 'ejr_scores': {}}

    for obj in objectives:
        for rule_id in rules:
            objectives[obj][rule_id] = []
    
    for n in tqdm(range(num_simulations)):
        profile = ApprovalProfile(num_agents, num_alternatives, num_winners, approval_sizes[n], utilities[n])
        cc_committee = abcrules.compute("cc", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
        av_committee = abcrules.compute("av", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
        optimal_representation = representation_score(cc_committee, profile) # cc_committee has optimal representation
        
        for rule_id in rules:
            result = abcrules.compute(rule_id, profile.profile_abc, committeesize=num_winners, resolute=True)[0]
            
            rep_score = representation_score(result, profile)
            objectives['voter_coverage'][rule_id].append(rep_score)
            objectives['representation_ratio'][rule_id].append(rep_score/optimal_representation)
            
            objectives['utilitarian_ratio'][rule_id].append(utilitarian_score(list(result), profile)/profile.optimal_welfare)
            objectives['voter_satisfaction'][rule_id].append(satisfaction_score(result, profile)/num_agents)

            minority_representation, majority_representation = project_representation_score(result, minority_projects[n], majority_projects[n])
            objectives['minority_representation'][rule_id].append(minority_representation)
            objectives['majority_representation'][rule_id].append(majority_representation)
        
            objectives['jr_scores'][rule_id].append(int(properties.check_JR(profile.profile_abc, result)))
            objectives['pjr_scores'][rule_id].append(int(properties.check_PJR(profile.profile_abc, result)))
            objectives['ejr_scores'][rule_id].append(int(properties.check_EJR(profile.profile_abc, result)))

    save_boxplots(objectives, setup)
    objectives_means = compute_mean(objectives)

    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Rule", "Utilitarian Ratio", "Representation Ratio", "Voter Coverage", "Voter Satisfaction",
         "Minority Representation", "Majority Representation", "EJR Score", "PJR Score", "JR Score"])
        for rule_id in rules:
            writer.writerow([rule_id, objectives_means['utilitarian_ratio'][rule_id], objectives_means['representation_ratio'][rule_id], 
            objectives_means['voter_coverage'][rule_id], objectives_means['voter_satisfaction'][rule_id], 
            objectives_means['minority_representation'][rule_id], objectives_means['majority_representation'][rule_id], 
            objectives_means['ejr_scores'][rule_id], objectives_means['pjr_scores'][rule_id], objectives_means['jr_scores'][rule_id]])
    
    return objectives

def check_profile_eligibility(utilities, approvals):
    profile = ApprovalProfile(num_agents, num_alternatives, num_winners, approvals, utilities)
    cc_committee = abcrules.compute("cc", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
    av_committee = abcrules.compute("av", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
    optimal_representation = representation_score(cc_committee, profile)
    av_representation = representation_score(av_committee, profile)/optimal_representation
    cc_utility = utilitarian_score(list(cc_committee), profile)/profile.optimal_welfare
    if cc_utility>profile_eligibility_threshold or av_representation>profile_eligibility_threshold:
        return False
    else:
        return True

def generate_results():
    objectives_results = {}
    approval_sizes = []
    minority_projects = []
    majority_projects = []
    init_opinions = []
    final_opinions = {}
    for group_div in group_divisions:
        final_opinions[group_div] = []

    print("\nGenerating profiles...")
    for i in tqdm(range(num_simulations)):
        opinions = simulate_for_all_group_divs()
        #approval = random.choices(approval_choices, k=num_agents)
        #approval = np.random.normal(10, 2, num_agents)
        #approval = [int(round(x)) for x in approval]
        approval = opinions['approval']
        approval_sizes.append(approval)
        minority_projects.append(opinions['minority_projects'])
        majority_projects.append(opinions['majority_projects'])
        init_opinions.append(opinions['initial_opinions'])
        for group_div in group_divisions:
            final_opinions[group_div].append(opinions['final_'+group_div])

    print('\nAverage approval ballot size =',np.mean(approval_sizes))
    print("\nGenerating results for initial opinions...")
    objectives_results['initial'] = compute_objectives(approval_sizes, init_opinions, minority_projects, majority_projects, "initial")

    print("\nGenerating results for final opinions...")
    for group_div in group_divisions:
        print("\nSetup:", group_div)
        objectives_results[group_div] = compute_objectives(approval_sizes, final_opinions[group_div], minority_projects, majority_projects, "final_"+group_div)
    
    test_significance(objectives_results)

generate_results()