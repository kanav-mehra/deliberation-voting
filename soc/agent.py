from config import *
import mallows_hamming as mh
import mallows_kendall as mk
import numpy as np
import random

def generate_uniform_utils(ranking):
	s = list(np.random.uniform(0,1,size=num_alternatives))
	s.sort(reverse=True)
	#print(s)
	utils = [0 for i in range(num_alternatives)]
	for idx,i in enumerate(ranking):
		utils[int(i)] = s[idx]
	#print(utils)
	return utils

def generate_harmonic_utils(ranking):
	utils = [0 for i in range(num_alternatives)]
	for idx,i in enumerate(ranking):
		utils[int(i)] = 1/(idx+1)
	return utils

def generate_opinions(demo):
	seed = seed_0 if demo == 0 else seed_1
	ranking = mk.sample(1,num_alternatives,phi=phi,s0=seed)[0]
	#print(ranking)
	utils = generate_uniform_utils(ranking)
	return utils

class Agent:
	def __init__(self,id,demo,ingroup_bias=ingroup_bias,outgroup_bias=outgroup_bias,delta=delta):
		self.id = id
		self.debug = False if id==0 else False
		self.demo = demo
		self.ingroup_bias = ingroup_bias
		self.outgroup_bias = outgroup_bias
		self.delta = delta
		self.init_opinions = generate_opinions(demo)
		self.opinions = self.init_opinions.copy()
		self.ops_heard = 0
		self.ops_listened = 0
		self.ops_updated = [0 for i in range(num_alternatives)]

	def update(self,src,src_demo,prob):
		self.ops_heard += 1
		if random.random() >= prob:
			return
		self.ops_listened += 1
		alpha = self.ingroup_bias if src_demo == self.demo else self.outgroup_bias
		for i in range(num_alternatives):
			l = self.opinions[i] - self.delta
			u = self.opinions[i] + self.delta
			if src[i] >= l and src[i] <= u:
				if self.debug:
					print(i,self.opinions[i],src[i],alpha)
				self.opinions[i] += alpha*(src[i] - self.opinions[i])
				if self.debug:
					print(self.opinions[i])
				self.ops_updated[i] += 1


def test():
	a = Agent(1,1)
	print(a.opinions)

#test()