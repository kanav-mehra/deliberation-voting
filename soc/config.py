num_agents = 100
majority = 0.8
num_alternatives = 50
num_winners = 5

approval_low = 3
approval_high = 10
#approval_choices = list(range(approval_low, approval_high+1))
approval_choices = [9,10,11]

num_simulations = 100
group_size = 10
profile_eligibility_threshold = 0.9

phi = 0.2

ingroup_bias = 0.2
outgroup_bias = 0.1
delta = 0.4


rules = ["av", "cc", "seqcc", "rule-x", "minimaxav", "sav", "slav", "pav", "seqpav", "geom1.5", "geom2", "geom5", "monroe"]
group_divisions = ['random','homo_demo','hetero_demo']