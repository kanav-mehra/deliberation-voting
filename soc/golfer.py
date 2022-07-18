import random
import numpy as np
from copy import deepcopy
import math
import time

GENERATIONS = 30
RANDOM_GENERATIONS = 2
MAX_EXPLORE = 5

def social_golfer(groups, group_size, num_rounds):
    """
    Given a group of players, a group size, and the number of rounds, return
    the group splits such that two players meet each other at most once.
    """
    num_golfers = groups * group_size
    weights = np.zeros((num_golfers, num_golfers) , dtype=int)

    def score(round, weights):
        """
        Given a round and the weights matrix, return the score.
        """
        group_scores = []
        for i in range(len(round)):
            group_score = 0
            for j in range(len(round[i])-1):
                for k in range(j+1,len(round[i])):
                    group_score += weights[round[i][j]][round[i][k]]**2
            group_scores.append(group_score)
        return {'groups': round, 'group_scores': group_scores, 'score': sum(group_scores)}

    def generate_permutation():
        """
        Generate a random permutation of the players split into groups.
        """
        players = list(range(num_golfers))
        random.shuffle(players)
        return [players[i*group_size:(i+1)*group_size] for i in range(groups)]
    
    def generate_candidates(options, weights):
        """
        Given a list of options and the weights matrix, return a list of
        candidates by generating mutating groups.
        """
        candidates = []
        for option in options:
            scored_groups = zip(option['groups'], option['group_scores'])
            sorted_scored_groups = sorted(scored_groups, key=lambda x: x[1], reverse=True)
            sorted_groups = [x[0] for x in sorted_scored_groups]
            #candidates.append(option)
            
            for i in range(group_size):
                for j in range(group_size, num_golfers):
                    candidates.append(score(swap(sorted_groups, i, j), weights))

            for i in range(RANDOM_GENERATIONS):
                candidates.append(score(generate_permutation(), weights))
    
        return candidates
    
    def swap(groups, i, j):
        """
        Given a list of groups and two indices, swap the players
        """
        new_candidate = deepcopy(groups)
        new_candidate[math.floor(i / group_size)][i % group_size] = groups[math.floor(j / group_size)][j % group_size]
        new_candidate[math.floor(j / group_size)][j % group_size] = groups[math.floor(i / group_size)][i % group_size]
        return new_candidate
            
    def update_weights(round, weights):
        """
        Given a round and the weights matrix, update the weights matrix.
        """
        for i in range(len(round)):
            for j in range(len(round[i])-1):
                for k in range(j+1,len(round[i])):
                    weights[round[i][j]][round[i][k]] += 1
                    weights[round[i][k]][round[i][j]] += 1

    rounds = []
    round_scores = []
    
    for i in range(num_rounds):
        options = []
        for k in range(5):
            permutation = generate_permutation()
            score_ = score(permutation, weights)
            options.append(score_)
        
        best_option = min(options, key=lambda x: x['score'])
        generation = 0
        while(generation < GENERATIONS and best_option['score']>0):
            candidates = generate_candidates(options, weights)
            # sort candidates by score
            best_option = min(candidates, key=lambda x: x['score'])
            # fliter candidates where score is less than or equal to best_option
            options = [x for x in candidates if x['score'] <= best_option['score']]
            random.shuffle(options)
            options = options[:MAX_EXPLORE]
            generation += 1
        
        rounds.append(best_option['groups'])
        round_scores.append(best_option['score'])

        #print("Round {}: {}\nConflict Score: {}\n".format(i, best_option['groups'], best_option['score']))

        update_weights(best_option['groups'], weights)
    
    return rounds, round_scores

#time_start = time.time()
#social_golfer(10, 10, 5)
#time_end = time.time()
#print("Time: {}".format(time_end-time_start))