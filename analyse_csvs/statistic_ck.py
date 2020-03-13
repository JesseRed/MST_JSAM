import os, json
import numpy as np
from numpy.random import randn
from numpy.random import seed
from numpy import mean
from numpy import var
from math import sqrt
from scipy import stats 
from scipy.stats import ttest_1samp, ttest_ind, ttest_rel
import statistics

class Statistic():
    def __init__(self, experiment = 'MST', group_list=[] , data_path = ".\\Data_python", _ids = None):
        self.group_list = group_list
        self.experiment = experiment
        self.data_path = data_path
        self._ids = _ids
        self.data = self.get_data_from_json_file(self.data_path, self._ids)
        # data is a list of groups
        # each group consists of a list of dictionaries 
        # one dictionary correspond to one subject
        # in these dictionaries are all data of the subjects
        # e.g. self.data[1][4]["corrsq_slope"] - der slope der lernleistung der 2.Gruppe des 5. Pateinten
        # self.prepare_data_json()

    def get_data_from_json_file(self, data_path, _ids):
        ''' get all data from the directory (data_path) and the prefix _ids
            the prefix is a list
            the number of list elements defines the number of different groups
        '''
        print("get data from json files")
        data = [] # list across groups
        for prefix in _ids:
            filenames = [filename for filename in os.listdir(data_path) if filename.startswith(prefix)]
            dict_list = []
            for filename in filenames:
                with open(os.path.join(data_path,filename), "r") as fp:   #Pickling
                    dict_list.append(json.load(fp))
            data.append(dict_list)
        return data

    def test_group_differences_ttest(self, key):
        d = self.get_target_values_by_key(key)
        if len(d)==2:
            self.test_group_differences_two_groups(key, d)
    
    def test_group_differences_two_groups(self, key, data):
        t, p = stats.ttest_ind(data[0], data[1])
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
        for group in self.data:
            subject_list = []
            for subj_dict in group:
                subject_list.append(subj_dict[key])
            target_val.append(subject_list)
        return target_val


    def print_pt_2g(self, key, t, p, mean = 0, std = 0):
        print(f"p = {p:.7}  with t = {t:.3}  (mean = {mean[0]:.3} +- {std[0]:.4}  vs. {mean[1]:.3} +- {std[1]:.4}")


if __name__ == "__main__":
    # seed random number generator
    experiment_name = 'MST'
    _ids = ["MST_G1_", "MST_G2_"]
    my_stat = Statistic(experiment = experiment_name, group_list= [], data_path = ".\\Data_python", _ids = _ids)
    my_stat.test_group_differences_ttest('corrsq_slope')
