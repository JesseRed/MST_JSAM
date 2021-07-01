import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, logging
from os import listdir, rename
from os.path import isfile, join
from mst import MST
from seq import SEQ
from srtt import SRTT
from asteroid import ASTEROID
from scipy import stats 
import datetime
import multiprocessing
from experiment import Experiment

logger = logging.getLogger(__name__)


class Group_pooling():
    def __init__(self, vpns=[], day=0, experiment_name='MST', 
                 path_inputfiles="./Data MST", filepattern="Tag1", 
                 path_outputfiles=".\\Data_python", paradigma=0, 
                 sequence_length=8):
        self.day = day
        self.vpns = vpns
        self.experiment_name = experiment_name
        self.path_inputfiles = path_inputfiles
        self.sequence_length = sequence_length  # only relevant for MST
        self.filepattern = filepattern
        self.path_outputfiles = path_outputfiles

        #self.files = self.get_group_files()
        self.subj_exp_list = []
        
    # def get_group_files(self):
    #     file_list = []
    #     for file in os.listdir(self.path_inputfiles):
    #         if self.filepattern in file:
    #             file_list.append(os.path.join(self.path_inputfiles, file))
    #     return file_list

    def load_data(self):
        for vpn in self.vpns:
            exp = Experiment(self.experiment_name, vpn, self.day, self.sequence_length, is_load=True)
            exp2 = exp.load()
            self.subj_exp_list.append(exp2)
        

if __name__ == '__main__':
    print(f"Gruppe 1")
    # seq_group1 = Group(experiment = 'SEQ', path_inputfiles = ".\\Data\\SEQ", filepattern="Elisabeth", path_outputfiles = ".\\Data_python", sequence_length = 8, is_estimate_network=True)
    #seq_group1 = Group_pooling(experiment = 'MST', path_inputfiles = ".\\Data\\MST", filepattern="Elisabeth", path_outputfiles = ".\\Data_python", sequence_length = 8, is_estimate_network=True)
    # seq_group1 = Group(experiment = 'SRTT', path_inputfiles = ".\\Data\\SRTT", filepattern="Elisabeth", path_outputfiles = ".\\Data_python", sequence_length = 8, is_estimate_network=True)
    #seq_group1.get_data()
    #seq_group1.save_data()
    # seq_group1 = Group(experiment = 'SEQ', path_inputfiles = ".\\Data_Seq_8", filepattern="Carsten", path_outputfiles = ".\\Data_python", sequence_length = 8, is_estimate_network=True)
    # seq_group1.get_data()
    # seq_group1.save_data()
    # print(f"Gruppe 1")
    # mst_group1 = Group(experiment = 'MST', path_inputfiles = ".\\Data MST", filepattern="Tag1", path_outputfiles = ".\\Data_python", sequence_length = 10)
    # mst_group1.get_data()
    # mst_group1.save_data()
    # print(f"Gruppe 2")
    # mst_group2 = Group(experiment = 'MST', path_inputfiles = ".\\Data MST", filepattern="Tag2", path_outputfiles = ".\\Data_python", sequence_length = 10)
    # mst_group2.get_data()
    # mst_group2.save_data()
    #print(mst_group1.corrsq)

#    statistic, pval = stats.ttest_ind(mst_group1.corrsq, mst_group2.corrsq)
    # statistic, pval = stats.ttest_ind(seq_group1.corrsq, seq_group2.corrsq)
    # print(f"statistic = {statistic}")
    # for i in pval:
    #     print(f"Block[i+1] - pval = {i:.4}")
