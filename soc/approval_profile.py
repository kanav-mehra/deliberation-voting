from abcvoting import abcrules, properties
from abcvoting.output import output, INFO, DETAILS, WARNING
from svvamp import GeneratorProfileCubicUniform, Profile
import numpy as np
from abcvoting.preferences import Profile as abcpf
from tqdm import tqdm

class ApprovalProfile():
    def __init__(self, num_voters, num_candidates, committee_size, num_approval, utilities):
        self.num_voters = num_voters
        self.num_candidates = num_candidates
        self.committee_size = committee_size
        self.num_approval = num_approval

        self.profile = Profile(preferences_ut=utilities)

        self.profile_pref_topk = self.profile.preferences_rk[:,:num_approval]
        self.optimal_welfare_committee = np.argpartition(self.profile.total_utility_c, -committee_size)[-committee_size:]
        self.optimal_welfare = self.profile.total_utility_c[self.optimal_welfare_committee].sum()

        self.profile_abc = abcpf(num_cand=num_candidates)
        self.profile_abc.add_voters(self.profile_pref_topk)