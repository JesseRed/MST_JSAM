import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from os import listdir, rename
from os.path import isfile, join
from mst import MST
from srtt import SRTT
from asteroid import ASTEROID
from scipy import stats 
import datetime

class Group():
    def __init__(self, experiment = 'MST', path_inputfiles="./Data MST", filepattern="Tag1", path_outputfiles = ".\\Data_python", _id = None, sequence_length=10, is_estimate_network = False):
        self.experiment = experiment
        self.path_inputfiles = path_inputfiles
        self.sequence_length = sequence_length # only relevant for MST
        self.filepattern = filepattern
        self.path_outputfiles = path_outputfiles
        self.is_estimate_network = is_estimate_network
        self.files = self.get_group_files()
        self.subj_class_list = []
                                                                                                    
        # create file identifier for all datafiles which will be created for this analysis
        if not _id:
            self._id = "MST_" + datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
        else:
            self._id = _id
        #self.get_data()
        
    def get_group_files(self):
        file_list = []
        for file in os.listdir(self.path_inputfiles):
            if self.filepattern in file:
                file_list.append(os.path.join(self.path_inputfiles, file))
        return file_list

    def get_data(self):
        """ get data from every mst.csv file
        """            
        # self.improvement = []
        # self.corrsq = []
        for filename in self.files:
            if self.experiment == 'MST':
                subj_class = MST(fullfilename = filename, sequence_length = self.sequence_length, path_output = self.path_outputfiles, _id = self._id)
            if self.experiment == 'SRTT':
                subj_class = SRTT(fullfilename = filename, path_output = self.path_outputfiles, _id = self._id)
            #    subj_class = SRTT(filename)
            if self.experiment == 'ASTEROID':
                subj_class = ASTEROID(fullfilename = filename, path_output = self.path_outputfiles, _id = self._id)
            if self.is_estimate_network:
                subj_class.add_network_class(coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= True, is_estimate_Q= True, num_random_Q=3)
        
            self.subj_class_list.append(subj_class)
        #     self.corrsq.append(mst.corrsq)
        #     self.improvement.append(mst.improvement)

    def perform_network_analysis(self):
        for subj in self.subj_class_list:
            subj.add_network_class()

    def save_data(self):
        for subj in self.subj_class_list:
            subj.save()

        # print(f"cor = {self.improvement}")
        # print(f"improvement = {self.improvement}")
        # print(f"mittelwert der improvement = {np.mean(self.improvement)}")
        # print(f"Standardabweichung der lersteigung = {np.std(self.improvement)}")

if __name__ == '__main__':
    print(f"Gruppe 1")
    mst_group1 = Group(experiment = 'MST', path_inputfiles = ".\\Data MST", filepattern="Tag1", path_outputfiles = ".\\Data_python", sequence_length = 10)
    mst_group1.get_data()
    mst_group1.save_data()
    print(f"Gruppe 2")
    mst_group2 = Group(experiment = 'MST', path_inputfiles = ".\\Data MST", filepattern="Tag2", path_outputfiles = ".\\Data_python", sequence_length = 10)
    mst_group2.get_data()
    mst_group2.save_data()
    # print(mst_group1.corrsq)

    # statistic, pval = stats.ttest_ind(mst_group1.corrsq, mst_group2.corrsq)
    # print(f"statistic = {statistic}")
    # for i in pval:
    #     print(f"Block[i+1] - pval = {i:.4}")
