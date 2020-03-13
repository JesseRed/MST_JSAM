import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from os import listdir, rename
from os.path import isfile, join
from mst import MST
from group import Group
from scipy import stats 
from myplots import my_violinplot, set_axis_style
from my_statistics import cohend
from statistic_ck import Statistic
from group import Group

class Group_analysis():
    ''' Verwaltung von Gruppenanalysen
        im Prinzip handelt es sich nur um eine Liste von Elementen der Klasse Group 
        auf der dann analysen stattfinden 
    '''

    def __init__(self, analysis_path = ".\\Data_python\\analysis"): #group1_path= "./Data MST", group1_filepattern="Tag1", group2_path= "./Data MST", group2_filepattern="Tag2" ):
        self.path = analysis_path
        self.groups = [] # eine Liste von Gruppen fuer die Analyse, in dieser stehen alle Infos

    def add_group(self, experiment = 'MST', path_inputfiles = ".\\Data MST", filepattern="Tag1", path_outputfiles = ".\\Data_python", sequence_length = 10, _id = None, is_estimate_network=False):
        print("adding additional groups for the analysis")
        group = Group(experiment = experiment, path_inputfiles = path_inputfiles, filepattern= filepattern, path_outputfiles = path_outputfiles, sequence_length = sequence_length, _id = _id, is_estimate_network = is_estimate_network)
        group.get_data()
        group.save_data()
        self.groups.append(group)


    def plot(self):
        # https://matplotlib.org/gallery/statistics/violinplot.html#sphx-glr-gallery-statistics-violinplot-py
        print(f"about to make beautiful violin plots")
        #print(self.mst_g1.corrsq) # list of lists of Probanden [correcte SEqenzen pro block] N x Bloecke
        #print(self.mst_g2.corrsq)
        my_violinplot(self.mst_g1.corrsq, self.mst_g2.corrsq)
        my_forestplot(self.mst_g1.corrsq, self.mst_g2.corrsq)
        

        
if __name__ == '__main__':
    
    is_perform_analysis = True
    is_perform_statistic = False

    experiment_name = 'MST'
    experiment_name = 'SRTT'
    analysis = Group_analysis(".\\Data_python\\analysis")
    is_estimate_network = True
    path_inputfiles = ".\\Data MST"
    path_inputfiles = ".\\Data MST_test"
    path_inputfiles = ".\\Data_SRTT_test"
    
    if is_perform_analysis:
        filepattern = "Tag1"
        filepattern = "01_"
        _id = "MST_G1_"
        _id = "SRTT_G1_"
        analysis.add_group(experiment = experiment_name, path_inputfiles = path_inputfiles, filepattern=filepattern, path_outputfiles = ".\\Data_python", sequence_length = 10, _id = _id, is_estimate_network = is_estimate_network)
        filepattern = "Tag2"
        filepattern = "02_"
        _id = "MST_G2_"
        _id = "SRTT_G2_"
        analysis.add_group(experiment = experiment_name, path_inputfiles = path_inputfiles, filepattern=filepattern, path_outputfiles = ".\\Data_python", sequence_length = 10, _id = _id, is_estimate_network = is_estimate_network)

    if is_perform_statistic:
        _ids = ["MST_G1_", "MST_G2_"]
        my_stat = Statistic(experiment = experiment_name, group_list= [], data_path = ".\\Data_python", _ids = _ids)
        my_stat.test_group_differences_ttest('corrsq_slope')
        for key, val in my_stat.data[0][1].items():
            print(key)
        print(my_stat.data[1][0]['phi_real_slope'])
        
        y = my_stat.data[1][0]['phi_real']
        x = list(range(len(y)))
        plt.scatter(x,y)
        plt.show()
#    my_stat = Statistic(experiment = experiment_name, group_list= analysis.groups, data_path = ".\\Data_python", _ids = _ids)
#    analysis.perform_statistics()

    

    