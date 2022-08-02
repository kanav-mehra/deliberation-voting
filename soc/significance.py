from scipy import stats
import numpy as np
from config import *
import csv

RESULT_PATH = 'results'

def test_significance(objectives_results):
    setups = list(objectives_results.keys())
    for obj in objectives_results['initial'].keys():
        fname = str.format("{}/significance/{}.csv", RESULT_PATH, obj)
        with open(fname, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["Rule", "Setup", "Setup", "Significance"])
            for rule_id in rules:
                for i in range(len(setups)):
                    for j in range(i+1, len(setups)):
                        r = stats.ttest_rel(objectives_results[setups[i]][obj][rule_id], objectives_results[setups[j]][obj][rule_id])
                        writer.writerow([rule_id, setups[i], setups[j], r.pvalue])
                        #if r.pvalue > 0.05:
                        #    print(str.format("{} {} {} {} {}", obj, rule_id, setups[i], setups[j], r))