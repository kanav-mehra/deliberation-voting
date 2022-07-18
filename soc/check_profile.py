from abcvoting import abcrules, properties
from approval_profile import ApprovalProfile
from objectives import utilitarian_score, representation_score, satisfaction_score
from config import *


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