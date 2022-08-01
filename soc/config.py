num_agents = 100
majority = 0.8
num_alternatives = 50
num_winners = 5

approval_mean = 10
approval_std = 2
#approval_choices = list(range(approval_low, approval_high+1))
approval_choices = [10]

num_simulations = 100
group_size = 10
profile_eligibility_threshold = 0.9

phi = 0.2

const_bc_flag = False
ingroup_bias = 0.2
outgroup_bias = 0.1
delta = 0.4

rules = ["av", "cc", "seqcc", "rule-x", "minimaxav", "sav", "pav", "seqpav", "geom2", "monroe"]
group_divisions = ['random','homo_demo','hetero_demo', 'iterative_golfer', 'iterative_random','large_group']
#group_divisions = ['large_group']

num_iterations = 5
num_groups = int(num_agents/group_size)