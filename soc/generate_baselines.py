from abcvoting import abcrules, properties
from abcvoting.output import output, INFO, DETAILS, WARNING
from svvamp import GeneratorProfileCubicUniform, Profile
import numpy as np
import csv
from abcvoting.preferences import Profile as abcpf
from tqdm import tqdm
from approval_profile import ApprovalProfile
from objectives import utilitarian_score, representation_score
from main import simulate
from config import *

def generate_baseline_results(utilities, file_name):
    '''
    Generates baseline results for a given set of voting rules, no. of candidates,
    committee size, no. of voters and no. of simulations.
    '''
    output.set_verbosity(WARNING)

    representation_ratio = {}
    raw_representation_score = {}
    utilitarian_ratio = {}
    ejr_scores = {}
    jr_scores = {}
    pjr_scores = {}

    for rule_id in rules:
        representation_ratio[rule_id] = 0
        raw_representation_score[rule_id] = 0
        utilitarian_ratio[rule_id] = 0
        ejr_scores[rule_id] = 0
        jr_scores[rule_id] = 0
        pjr_scores[rule_id] = 0

    for n in tqdm(range(num_simulations)):
        profile = ApprovalProfile(num_agents, num_alternatives, num_winners, num_approval, utilities[n])
        cc_committee = abcrules.compute("cc", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
        optimal_representation = representation_score(cc_committee, profile)
        
        for rule_id in rules:
            result = abcrules.compute(rule_id, profile.profile_abc, committeesize=num_winners, resolute=True)[0]
            #print(rule_id, result)
            rep_score = representation_score(result, profile)
            representation_ratio[rule_id] += rep_score/optimal_representation
            
            utilitarian_ratio[rule_id] += utilitarian_score(list(result), profile)/profile.optimal_welfare
            raw_representation_score[rule_id] += rep_score
            
            ejr_scores[rule_id] += int(properties.check_EJR(profile.profile_abc, result))
            jr_scores[rule_id] += int(properties.check_JR(profile.profile_abc, result))
            pjr_scores[rule_id] += int(properties.check_PJR(profile.profile_abc, result))
    
    # divide by num_simulations to get the average
    for rule_id in representation_ratio:
        representation_ratio[rule_id] = np.round(representation_ratio[rule_id]/num_simulations, 3)
        raw_representation_score[rule_id] = np.round(raw_representation_score[rule_id]/num_simulations, 3)
        utilitarian_ratio[rule_id] = np.round(utilitarian_ratio[rule_id]/num_simulations, 3)
        ejr_scores[rule_id] = np.round(ejr_scores[rule_id]/num_simulations, 3)
        jr_scores[rule_id] = np.round(jr_scores[rule_id]/num_simulations, 3)
        pjr_scores[rule_id] = np.round(pjr_scores[rule_id]/num_simulations, 3)

    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Rule", "Utilitarian Ratio", "Representation Ratio", "Raw Representation Score", "EJR Score", "JR Score", "PJR Score"])
        for rule_id in representation_ratio:
            writer.writerow([rule_id, utilitarian_ratio[rule_id], representation_ratio[rule_id], raw_representation_score[rule_id], ejr_scores[rule_id], jr_scores[rule_id], pjr_scores[rule_id]])

def generate_results():

    init_opinions = []
    final_opinions = []

    for n in range(num_simulations):
        init_utils, final_utils = simulate(group_div)
        init_opinions.append(init_utils)
        final_opinions.append(final_utils)
    
    file_name_init = str.format("nC{}_nW{}_nV{}_nS{}_{}_{}", num_alternatives, num_winners, num_agents, num_simulations, group_div, "init.csv")
    file_name_final = str.format("nC{}_nW{}_nV{}_nS{}_{}_{}", num_alternatives, num_winners, num_agents, num_simulations, group_div, "final.csv")

    print("Generating baseline results for initial opinions...")
    generate_baseline_results(init_opinions, file_name_init)

    print("Generating baseline results for final opinions...")
    generate_baseline_results(final_opinions, file_name_final)

generate_results()