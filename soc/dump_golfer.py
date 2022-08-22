from golfer import social_golfer
from config import *
import multiprocessing as mp
import numpy as np
import time

def dump_and_generate(N):
	res = []
	num_groups = num_agents//group_size
	for i in range(N):
		rounds, _ = social_golfer(num_groups,group_size,num_iterations)
		res.append(rounds)

	res = np.array(res)

	with open('golfer_rounds.npy', 'wb') as f:
		np.save(f, res)

def gen(output_q):
	num_groups = num_agents//group_size
	rounds, _ = social_golfer(num_groups,group_size,10)
	output_q.put(rounds)

def dump(N):
	start = time.time()
	queue = mp.Queue()
	batch = 10
	results = []
	for i in range(N//batch):
		processes = [mp.Process(target=gen,args=(queue,)) for i in range(N)]
		for p in processes:
			p.start()
		for p in processes:
			p.join()

		results += [queue.get() for i in processes]
		print("Done with round {}".format(i))
	print(results)
	results = np.array(results)
	with open('golfer_10rounds.npy', 'wb') as f:
		np.save(f, results)
	print(time.time() - start)

def read_results():
	with open('golfer_dump.npy', 'rb') as f:
		res = np.load(f)
		idx = np.random.choice(len(res))
		print(res[idx])
		print(res.shape)

#generate_and_dump(2)
#dump(50)
read_results()