import mallows_hamming as mh
import random
import numpy as np
from config import *



def lex_dist(a,b):
	s = 0
	for i in range(num_alternatives):
		s += (a-b)*2**(num_alternatives-i)
	return s

def compute_pairwise_dist(res):
	d = 0
	for idx,i in enumerate(res):
		for j in res[idx+1:]:
			if (i == j).all():
				continue
			d += mh.distance(i,j)
	
	n = len(res)
	pairs = n*(n-1)/2
	d = d/pairs
	print(d)
	return d

def generate_samples(phi):
	res = mh.sample(100,num_alternatives,phi=phi,s0=seed)
	d = []
	ld = []
	for i in res:
		dist = mh.distance(seed,i)
		#print(dist)
		d.append(dist)
		ld.append(lex_dist(seed,i))
	compute_pairwise_dist(res)
	#print(np.mean(d))
	#print(np.mean(ld))
	return np.mean(d),np.mean(ld)

seed_0 = [7,3,14,12,8,17,16,0,9,13,19,11,10,18,4,15,5,2,1,6]
seed_1 = [1,4,3,6,14,7,9,17,5,15,19,11,10,2,13,8,16,12,0,18]
seed_1_x = mh.sample_at_dist(num_alternatives,20,seed_0)
print(seed_1_x)
print(mh.distance(seed_0,seed_1))

exit()
seed = list(range(num_alternatives))
random.shuffle(seed)
print(seed)
phis = [0.01,0.02,0.05,0.08,0.1,0.2]
for i in phis:
	a,b = generate_samples(i)
	print(i,a,b)