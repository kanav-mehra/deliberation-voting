from abcvoting import abcrules, properties
from abcvoting.output import output, INFO, DETAILS, WARNING
from svvamp import GeneratorProfileCubicUniform, Profile
import numpy as np
import csv
import os, ray
import random
import json
from abcvoting.preferences import Profile as abcpf
from tqdm import tqdm
from approval_profile import ApprovalProfile
from objectives import utilitarian_score, representation_score, satisfaction_score, perc_satisfaction,\
    project_representation_score, approval_scores, nash_welfare_score
from main import simulate_for_all_group_divs
import matplotlib.pyplot as plt
from config import *
from deliberation_metrics import plot_deliberation_results, plot_compare_iterative

# create a directory results if it doesn't exist
if not os.path.exists(RESULT_PATH):
    os.mkdir(RESULT_PATH)
    os.mkdir(RESULT_PATH+'/boxplots')
    os.mkdir(RESULT_PATH+'/significance')
    os.mkdir(RESULT_PATH+'/tables')
    os.mkdir(RESULT_PATH+'/charts')
    os.mkdir(RESULT_PATH+'/deliberation')
    os.mkdir(RESULT_PATH+'/violations')

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def compute_mean(objectives_):
    '''
    Computes mean of all objectives.
    '''
    # initialize objectives
    objectives_means = {'representation_ratio': {}, 'utilitarian_ratio': {}, 'utility_rep_agg': {}, 'nash_welfare_score':{}, 
    'voter_coverage': {}, 'voter_satisfaction': {}, 'minority_representation': {}, 'majority_representation':{}, 'jr_scores': {}, 
    'pjr_scores': {}, 'ejr_scores': {}, 'violationsx': {}, 'violationsy': {}, 'cohesive_groups': {}, 'violation_percent': {}}

    for obj in objectives_means:
        for rule_id in rules:
            objectives_means[obj][rule_id] = []
    
    for obj in objectives_:
        for rule_id in rules:
            if objectives_[obj][rule_id]:
                objectives_means[obj][rule_id] = np.round(np.mean(objectives_[obj][rule_id]), 3)
            else:
                objectives_means[obj][rule_id] = 0
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
        plt.savefig(str.format("{}/boxplots/{}_{}.png", RESULT_PATH, setup, obj))
        plt.close()

def plot_violations(violationsx, violationsy, cohesive_groups, violation_percent, setup):
    '''
    Plots violations for all rules.
    '''
    for rule in violationsx:
        plt.figure(figsize=(20,10))
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.scatter(violationsx[rule], violationsy[rule])
        plt.xlabel('Proportion of Voter Group')
        plt.ylabel('Violation Extent')
        vcount = len(violationsx[rule])
        gcount = sum(cohesive_groups[rule])
        percent = sum(violation_percent[rule])/num_simulations
        plt.title(str.format("{}_{}_{}_{}_{}_{}", rule, setup, vcount, gcount, vcount/gcount, percent))
        plt.savefig(str.format("{}/violations/{}_{}.png", RESULT_PATH, setup, rule))
        plt.close()

def save_cc_approvals(cc_approvals):
    plt.rcParams.update({'font.size': 48})
    gd = ['initial'] + group_divisions
    gd_names = ['initial', 'random', 'homogeneous', 'heterogeneous', 'iterative golfer', 'iterative random', 'large group']
    width = 0.75
    plt.figure(figsize=(50,30))
    ax = plt.gca()
    xticks = np.arange(len(gd))
    ax.set_ylabel('Approval Scores')
    ax.set_xlabel('Deliberation Mechanism')
    ax.set_xticks(xticks, gd_names)
    candidate_approvals = [cc_approvals[x] for x in gd]

    for i in range(num_winners):
        offset = width*(i-2)/num_winners
        plot_list = [x[i] for x in candidate_approvals]
        ax.bar(xticks+offset, plot_list, width=width/num_winners, label='Candidate {}'.format(i+1))
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.01), ncol=5, prop={'size': 48})
    ax.set_title('Approval Scores for candidates in CC committees')
    plt.tight_layout(pad=1.0)
    plt.savefig(str.format("{}/charts/nC{}_nW{}_nV{}_nS{}_{}.png", RESULT_PATH, num_alternatives, num_winners, num_agents, num_simulations, "cc_approvals"))

@ray.remote
def compute_objectives(approval_sizes, utilities, minority_projects, majority_projects, setup):
    '''
    Computes objectives for a given set of voting rules given the setup, profile utilities, and approvals.
    Opinions and utilities are used interchangebly.
    '''
    output.set_verbosity(WARNING)

    file_name = str.format("{}/tables/nC{}_nW{}_nV{}_nS{}_{}.csv", RESULT_PATH, num_alternatives, num_winners, num_agents, num_simulations, setup)

    # initialize objectives
    objectives = {'representation_ratio': {}, 'utilitarian_ratio': {}, 'utility_rep_agg': {}, 'nash_welfare_score': {}, 
    'voter_coverage': {}, 'voter_satisfaction': {}, 'minority_representation': {}, 'majority_representation': {}, 'jr_scores': {},
    'pjr_scores': {}, 'ejr_scores': {}, 'violationsx': {}, 'violationsy': {}, 'cohesive_groups': {}, 'violation_percent': {}}

    for obj in objectives:
        for rule_id in rules:
            objectives[obj][rule_id] = []
    
    cc_approvals = []

    for n in range(num_simulations):
        profile = ApprovalProfile(num_agents, num_alternatives, num_winners, approval_sizes[n], utilities[n])
        cc_committee = abcrules.compute("cc", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
        av_committee = abcrules.compute("av", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
        optimal_representation = representation_score(cc_committee, profile) # cc_committee has optimal representation
        cc_approvals.append(approval_scores(cc_committee, profile))
        committee_results = []

        for rule_id in rules:
            result = abcrules.compute(rule_id, profile.profile_abc, committeesize=num_winners, resolute=True)[0]
            committee_results.append((rule_id, list(result)))
            rep_score = representation_score(result, profile)
            rep_ratio = rep_score/optimal_representation
            util_ratio = utilitarian_score(list(result), profile)/profile.optimal_welfare

            objectives['voter_coverage'][rule_id].append(rep_score)
            objectives['representation_ratio'][rule_id].append(rep_ratio)
            objectives['utilitarian_ratio'][rule_id].append(util_ratio)

            objectives['utility_rep_agg'][rule_id].append(rep_ratio*util_ratio)
            objectives['voter_satisfaction'][rule_id].append(satisfaction_score(result, profile)/num_agents)
            objectives['nash_welfare_score'][rule_id].append(nash_welfare_score(list(result), profile))

            minority_representation, majority_representation = project_representation_score(result, minority_projects[n], majority_projects[n])
            objectives['minority_representation'][rule_id].append(minority_representation)
            objectives['majority_representation'][rule_id].append(majority_representation)
        
            objectives['jr_scores'][rule_id].append(int(properties.check_JR(profile.profile_abc, result)))
            objectives['pjr_scores'][rule_id].append(int(properties.check_PJR(profile.profile_abc, result)))
            objectives['ejr_scores'][rule_id].append(int(properties.check_EJR(profile.profile_abc, result)))
        
        satisfaction_results = ray.get([perc_satisfaction.remote(profile.profile_abc, cm[0], cm[1]) for cm in committee_results])
        for sr in satisfaction_results:
            rule_id = sr[0]
            objectives['violationsx'][rule_id] += sr[1]
            objectives['violationsy'][rule_id] += sr[2]
            objectives['cohesive_groups'][rule_id].append(sr[3])
            objectives['violation_percent'][rule_id].append(len(sr[1])/sr[3])
        
    save_boxplots(objectives, setup)
    plot_violations(objectives['violationsx'], objectives['violationsy'], objectives['cohesive_groups'], objectives['violation_percent'], setup)
    objectives_means = compute_mean(objectives)
    cc_approvals_mean = np.round(np.mean(cc_approvals, axis=0), 3)
    
    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Rule", "Utilitarian Ratio", "Representation Ratio", "Utility Representation Aggregate", "Nash Welfare", "Voter Coverage", "Voter Satisfaction",
         "Minority Representation", "Majority Representation", "EJR Score", "PJR Score", "JR Score", "ViolationsX", "ViolationsY", "Cohesive Groups", "Violation Percent"])
        for rule_id in rules:
            writer.writerow([rule_id, objectives_means['utilitarian_ratio'][rule_id], objectives_means['representation_ratio'][rule_id], objectives_means['utility_rep_agg'][rule_id],
            objectives_means['nash_welfare_score'][rule_id], objectives_means['voter_coverage'][rule_id], objectives_means['voter_satisfaction'][rule_id], 
            objectives_means['minority_representation'][rule_id], objectives_means['majority_representation'][rule_id], 
            objectives_means['ejr_scores'][rule_id], objectives_means['pjr_scores'][rule_id], objectives_means['jr_scores'][rule_id],
            objectives_means['violationsx'][rule_id], objectives_means['violationsy'][rule_id], objectives_means['cohesive_groups'][rule_id], objectives_means['violation_percent'][rule_id]])
    
    return objectives, cc_approvals_mean

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
    cc_approvals_results = {}
    approval_sizes = []
    minority_projects = []
    majority_projects = []
    init_opinions = []
    final_opinions = {}
    for group_div in group_divisions:
        final_opinions[group_div] = []

    variance = []
    intergroup_dist = []
    min_drift = []
    maj_drift = []
    del_mvmt_golfer = []
    del_mvmt_random = []

    print("\nGenerating profiles...")
    for i in tqdm(range(num_simulations)):
        opinions = simulate_for_all_group_divs()
        variance.append(opinions['variance'])
        intergroup_dist.append(opinions['intergroup_dist'])
        maj_drift.append(opinions['maj_drift'])
        min_drift.append(opinions['min_drift'])
        del_mvmt_golfer.append(opinions['del_movement_iterative_golfer'])
        del_mvmt_random.append(opinions['del_movement_iterative_random'])

        approval = opinions['approval']
        approval_sizes.append(approval)
        minority_projects.append(opinions['minority_projects'])
        majority_projects.append(opinions['majority_projects'])
        init_opinions.append(opinions['initial_opinions'])
        for group_div in group_divisions:
            final_opinions[group_div].append(opinions['final_'+group_div])

    print('\nAverage approval ballot size =',np.mean(approval_sizes))

    ray.init()
    refs = [compute_objectives.remote(approval_sizes, init_opinions, minority_projects, majority_projects, "initial")]
    for group_div in group_divisions:
        refs.append(compute_objectives.remote(approval_sizes, final_opinions[group_div], minority_projects, majority_projects, "final_"+group_div))
    
    ray_results = ray.get(refs)
    
    objectives_results['initial'], cc_approvals_results['initial'] = ray_results[0]
    for group_div in group_divisions:
        objectives_results[group_div], cc_approvals_results[group_div] = ray_results[group_divisions.index(group_div)+1]
    
    # Dump objectives results into a json file
    with open(str.format('{}/objectives_results.json', RESULT_PATH), 'w') as fp:
        json.dump(objectives_results, fp, cls=NumpyEncoder)

    #test_significance(objectives_results)
    save_cc_approvals(cc_approvals_results)   
    
    xticks = ['initial'] + group_divisions
    var,var_err = np.mean(variance,axis=0),np.std(variance,axis=0)
    plot_deliberation_results(var,var_err,"Variance",xticks)
    igd,igd_err = np.mean(intergroup_dist,axis=0),np.std(intergroup_dist,axis=0)
    plot_deliberation_results(igd,igd_err,"Intergroup Ballot Disagreement",xticks)
    xticks.pop(0)
    mjd,mjd_err = np.mean(maj_drift,axis=0),np.std(maj_drift,axis=0)
    plot_deliberation_results(mjd,mjd_err,"Majority Ballot Drift",xticks)
    mnd,mnd_err = np.mean(min_drift,axis=0),np.std(min_drift,axis=0)
    plot_deliberation_results(mnd,mnd_err,"Minority Ballot Drift",xticks)
    dmg,dmg_err = np.mean(del_mvmt_golfer,axis=0),np.std(del_mvmt_golfer,axis=0)
    dmr,dmr_err = np.mean(del_mvmt_random,axis=0),np.std(del_mvmt_random,axis=0)
    plot_compare_iterative(dmg,dmr,dmg_err,dmr_err)  

generate_results()