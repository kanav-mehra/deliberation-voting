from abcvoting import abcrules, properties
from abcvoting.output import output, INFO, DETAILS, WARNING
from svvamp import GeneratorProfileCubicUniform, Profile
import numpy as np
import csv
import os
import random
from abcvoting.preferences import Profile as abcpf
from tqdm import tqdm
from approval_profile import ApprovalProfile
from objectives import utilitarian_score, representation_score, satisfaction_score, project_representation_score, approval_scores, nash_welfare_score
from main import simulate_for_all_group_divs
import matplotlib.pyplot as plt
from config import *
from deliberation_metrics import plot_deliberation_results, plot_compare_iterative
import multiprocessing as mp
import json
import time

# create a directory results if it doesn't exist
if not os.path.exists(RESULT_PATH):
    os.mkdir(RESULT_PATH)
    os.mkdir(RESULT_PATH+'/boxplots')
    os.mkdir(RESULT_PATH+'/significance')
    os.mkdir(RESULT_PATH+'/tables')
    os.mkdir(RESULT_PATH+'/charts')
    os.mkdir(RESULT_PATH+'/deliberation')

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
    objectives_means = {'representation_ratio': {}, 'utilitarian_ratio': {}, 'utility_rep_agg': {}, 'nash_welfare_score':{}, 'voter_coverage': {}, 'voter_satisfaction': {}, 
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
        plt.savefig(str.format("{}/boxplots/{}_{}.png", RESULT_PATH, setup, obj))
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

def compute_objectives(approval_sizes, utilities, minority_projects, majority_projects, setup, output_queue):
    '''
    Computes objectives for a given set of voting rules given the setup, profile utilities, and approvals.
    Opinions and utilities are used interchangebly.
    '''
    output.set_verbosity(WARNING)

    

    file_name = str.format("{}/tables/nC{}_nW{}_nV{}_nS{}_{}.csv", RESULT_PATH, num_alternatives, num_winners, num_agents, num_simulations, setup)

    # initialize objectives
    objectives = {'representation_ratio': {}, 'utilitarian_ratio': {}, 'utility_rep_agg': {}, 'nash_welfare_score':{}, 'voter_coverage': {}, 'voter_satisfaction': {},
    'minority_representation': {}, 'majority_representation': {}, 'jr_scores': {}, 'pjr_scores': {}, 'ejr_scores': {}}

    for obj in objectives:
        for rule_id in rules:
            objectives[obj][rule_id] = []
    
    cc_approvals = []

    log_interval = 20
    for n in range(num_simulations):
        if n > 0 and n%log_interval == 0 and setup == 'initial':
            print('Progress: {}/{}'.format(n,num_simulations))
        profile = ApprovalProfile(num_agents, num_alternatives, num_winners, approval_sizes[n], utilities[n])
        cc_committee = abcrules.compute("cc", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
        av_committee = abcrules.compute("av", profile.profile_abc, committeesize=num_winners, resolute=True)[0]
        optimal_representation = representation_score(cc_committee, profile) # cc_committee has optimal representation
        cc_approvals.append(approval_scores(cc_committee, profile))

        for rule_id in rules:
            result = abcrules.compute(rule_id, profile.profile_abc, committeesize=num_winners, resolute=True)[0]
            
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
    
    save_boxplots(objectives, setup)
    objectives_means = compute_mean(objectives)
    cc_approvals_mean = np.round(np.mean(cc_approvals, axis=0), 3)
    
    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Rule", "Utilitarian Ratio", "Representation Ratio", "Utility Representation Aggregate", "Nash Welfare", "Voter Coverage", "Voter Satisfaction",
         "Minority Representation", "Majority Representation", "EJR Score", "PJR Score", "JR Score"])
        for rule_id in rules:
            writer.writerow([rule_id, objectives_means['utilitarian_ratio'][rule_id], objectives_means['representation_ratio'][rule_id], objectives_means['utility_rep_agg'][rule_id],
            objectives_means['nash_welfare_score'][rule_id], objectives_means['voter_coverage'][rule_id], objectives_means['voter_satisfaction'][rule_id], 
            objectives_means['minority_representation'][rule_id], objectives_means['majority_representation'][rule_id], 
            objectives_means['ejr_scores'][rule_id], objectives_means['pjr_scores'][rule_id], objectives_means['jr_scores'][rule_id]])
    
    #return objectives, cc_approvals_mean
    if 'final_' in setup:
        setup = setup[6:]
    d = {}
    d['objectives'] = objectives
    d['cc'] = cc_approvals_mean
    #d['objectives'] = np.arange(100,100)
    #d['cc'] = np.arange(100)
    with open('tmp_res/{}.json'.format(setup),'w') as f:
        json.dump(d,f,cls=NumpyEncoder)
    output_queue.put(setup)

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

def simulate_wrapper(n,output_queue):
    n = str(n)
    r = simulate_for_all_group_divs()
    with open('tmp_res/{}.json'.format(n),'w') as f:
        json.dump(r,f,cls=NumpyEncoder)
    output_queue.put(n)

def generate_results():
    start = time.time()
    if not os.path.exists('tmp_res'):
        os.mkdir('tmp_res')
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

    #with Pool(processes = cpu_count, )
    simulate_queue = mp.Queue()
    cpu_count = mp.cpu_count()
    batch_size = int(1.5*cpu_count)
    print('CPU count: {}, Batch Size: {}'.format(cpu_count,batch_size))

    results = []
    x = 0
    while x < num_simulations:
        processes = [mp.Process(target=simulate_wrapper,args=(x+i,simulate_queue)) for i in range(min(num_simulations-x,batch_size))]
        for p in processes:
            p.start()
        #print('Started',len(processes))
        for p in processes:
            p.join()
        
        results += [simulate_queue.get() for p in processes]
        x += batch_size
        x = min(num_simulations,x)
        print('Progress: {}/{}'.format(x,num_simulations))
    assert len(results) == num_simulations

    for i in results:
        fname = 'tmp_res/{}.json'.format(i)
        with open(fname, 'r') as f:
            opinions = json.load(f)
        os.remove(fname)
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
    assert len(os.listdir('tmp_res')) == 0
    part1 = time.time()
    print('Done with deliberation phase in ', part1-start)
    op_queue = mp.Queue()

    processes = []
    init_p = mp.Process(target=compute_objectives,args=(approval_sizes, init_opinions, minority_projects, majority_projects, "initial", op_queue))
    processes.append(init_p)
    for group_div in group_divisions:
        p = mp.Process(target=compute_objectives,args=(approval_sizes, final_opinions[group_div], minority_projects, majority_projects, "final_"+group_div, op_queue))
        processes.append(p)

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    results = [op_queue.get() for p in processes]

    for r in results:
        fname = 'tmp_res/{}.json'.format(r)
        with open(fname,'r') as f:
            data = json.load(f)
        os.remove(fname)
        objectives_results[r] = data['objectives']
        cc_approvals_results[r] = data['cc']
    assert len(os.listdir('tmp_res')) == 0
    part2 = time.time()
    print('Done with voting and computation in', part2 - part1)

    # Dump objectives results into a json file
    with open('results/objectives_results.json', 'w') as fp:
        json.dump(objectives_results, fp, cls=NumpyEncoder)

    #test_significance(objectives_results)
    save_cc_approvals(cc_approvals_results)   

    # Deliberation plots
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

    
    os.rmdir('tmp_res')
    print('Total time taken: ',time.time()-start)
generate_results()