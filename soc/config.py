num_agents = 100
<<<<<<< HEAD
majority = 0.8
num_alternatives = 100
=======
num_alternatives = 50
>>>>>>> d571910af56e806d0176ce2b1c172bff35bd3bc7
num_winners = 5
num_approval = 10
num_simulations = 100
group_size = 10

phi = 0.2

ingroup_bias = 0.2
outgroup_bias = 0.1
delta = 0.4

<<<<<<< HEAD
=======
seed_0 = list(range(num_alternatives))
seed_1 = list(range(num_alternatives))
#seed_1.reverse()
random.shuffle(seed_0)
random.shuffle(seed_1)
#seed_1 = mh.sample_at_dist(num_alternatives, num_alternatives, seed_0)
print(seed_0)
print(seed_1)
>>>>>>> d571910af56e806d0176ce2b1c172bff35bd3bc7

rules = ["av", "cc", "seqcc", "rule-x", "minimaxav", "sav", "slav", "pav", "seqpav", "geom1.5", "geom2", "geom5", "monroe"]
group_divisions = ['random','homo_demo','hetero_demo']