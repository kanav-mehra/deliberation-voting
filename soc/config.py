# Setup
num_agents = 100
majority = 0.8
num_alternatives = 30
num_winners = 3
num_simulations = 100

# Ballot params
approval_mean = 2*num_winners
approval_std = 1
#approval_choices = list(range(approval_low, approval_high+1))
#approval_choices = [3,4,5,6,7,8,9,10]

group_size = 10
profile_eligibility_threshold = 0.9
phi = 0.2

# BC Params
const_bc_flag = False
bc_params_dist = 'UNIFORM'
bc_std = 0.25
bc_mean = 0.5
ingroup_bias = 0.2
outgroup_bias = 0.1
delta = 0.4

#rules = ["av", "cc", "seqcc", "rule-x", "minimaxav", "sav", "pav", "seqpav", "geom2", "monroe"]
#group_divisions = ['random','homo_demo','hetero_demo', 'iterative_golfer', 'iterative_random','large_group','large_group_wrp']

rules = ["av", "rule-x", "pav", "cc"]
group_divisions = ['random','homo_demo','hetero_demo', 'iterative_golfer', 'iterative_random','large_group']

num_iterations = 5
deliberation_stopping_threshold = 0.0
num_groups = int(num_agents/group_size) 
golfer_from_file = True

RESULT_PATH = 'results'+str(num_alternatives)