def calc_disagreement(i,j):
	agreement = len(set(i) & set(j))/min(len(i),len(j))
	return 1 - agreement

# TODO: use numpy to do this better/faster
def gen_rankings_from_utils(utils):
	utils=list(utils)
	rankings = []
	u = utils.copy()
	utils.sort(reverse=True)
	for i in utils:
		rankings.append(u.index(i))
	return rankings

def generate_rankings(opinions):
	rankings = []
	for i in opinions:
		rankings.append(gen_rankings_from_utils(i))
	return rankings


def calc_distance(ops_1,ops_2,approvals):
	assert len(ops_1) == len(ops_2)
	r1 = generate_rankings(ops_1)
	r2 = generate_rankings(ops_2)
	dist = 0
	for i in range(len(r1)):
		#dist += mk.distance(r1[i],r2[i])
		dist += calc_disagreement(r1[i][:approvals[i]],r2[i][:approvals[i]])
	return dist/len(r1)