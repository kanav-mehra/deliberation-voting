from abcvoting import abcrules, properties
from abcvoting.output import output, INFO, DETAILS, WARNING
from svvamp import GeneratorProfileCubicUniform, Profile
import numpy as np
from abcvoting.preferences import Profile as abcpf
from tqdm import tqdm
from config import *
from approval_profile import ApprovalProfile
import itertools, math, ray

def intersection(a, b):
    return list(set(a) & set(b))

def utilitarian_score(candidate_committee, profile):
    '''
    Given an approval profile, calculates the utilitarian score for a winning committee
    Utility Score = Sum of utilities for each voter over candidates in the winning committee
    '''
    utility_score = 0
    for idx in range(num_agents):
        utility_score += profile.profile.preferences_ut[idx, candidate_committee].sum()
    return utility_score

def representation_score(candidate_committee, profile):
    '''
    Given an approval profile, calculates the representation score for a winning committee
    Representation Score = Sum of representation for each voter in the winning committee
    '''
    rep_score = 0
    for voter in profile.profile_pref_topk:
        rep_score += min(1, len(intersection(candidate_committee, voter)))
    return rep_score

def satisfaction_score(candidate_committee, profile):
    '''
    Given an approval profile, calculates the satisfaction score for a winning committee
    Satisfaction Score = Sum of satisfaction for each voter in the winning committee
    '''
    sat_score = 0
    for voter in profile.profile_pref_topk:
        sat_score += len(intersection(candidate_committee, voter))
    return sat_score

def project_representation_score(candidate_committee, minority_projects, majority_projects):
    '''
    Given a candidate committee, calculates the projects represented for majority/minority based
    on their initial approvals.
    '''
    min_project_score = len(intersection(candidate_committee, minority_projects))
    maj_project_score = len(intersection(candidate_committee, majority_projects))
    return min_project_score, maj_project_score

def approval_scores(candidate_committee, profile):
    '''
    Given an approval profile, calculates the approval scores for a winning committee
    Approval Score = Approvals for each candidate in the winning committee
    '''
    approval_score = []
    for candidate in candidate_committee:
        cand_score = 0
        for voter in profile.profile_pref_topk:
            if candidate in voter:
                cand_score += 1
        approval_score.append(cand_score)
    return np.sort(approval_score)


def nash_welfare_score(candidate_committee, profile):
    '''
    Given an approval profile, calculates the nash welfare score for a winning committee
    Nash Welfare Score = Product of utilities for each voter over candidates in the winning committee
    '''
    nash_score = 1
    for idx in range(num_agents):
        nash_score *= (profile.profile.preferences_ut[idx, candidate_committee].sum())
    return pow(nash_score, (1/num_agents))

@ray.remote
def perc_satisfaction(prof, rule, committee):
    datax = []
    datay = []
    k = num_winners
    num_cohesive_groups = 0
    for cohesiveness in range(1,k+1):
        for s in itertools.combinations(prof.candidates, cohesiveness):
            voters = [i for i in range(len(prof)) if set(s) <= prof[i].approved]
            if len(voters)*k/len(prof) >= cohesiveness:
                num_cohesive_groups += 1
                satisfaction = [len(set(committee) & prof[i].approved) for i in voters]
                satisfaction.sort()
                for subgroupsize in range(len(voters),0,-1):
                    if subgroupsize*k < cohesiveness*len(prof): # corresponds to subgroupsize*k/len(prof.preferences) < cohesiveness*
                        break  # group too small to have a justifiable representation of *cohesiveness*
                    num_cohesive_groups += math.comb(len(voters), subgroupsize)
                    dataxpoint = subgroupsize/float(len(prof))
                    jar = min(subgroupsize*k/float(len(prof)),cohesiveness)
                    dataypoint = sum(satisfaction[:subgroupsize])/float(subgroupsize*jar)  # average satisfaction / jar
                    if dataypoint <= 0.9999999:  # only a violation if smaller than 1 ( 0.9999999 chosen due to float rounding)
                        datax.append(dataxpoint)
                        datay.append(dataypoint)
    return rule, datax, datay, num_cohesive_groups