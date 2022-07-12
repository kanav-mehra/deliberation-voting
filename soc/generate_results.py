from abcvoting import abcrules, properties
from abcvoting.output import output, INFO, DETAILS, WARNING
from svvamp import GeneratorProfileCubicUniform, Profile
import numpy as np
import csv
from abcvoting.preferences import Profile as abcpf
from tqdm import tqdm
from approval_profile import ApprovalProfile
from objectives import utilitarian_score, representation_score, satisfaction_score
from main import simulate_for_all_group_divs
from config import *

def compute_mean(objectives):
    '''
    Computes mean of all objectives.
    '''
    print(objectives)
    for obj in objectives:
        for rule_id in rules:
            objectives[obj][rule_id] = np.round(np.mean(objectives[obj][rule_id]), 3)
    return objectives

def compute_objectives(utilities, setup):
    '''
    Computes objectives for a given set of voting rules given the setup and profile utilities.
    Opinions and utilities are used interchangebly.
    '''
    output.set_verbosity(WARNING)
    file_name = str.format("results/nC{}_nW{}_nV{}_nS{}_{}", num_alternatives, num_winners, num_agents, num_simulations, setup+".csv")

    # initialize objectives
    objectives = {'representation_ratio': {}, 'utilitarian_ratio': {}, 'voter_coverage': {}, 'voter_satisfaction': {}, 'jr_scores': {}, 'pjr_scores': {}, 'ejr_scores': {}}
    for obj in objectives:
        for rule_id in rules:
            objectives[obj][rule_id] = []
    
    for n in tqdm(range(num_simulations)):
        profile = ApprovalProfile(num_agents, num_alternatives, num_winners, num_approval, utilities[n])
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
            
            objectives['jr_scores'][rule_id].append(int(properties.check_JR(profile.profile_abc, result)))
            objectives['pjr_scores'][rule_id].append(int(properties.check_PJR(profile.profile_abc, result)))
            objectives['ejr_scores'][rule_id].append(int(properties.check_EJR(profile.profile_abc, result)))
    
    objectives_means = compute_mean(objectives)

    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Rule", "Utilitarian Ratio", "Representation Ratio", "Voter Coverage", "Voter Satisfaction", "EJR Score", "PJR Score", "JR Score"])
        for rule_id in rules:
            writer.writerow([rule_id, objectives_means['utilitarian_ratio'][rule_id], objectives_means['representation_ratio'][rule_id], 
            objectives_means['voter_coverage'][rule_id], objectives_means['voter_satisfaction'][rule_id], objectives_means['ejr_scores'][rule_id], 
            objectives_means['pjr_scores'][rule_id], objectives_means['jr_scores'][rule_id]])

def check_profile_eligibility(utilities):
    profile = ApprovalProfile(num_agents, num_alternatives, num_winners, num_approval, utilities)
    cc_committee = abcrules.compute("cc", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
    av_committee = abcrules.compute("av", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
    optimal_representation = representation_score(cc_committee, profile)
    av_representation = representation_score(av_committee, profile)/optimal_representation
    cc_utility = utilitarian_score(list(cc_committee), profile)/profile.optimal_welfare
    if cc_utility>0.9 or av_representation>0.9:
        return False
    else:
        return True

def generate_results():

    init_opinions = []
    final_opinions = {}
    for group_div in group_divisions:
        final_opinions[group_div] = []
    simulation_count = 0

    while simulation_count<num_simulations:
        opinions = simulate_for_all_group_divs()
        if check_profile_eligibility(opinions['initial_opinions'])==True:
            init_opinions.append(opinions['initial_opinions'])
            for group_div in group_divisions:
                final_opinions[group_div].append(opinions['final_'+group_div])
            simulation_count+=1
        else:
            continue
    
    print("Generating baseline results for initial opinions...")
    compute_objectives(init_opinions, "initial")

    print("Generating baseline results for final opinions...")
    for group_div in group_divisions:
        print("Setup:", group_div)
        compute_objectives(final_opinions[group_div], "final_"+group_div)

generate_results()