from abcvoting import abcrules, properties
from abcvoting.output import output, INFO, DETAILS, WARNING
from svvamp import GeneratorProfileCubicUniform, Profile
import numpy as np
from abcvoting.preferences import Profile as abcpf
from tqdm import tqdm
import random

class ApprovalProfile():
    def __init__(self, num_agents, num_alternatives, num_winners, approvals, utilities):
        self.num_agents = num_agents
        self.num_alternatives = num_alternatives
        self.num_winners = num_winners
        self.approvals = approvals

        self.profile = Profile(preferences_ut=utilities)
        self.profile_pref_topk = []

        for i in range(num_agents):
            self.profile_pref_topk.append(self.profile.preferences_rk[i,:self.approvals[i]])
        
        self.optimal_welfare_committee = np.argpartition(self.profile.total_utility_c, -num_winners)[-num_winners:]
        self.optimal_welfare = self.profile.total_utility_c[self.optimal_welfare_committee].sum()

        self.profile_abc = abcpf(num_cand=num_alternatives)
        self.profile_abc.add_voters(self.profile_pref_topk)