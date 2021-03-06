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
    def __init__(self, experiment_name = 'MST', groups = [], key = "cor_seqsum_lpn", level = "pn", paradigma = 0, is_independent = False):
        self.groups = groups
        self.experiment_name = experiment_name
        self.key = key
        self.is_independent = is_independent
        self.paradigma = paradigma
        self.level = level
        self.test_group_differences_ttest(key, self.is_independent, self.paradigma, self.level)

    def test_group_differences_ttest(self, key, is_independent, paradigma, level):
        # ich laufe ueber die Buchstaben der levelbeschreibung und ziehe die richtigen Daten heraus
        values = self.get_target_values_by_key(key)
        for i in range(len(level)):
            if level[i]== 'p':
                values = self.filter_target_values_by_paradigma(values, paradigma)
            if level[i]=='n':
                self.test_group_differences_two_groups(key, values, is_independent=is_independent)

#        d = self.get_target_values_by_key_and_level(key, paradigma, level)
 #       if len(d)==2:
            
    

    def get_target_values_by_key(self, key):
        """ get the target attributes out of the experiment objects 
            and put these into a list for each group 
        """
        target_val = []
        for group in self.groups:
            subject_list = []
            for subj_exp in group.subj_exp_list:
                exp_value = getattr(subj_exp, key)
                subject_list.append(exp_value)
            target_val.append(subject_list)
        return target_val

    def filter_target_values_by_paradigma(self,values, paradigma):
        new_val = []
        for attribute_list in values:
            new_attribute_list = []
            for attribute in attribute_list:
                new_attribute_list.append(attribute[paradigma])
            new_val.append(new_attribute_list)
        return new_val


    def list_of_list_to_list(self, input_list):
        # if input_list is a list of list then it will be transformed to a list
        # by averaging the second dimension
        if any(isinstance(el, list) for el in input_list):
            input_list = [statistics.mean(f) for f in input_list]
        return input_list

    def test_group_differences_two_groups(self, key, data, is_independent=True):
        # reduce a list of lists to a list by averaging
        G1 = self.list_of_list_to_list(data[0])
        G2 = self.list_of_list_to_list(data[1])
            
        if is_independent:
            t, p = stats.ttest_ind(G1, G2)
        else:
            t, p = stats.ttest_rel(G1, G2)
        m = [statistics.mean(G1), statistics.mean(G2)]
        std = [statistics.stdev(G1), statistics.stdev(G2)]

        self.print_pt_2g(key=key, t=t,p=p, mymean = m, std=std)


    def get_target_values_by_key_level_1(self, key, paradigma):
        # extracts from the dictionaries of all groups the value
        # with key = key
        # returns a list with groups, the group list consists of a list with the key elements
        target_val = []
        for group in self.groups:
            subject_list = []
            for subj_exp in group.subj_exp_list:
                exp_value = getattr(subj_exp, key)[paradigma]
                print(exp_value)
                subject_list.append(exp_value)
            target_val.append(subject_list)
        return target_val


    def print_pt_2g(self, key, t, p, mymean=0, std=0):
        mymean = [float(m) for m in mymean]
        std = [float(s) for s in std]
        print(f"{key} p = {p:.7}  with t = {t:.3}  (mean = {mymean[0]:.3} +- {std[0]:.4}  vs. {mymean[1]:.3} +- {std[1]:.4}")

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
