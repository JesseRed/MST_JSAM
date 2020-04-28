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
    is_estimate_network = False
    is_perform_statistic = False

    experiment_name = 'MST'
#    experiment_name = 'SRTT'
    #experiment_name = 'ASTEROID'


    if experiment_name ==  'MST':
        path_inputfiles = ".\\Data_Rogens\\MST"
        filepattern1 = "REST1"
        filepattern2 = "REST2"
        _ids = ["MST_G1_", "MST_G2"]
        analysis = Group_analysis(".\\Results\\Rogens")
    

    

    if is_perform_analysis:
        analysis.add_group(experiment = experiment_name, path_inputfiles = path_inputfiles, filepattern=filepattern1, path_outputfiles = ".\\Results\\Rogens", sequence_length = 10, _id = _ids[0], is_estimate_network = is_estimate_network)
        analysis.add_group(experiment = experiment_name, path_inputfiles = path_inputfiles, filepattern=filepattern2, path_outputfiles = ".\\Results\\Rogens", sequence_length = 10, _id = _ids[1], is_estimate_network = is_estimate_network)
    
    my_stat = Statistic(experiment=experiment_name, group_list=analysis.groups, data_path=".\\Results\\Rogens", _ids=_ids)
    keys = ["corrsq_slope", "abs_corr_seq", "pos_of_first_best_block", "pos_of_last_best_block"]
    for key in keys:
        my_stat.test_group_differences_ttest(key = key, is_independent = False)
        my_stat.show_group_differences(key)
    
    my_stat.plot_one_group_sequence("corrsq")
    
#     if experiment_name == 'SRTT':
#         path_inputfiles = ".\\Data_SRTT_test"
#         filepattern = "01_"
#         _id = "SRTT_G1_"
#         analysis = Group_analysis(".\\Data_python\\analysis")
        
#     if experiment_name == 'ASTEROID':
#         path_inputfiles = ".\\Data_Asteroid"
#         filepattern = "Asteroid1_"
#         _id = "ASTEROID_G1_"
#         analysis = Group_analysis(".\\Data_python\\analysis")
        

    
#     if is_perform_analysis:
#         analysis.add_group(experiment = experiment_name, path_inputfiles = path_inputfiles, filepattern=filepattern, path_outputfiles = ".\\Data_python", sequence_length = 10, _id = _id, is_estimate_network = is_estimate_network)


#     if experiment_name ==  'MST':
#         path_inputfiles = ".\\Data MST"
#         path_inputfiles = ".\\Data MST_test"
#         filepattern = "Tag2"
#         _id = "MST_G2_"
#         analysis = Group_analysis(".\\Data_python\\analysis")
    
#     if experiment_name == 'SRTT':
#         path_inputfiles = ".\\Data_SRTT_test"
#         filepattern = "02_"
#         _id = "SRTT_G2_"
#         analysis = Group_analysis(".\\Data_python\\analysis")


#     if experiment_name == 'ASTEROID':
#         path_inputfiles = ".\\Data_Asteroid"
#         filepattern = "Asteroid2_"
#         _id = "ASTEROID_G2_"
#         analysis = Group_analysis(".\\Data_python\\analysis")
        

#     if is_perform_analysis:
#         analysis.add_group(experiment = experiment_name, path_inputfiles = path_inputfiles, filepattern=filepattern, path_outputfiles = ".\\Data_python", sequence_length = 10, _id = _id, is_estimate_network = is_estimate_network)


#     if is_perform_statistic:
#         if experiment_name == 'MST':
#             _ids = ["MST_G1_", "MST_G2_"]
#         if experiment_name == 'SRTT':
#             _ids = ["SRTT_G1_", "SRTT_G2_"]
#         if experiment_name == 'ASTEROID':
#             _ids = ["ASTEROID_G1_", "ASTEROID_G2_"]

#         my_stat = Statistic(experiment=experiment_name, group_list=[], data_path=".\\Data_python", _ids=_ids)
#         #my_stat.test_group_differences_ttest('corrsq_slope')
#         my_stat.test_group_differences_ttest('success_per_block')
#         my_stat.test_group_differences_ttest('abs_success')
#         for key, val in my_stat.data[0][1].items():
#             print(key)
#         print(my_stat.data[1][0]['phi_real_slope'])
        
#         y = my_stat.data[1][0]['phi_real']
#         x = list(range(len(y)))
#         plt.scatter(x,y)
#         plt.show()
# #    my_stat = Statistic(experiment = experiment_name, group_list= analysis.groups, data_path = ".\\Data_python", _ids = _ids)
# #    analysis.perform_statistics()

    

#!  Jenaer Planungsgespraeche 28.04.2020
""" ------------------------------------
    outcomeparameter zu Berechnen
        Anstieg insgesamt
        Anstieg zum Maximum
        Maximum
        Gesamtzahl korrekter Sequenzen
        Veraenderung der Outcomeparameter von Tag_1 zu Tag_2
        Fehlerhafte Sequenzen pro Block

    Ziele:
        - Wie gut kann ich Lernerfolg mit unterschiedlichen Lernspielen testen
        - Wie valide sind die verschiedenen Lernspiele fuer diese Frage
        - Wie kann ich Lerntypen unterscheiden, was sind Einflussfaktoren

        Teilung der Gruppe anhand der Outcomeparameter in 2 Gruppen im median und Untersuchung 
            welche Unterschiede diese Gruppen aufweisen


        std der Lernspiele fuer verschiende outcomeparameter an Tag1, Tag2 und Tag2-Tag1
        

        Indentifikation verschiedener LErntypen

            Multiple Regressionsanalyse verschiedener Einflussfaktoren auf die outcomeparameter
            1... alles aus neuropsych 
            2... chunking
            3... Alter, Geschlecht
            4... Fehlerquote


    ich bekomme eine Tabelle mit den klinischen Daten der Probanden
    dann trage ich dort ein:
    1. Outcomeparamter 
    2. die erfolgreichen Sequenzen pro Block
    3. chunking ... Mass Q

    die Tabelle dient zur Visualisierung und Nachauswertung durch die Probanden


    """