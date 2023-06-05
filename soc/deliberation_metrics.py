from config import *
import mallows_kendall as mk
#from main import simulate_for_all_group_divs
from util_functions import *
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import multiprocessing as mp
import time


def calc_intergroup_dist(rankings):
	maj_agents = rankings[:int(majority*num_agents)]
	min_agents = rankings[int(majority*num_agents):]
	dist = 0
	for i in maj_agents:
		for j in min_agents:
			dist += mk.distance(i,j)

	num_pairs = len(maj_agents) * len(min_agents)
	#assert num_pairs == 1600
	return dist/num_pairs

def calc_intergroup_ballot_disagreement(rankings,approvals):
	idx = int(majority * num_agents)
	dist = 0
	for i in range(0,idx):
		for j in range(idx,num_agents):
			dist += calc_disagreement(rankings[i][:approvals[i]],rankings[j][:approvals[j]])
	num_pairs = idx * (num_agents - idx)
	#assert num_pairs == 1600
	return dist/num_pairs

def calc_drift(rankings,maj=True):
	idx = int(majority*num_agents)
	r = []
	for i in rankings:
		cut = i[:idx] if maj else i[idx:]
		r.append(cut)
	#print(len(r),len(r[0]),len(r[0][0]))

	init = r.pop(0)
	drift = []
	for i in r:
		d = 0
		assert len(i) == 80 or len(i) == 20
		for j in range(len(i)):
			d += mk.distance(init[j],i[j])
		drift.append(d/len(i))

	return drift

def calc_drift_ballots(rankings,approvals,maj=True):
	idx = int(majority*num_agents)
	if maj:
		low, high = 0, idx
	else:
		low, high = idx, num_agents
	init = rankings.pop(0)
	drift = []
	for i in rankings:
		d = 0
		for j in range(low,high):
			d += calc_disagreement(i[j][:approvals[j]], init[j][:approvals[j]])
		drift.append(d/(high-low))

	return drift

def return_deliberation_metrics(opinions):
	ops = [opinions['initial_opinions']]
	approvals = opinions['approval']
	for group_div in group_divisions:
		ops.append(opinions['final_'+group_div])

	variance = [np.mean(np.var(i,axis=0)) for i in ops]
	#print(variance)

	rankings = [generate_rankings(i) for i in ops]
	intergroup_dist = [calc_intergroup_ballot_disagreement(i,approvals) for i in rankings]
	#print(intergroup_dist)

	maj_drift = calc_drift_ballots(rankings.copy(),approvals,maj=True)
	min_drift = calc_drift_ballots(rankings.copy(),approvals,maj=False)

	res = {}
	res['variance'] = variance
	res['intergroup_dist'] = intergroup_dist
	res['maj_drift'] = maj_drift
	res['min_drift'] = min_drift

	return res

'''
def parallel_compute_metrics(op_queue):
	res = simulate_for_all_group_divs()
	metrics = return_deliberation_metrics(res)
	#metrics.update(res)
	k = [i for i in res.keys() if 'del' in i ]
	for i in k:
		metrics[i] = res[i]
	op_queue.put(metrics)

def parallel_analyser():
	start = time.time()
	print(start)
	variance = []
	intergroup_dist = []
	maj_drift = []
	min_drift = []
	del_rounds = []
	del_mvmt_golfer = []
	del_mvmt_random = []
	batch_size = mp.cpu_count()
	output_queue = mp.Queue()
	results = []
	x = 0
	while x < num_simulations:
		processes = [mp.Process(target=parallel_compute_metrics,args=(output_queue,)) for i in range(min(num_simulations-x,batch_size))]
		for p in processes:
			p.start()

		for p in processes:
			p.join()
		
		results += [output_queue.get() for p in processes]
		x += batch_size
		print('Progress: {}'.format(x))

	assert len(results) == num_simulations
	for metrics in results:
		variance.append(metrics['variance'])
		intergroup_dist.append(metrics['intergroup_dist'])
		maj_drift.append(metrics['maj_drift'])
		min_drift.append(metrics['min_drift'])
		dr = []
		for gd in group_divisions:
			dr.append(metrics['del_rounds_' + gd])
		del_mvmt_golfer.append(metrics['del_movement_iterative_golfer'])
		del_mvmt_random.append(metrics['del_movement_iterative_random'])
		del_rounds.append(dr) 

	xticks = ['initial'] + group_divisions
	var,var_err = np.mean(variance,axis=0),np.std(variance,axis=0)
	plot_results(var,var_err,"Variance",xticks)
	igd,igd_err = np.mean(intergroup_dist,axis=0),np.std(intergroup_dist,axis=0)
	plot_results(igd,igd_err,"Intergroup Ballot Disagreement",xticks)
	xticks.pop(0)
	mjd,mjd_err = np.mean(maj_drift,axis=0),np.std(maj_drift,axis=0)
	plot_results(mjd,mjd_err,"Majority Ballot Drift",xticks)
	mnd,mnd_err = np.mean(min_drift,axis=0),np.std(min_drift,axis=0)
	plot_results(mnd,mnd_err,"Minority Ballot Drift",xticks)
	dr,dr_err = np.mean(del_rounds,axis=0),np.std(del_rounds,axis=0)
	dmg,dmg_err = np.mean(del_mvmt_golfer,axis=0),np.std(del_mvmt_golfer,axis=0)
	dmr,dmr_err = np.mean(del_mvmt_random,axis=0),np.std(del_mvmt_random,axis=0)
	plot_results(dmg,dmg_err,"Deliberation Mvmt Golfer",[str(i) for i in range(len(dmg))])
	plot_results(dmr,dmr_err,"Deliberation Mvmt Random",[str(i) for i in range(len(dmg))])
	print("Time taken for parallel_analyser: ", time.time() - start)

def analyser():
	variance = []
	intergroup_dist = []
	maj_drift = []
	min_drift = []
	
	for i in tqdm(range(10)):
		res = simulate_for_all_group_divs()
		metrics = return_deliberation_metrics(res)

		variance.append(metrics['variance'])
		intergroup_dist.append(metrics['intergroup_dist'])
		maj_drift.append(metrics['maj_drift'])
		min_drift.append(metrics['min_drift'])


	var,var_err = np.mean(variance,axis=0),np.std(variance,axis=0)
	plot_results(var,var_err,"Variance")
	igd,igd_err = np.mean(intergroup_dist,axis=0),np.std(intergroup_dist,axis=0)
	plot_results(igd,igd_err,"Intergroup Ballot Disagreement")
	mjd,mjd_err = np.mean(maj_drift,axis=0),np.std(maj_drift,axis=0)
	plot_results(mjd,mjd_err,"Majority Ballot Drift")
	mnd,mnd_err = np.mean(min_drift,axis=0),np.std(min_drift,axis=0)
	plot_results(mnd,mnd_err,"Minority Ballot Drift")

def plot_results(data,err,title,xticks):
	print(title,data,err)
	plt.figure(figsize=(20,5))
	ax = plt.subplot()
	idx = list(range(len(data)))
	ax.bar(idx,data,yerr=err,ecolor='black', align='center',width=0.3)
	ax.set_xticks(idx)
	ax.set_xticklabels(xticks)
	plt.xlabel('Group Division')
	plt.ylabel(title)
	plt.savefig('del_res/' + title + '.png')
	plt.close()


def sweep_reception_prob():
	rp = [i/10 for i in range(10)]
	for i in rp:
		pass

parallel_analyser()
'''

def plot_deliberation_results(data,err,title,xticks):
	plt.rcParams.update({'font.size': 75})
	gd_names = ['initial', 'random', 'homogeneous', 'heterogeneous', 'iterative golfer', 'iterative random', 'large group']
	#print(title,data,err)
	plt.figure(figsize=(50,30))
	ax = plt.subplot()
	idx = list(range(len(data)))
	ax.bar(idx,data,yerr=err,ecolor='black', align='center',width=0.3)
	ax.set_xticks(idx, rotation=45)
	if title=='Variance':
		ax.set_xticklabels(gd_names, fontsize=75)
	else:
		ax.set_xticklabels(xticks, fontsize=75)
	plt.xlabel('Deliberation Mechanism', fontsize=75)
	plt.ylabel(title, fontsize=75)
	plt.tight_layout(pad=1.0)
	plt.savefig(RESULT_PATH + '/deliberation/' + title + '.png')
	plt.close()


def plot_compare_iterative(golfer,vanilla, golfer_std, vanilla_std, metric='Deliberation Mvmt'):
	#print(golfer,vanilla)
	width = .75
	plt.figure(figsize=(20,10))
	ax = plt.gca()
	xticks = np.arange(num_iterations) + 1
	ax.set_ylabel(metric)
	ax.set_xlabel('Round')

	ax.bar(xticks - .25*width, golfer, yerr = golfer_std, width = width/2, label = 'golfer')
	ax.bar(xticks + .25*width, vanilla, yerr = vanilla_std, width = width/2, label = 'random')
	ax.legend(loc='upper right')
	ax.set_title('Comparing deliberation movement between iterative_golfer and iterative_random')

	plt.savefig(RESULT_PATH + '/deliberation/' + 'Compare Iterative Methods' + '.png')
	plt.close()

    