from scipy import stats
import numpy as np
from config import *
import csv
import json
from scipy.stats import normaltest

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
                        data_1 = objectives_results[setups[i]][obj][rule_id]
                        data_2 = objectives_results[setups[j]][obj][rule_id]
                        
                        r = stats.ttest_ind(data_1, data_2, equal_var=False)
                        writer.writerow([rule_id, setups[i], setups[j], r.pvalue])

def test_normality(objectives_results):
    setups = list(objectives_results.keys())
    for obj in objectives_results['initial'].keys():
        fname = str.format("{}/significance/{}_normality.csv", RESULT_PATH, obj)
        with open(fname, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["Rule", "Setup", "Normality"])
            for rule_id in rules:
                for i in range(len(setups)):
                    data = objectives_results[setups[i]][obj][rule_id]
                    r = normaltest(data)
                    if r.pvalue < 0.05 and obj not in ['ejr_scores', 'pjr_scores', 'jr_scores']:
                        print(obj, rule_id, setups[i], "Not Normal")
                    writer.writerow([rule_id, setups[i], r.pvalue])

# Read json file from results directory
def read_json(fname):
    with open(fname, 'r') as f:
        return json.load(f)

fname = str.format("{}/objectives_results.json", RESULT_PATH)
objectives_results = read_json(fname)
test_significance(objectives_results)
#test_normality(objectives_results)