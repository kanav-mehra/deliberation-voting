from abcvoting import abcrules, properties
from abcvoting.output import output, INFO, DETAILS, WARNING
from svvamp import GeneratorProfileCubicUniform, Profile
import numpy as np
import csv
from abcvoting.preferences import Profile as abcpf
from tqdm import tqdm
from approval_profile import ApprovalProfile
from objectives import utilitarian_score, representation_score

def generate_baseline_results(rules, num_candidates, committee_size, num_voters, num_simulations):
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
        
        profile = ApprovalProfile(num_voters, num_candidates, committee_size)

        cc_committee = abcrules.compute("cc", profile.profile_abc, committeesize=committee_size, resolute=True)[0]
        optimal_representation = representation_score(cc_committee, profile)
        
        for rule_id in rules:
            result = abcrules.compute(rule_id, profile.profile_abc, committeesize=committee_size, resolute=True)[0]
            
            rep_score = representation_score(result, profile)
            representation_ratio[rule_id] += rep_score/optimal_representation
            
            utilitarian_ratio[rule_id] += utilitarian_score(list(result), profile)/profile.optimal_welfare
            raw_representation_score[rule_id] += rep_score
            
            ejr_scores[rule_id] += int(properties.check_EJR(profile.profile_abc, result))
            jr_scores[rule_id] += int(properties.check_JR(profile.profile_abc, result))
            pjr_scores[rule_id] += int(properties.check_PJR(profile.profile_abc, result))
                    
    return representation_ratio, utilitarian_ratio, raw_representation_score, ejr_scores, jr_scores, pjr_scores

if __name__ == "__main__":
    num_candidates = 20
    committee_size = 5
    num_voters = 100
    num_simulations = 10
    rules = ["av", "cc", "seqcc", "rule-x", "minimaxav", "sav", "pav"]
    file_name = str.format("nC{}_nK{}_nV{}_nS{}_{}", num_candidates, committee_size, num_voters, num_simulations, "experiments.csv")

    representation_ratio, utilitarian_ratio, raw_representation_score, ejr_scores, jr_scores, pjr_scores = generate_baseline_results(rules, num_candidates, committee_size, num_voters, num_simulations)

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