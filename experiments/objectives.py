from abcvoting import abcrules, properties
from abcvoting.output import output, INFO, DETAILS, WARNING
from svvamp import GeneratorProfileCubicUniform, Profile
import numpy as np
from abcvoting.preferences import Profile as abcpf
from tqdm import tqdm
from approval_profile import ApprovalProfile

def intersection(a, b):
    return list(set(a) & set(b))

def utilitarian_score(candidate_committee, profile):
    '''
    Given an approval profile, calculates the utilitarian score for a winning committee
    Utility Score = Sum of utilities for each voter over candidates in the winning committee
    '''
    utility_score = 0
    for idx in range(len(profile.profile_pref_topk)):
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

'''
def nash_welfare_score(candidate_committee, profile):
    #Given an approval profile, calculates the nash welfare score for a winning committee
    #Nash Welfare Score = Product of utilities for each voter over candidates in the winning committee
    nash_score = 1
    for idx in range(len(profile.profile_pref_topk)):
        nash_score *= profile.profile.preferences_ut[idx, candidate_committee].sum()
    return nash_score
'''