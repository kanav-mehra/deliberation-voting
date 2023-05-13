# deliberation-voting

This is the code repository for the experiments in the paper "Deliberation and Voting in Approval-Based Multi-Winner Elections" by Kanav Mehra, Nanda K. Sreenivas, Kate Larson [1].

## Code Structure
The required code files are in the "soc" directory. The main code for the experiments can be run using the "soc/generate_results.py" (uses Ray) or "soc/generate_results_mp.py" (uses Python multiprocessing). The respective agent parameters and experimental setup details are defined in config.py. To generate the respective graphs for the experiments, run the "soc/merge_results.py" file. For reproducing results in the paper, please use the config as it is. 

Note: This repository is still a work in progress. Please reach out if you have any questions. 

### References

[1] Kanav Mehra, Nanda K. Sreenivas, Kate Larson: Deliberation and Voting in Approval-Based Multi-Winner Elections. International Joint Conference on Artificial Intelligence (IJCAI) 2023 Main Track. (2023)."
