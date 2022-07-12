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

def generate_baseline_results(utilities, setup):
    '''
    Generates baseline results for a given set of voting rules, no. of candidates,
    committee size, no. of voters and no. of simulations.
    '''
    output.set_verbosity(WARNING)

    file_name = str.format("results/nC{}_nW{}_nV{}_nS{}_{}", num_alternatives, num_winners, num_agents, num_simulations, setup+".csv")

    representation_ratio = {}
    voter_coverage = {}
    voter_satisfaction = {}
    utilitarian_ratio = {}
    ejr_scores = {}
    jr_scores = {}
    pjr_scores = {}

    for rule_id in rules:
        representation_ratio[rule_id] = 0
        voter_coverage[rule_id] = 0
        voter_satisfaction[rule_id] = 0
        utilitarian_ratio[rule_id] = 0
        ejr_scores[rule_id] = 0
        jr_scores[rule_id] = 0
        pjr_scores[rule_id] = 0
    
    for n in tqdm(range(num_simulations)):
        profile = ApprovalProfile(num_agents, num_alternatives, num_winners, num_approval, utilities[n])
        cc_committee = abcrules.compute("cc", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
        av_committee = abcrules.compute("av", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
        optimal_representation = representation_score(cc_committee, profile)
        
        for rule_id in rules:
            result = abcrules.compute(rule_id, profile.profile_abc, committeesize=num_winners, resolute=True)[0]
            #print(rule_id, result)
            rep_score = representation_score(result, profile)
            representation_ratio[rule_id] += rep_score/optimal_representation
            
            utilitarian_ratio[rule_id] += utilitarian_score(list(result), profile)/profile.optimal_welfare
            voter_coverage[rule_id] += rep_score
            voter_satisfaction[rule_id] += satisfaction_score(result, profile)/num_agents
            
            ejr_scores[rule_id] += int(properties.check_EJR(profile.profile_abc, result))
            jr_scores[rule_id] += int(properties.check_JR(profile.profile_abc, result))
            pjr_scores[rule_id] += int(properties.check_PJR(profile.profile_abc, result))
    
    # divide by num_simulations to get the average
    for rule_id in representation_ratio:
        representation_ratio[rule_id] = np.round(representation_ratio[rule_id]/num_simulations, 3)
        voter_coverage[rule_id] = np.round(voter_coverage[rule_id]/num_simulations, 3)
        voter_satisfaction[rule_id] = np.round(voter_satisfaction[rule_id]/num_simulations, 3)
        utilitarian_ratio[rule_id] = np.round(utilitarian_ratio[rule_id]/num_simulations, 3)
        ejr_scores[rule_id] = np.round(ejr_scores[rule_id]/num_simulations, 3)
        jr_scores[rule_id] = np.round(jr_scores[rule_id]/num_simulations, 3)
        pjr_scores[rule_id] = np.round(pjr_scores[rule_id]/num_simulations, 3)

    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Rule", "Utilitarian Ratio", "Representation Ratio", "Voter Coverage", "Voter Satisfaction", "EJR Score", "PJR Score", "JR Score"])
        for rule_id in representation_ratio:
            writer.writerow([rule_id, utilitarian_ratio[rule_id], representation_ratio[rule_id], voter_coverage[rule_id], voter_satisfaction[rule_id], ejr_scores[rule_id], pjr_scores[rule_id], jr_scores[rule_id]])

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
            #print(simulation_count)
        else:
            continue
    
    print("Generating baseline results for initial opinions...")
    generate_baseline_results(init_opinions, "initial")

    print("Generating baseline results for final opinions...")
    for group_div in group_divisions:
        print("Setup:", group_div)
        generate_baseline_results(final_opinions[group_div], "final_"+group_div)

generate_results()