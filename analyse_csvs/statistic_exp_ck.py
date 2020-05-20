import os, json
import numpy as np
import pandas as pd
from numpy.random import randn
from numpy.random import seed
from numpy import mean
from numpy import var
from math import sqrt
from scipy import stats 
from scipy.stats import ttest_1samp, ttest_ind, ttest_rel
import statistics
import matplotlib.pyplot as plt

class Statistic_Exp():
    def __init__(self, experiment_name = 'MST', groups = [], key = "cor_seqsum_lpn", level = 1, paradigma = 0, is_independent = False):
        self.groups = groups
        self.experiment_name = experiment_name
        self.key = key
        self.is_independet = is_independent
        self.paradigma = paradigma
        self.level = level
        self.test_group_differences_ttest(self, key, is_independent = False)

    def test_group_differences_ttest(self, key, is_independent=True):
        d = self.get_target_values_by_key(key)
        if len(d)==2:
            self.test_group_differences_two_groups(key, d, is_independent=is_independent)
    
    def test_group_differences_two_groups(self, key, data, is_independent=True):
        if is_independent:
            t, p = stats.ttest_ind(data[0], data[1])
        else:
            t, p = stats.ttest_rel(data[0], data[1])
        mean = []
        mean.append(sum(data[0])/len(data[0]))
        mean.append(sum(data[1])/len(data[1]))
        std = []
        std.append(statistics.stdev(data[0]))
        std.append(statistics.stdev(data[1]))
        self.print_pt_2g(key=key, t=t,p=p, mean = mean, std = std)

    def get_target_values_by_key(self, key):
        # extracts from the dictionaries of all groups the value
        # with key = key
        # returns a list with groups, the group list consists of a list with the key elements
        target_val = []
        for group in self.groups:
            subject_list = []
            for subj_exp in group.subj_exp_list:
                subject_list.append(getattr(subj_exp, key))
            target_val.append(subject_list)
        return target_val


    def print_pt_2g(self, key, t, p, mean = 0, std = 0):
        print(f"{key} p = {p:.7}  with t = {t:.3}  (mean = {mean[0]:.3} +- {std[0]:.4}  vs. {mean[1]:.3} +- {std[1]:.4}")

    def show_group_differences(self, key):
        data = self.get_target_values_by_key(key)
        data = np.asarray(data)
        print(f"Group Results of {key}")
        df = pd.DataFrame(data.T, columns = [self._ids[0], self._ids[1]])
        print(df.head(30))

    def plot_one_group_sequence(self, key):
        data = self.get_target_values_by_key(key)
        #print(data)
        #print("---")
        data = data[0]
        #print(np.asarray(data))
        #print(data)
        #print(data.shape)
        for subj in data:
            plt.plot(subj)
        
        plt.show()
        # plt.plot( 'x', 'y1', data=data, marker='o', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=4)
        # plt.plot( 'x', 'y2', data=df, marker='', color='olive', linewidth=2)
        # plt.plot( 'x', 'y3', data=df, marker='', color='olive', linewidth=2, linestyle='dashed', label="toto")
        # plt.legend()

    
if __name__ == "__main__":
    # seed random number generator
    experiment_name = 'MST'
    experiment_name = 'ASTEROID'
    _ids = ["MST_G1_", "MST_G2_"]
    _ids = ["ASTEROID_G1_", "ASTEROID_G2_"]
    my_stat = Statistic(experiment = experiment_name, group_list= [], data_path = ".\\Data_python", _ids = _ids)
    #my_stat.test_group_differences_ttest('corrsq_slope')
    my_stat.test_group_differences_ttest('success_per_block_slope', is_independent=False)
    my_stat.test_group_differences_ttest('abs_success', is_independent=False)
    my_stat.show_group_differences('abs_success')
    my_stat.show_group_differences('success_per_block_slope')
