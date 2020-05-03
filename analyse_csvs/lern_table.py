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
import experiments_config #import estimate_Rogens
import logging, json
logger = logging.getLogger(__name__)

class LearnTable():
    ''' Verwaltung der Table fuer die Doktoranden 
    '''

    def __init__(self, table_file_name):
        self.table_file_name = table_file_name
        self.df = pd.read_csv(self.table_file_name, sep = '|', engine= "python" )
        self.mst_colnamelist = ['abs_corr_seq', 'corrsq', 'corrsq_slope', 'corrsq_slope_to_max',
            'corrsq_slope_1_10', 'errors_per_block', 'abs_errors', 'abs_corr_seq', 'pos_of_first_best_block',
            'pos_of_last_best_block','sequence_length','q_real','phi_real','phi_real_slope',
            'q_fake_list', 'q_fake_list_mean', 'q_real_p', 'q_real_t']
        self.seq_colnamelist = ['abs_corr_seq', 'corrsq', 'corrsq_slope', 'corrsq_slope_to_max',
            'corrsq_slope_1_10', 'errors_per_block', 'abs_errors', 'abs_corr_seq', 'pos_of_first_best_block',
            'pos_of_last_best_block','sequence_length','q_real','phi_real','phi_real_slope',
            'q_fake_list', 'q_fake_list_mean', 'q_real_p', 'q_real_t']
        self.srtt_colnamelist = ['abs_corr_seq', 'corrsq', 'corrsq_slope', 'corrsq_slope_to_max',
            'corrsq_slope_1_10', 'errors_per_block', 'abs_errors', 'abs_corr_seq', 'pos_of_first_best_block',
            'pos_of_last_best_block','sequence_length','q_real','phi_real','phi_real_slope',
            'q_fake_list', 'q_fake_list_mean', 'q_real_p', 'q_real_t']

    def add_to_table(self, dic): 
        # es wird ein Dictionary uebergeben von dem Lernparadigma
        # mit den enthaltenen Infos wird die Tabelle gefuellt
        # es muss allerdings zwingend vorher alles ausgerechnet worden sein
        #print(self.df.head(50))
        for subgroup in dic["_ids"]:
            print(dic["path_outputfiles"])
            files = [file for file in os.listdir(dic["path_outputfiles"]) if subgroup in file]
            for filename in files:
                with open(os.path.join(dic["path_outputfiles"],filename), "r") as fp:   
                    result_dict = json.load(fp)
                experiment, group, row_num = self.get_row_number_of_subject_from_file(filename, dic)
                self.add_results_to_table(result_dict, row_num)
                return
                # if dic["experiment_name"] == 'MST':
                #     self.add_MST_result_file(result_dict)


    def add_results_to_table(self, results_dic, row_num, experiment, filename):
        if results_dic["experiment"]=="MST":
            if not experiment=="MST":
                print(f"experiment name does not match filedescription of {filename}")
                raise Exception("experiment name does not match filedescription of {filename}")
            self.add_MST_results_to_table(results_dic, row_num)


    def add_MST_results_to_table(self, result_dic, row_num):
        df = self.df

        df.loc[row_num,'MST_abs_corr_seq'] = result_dic["abs_corr_seq"]
        df.loc[row_num,'MST_q_real_t'] = 4
        pd.set_option('display.max_columns', 50)
        print(df.head(15))

    def get_row_number_of_subject_from_file(self, filename, dic):
        #if dic["experiment_name"]=="MST":
        # alle filename must have the structure of ExperimentName_Gruppe_VPN_Nachname_Vorname...
        tmp = filename.split('_')
        experiment = tmp[0]
        group = tmp[1]
        vpn = int(tmp[2])
        rownum = self.df.loc[self.df['VPN']==vpn].iloc[0,0]
        return (experiment, group, rownum)

        



    def add_experimental_columns_to_table(self, dic):


        if dic["experiment_name"]=="MST":
            colnamelist = self.mst_colnamelist
        if dic["experiment_name"]=="SEQ":
            colnamelist = self.seq_colnamelist
        if dic["experiment_name"]=="SRTT":
            colnamelist = self.srtt_colnamelist

        df = self.df
        for _id in dic["_ids"]:
            for colname in colnamelist:
                colnameid = _id + '_' + colname
                if not colnameid in df:
                    df = df.insert(df.shape[1],colnameid,[0]*df.shape[0])

            #         df = df.assign(MST_G1_abs_corr_seq = [0] * df.shape[0])
            # df = df.assign(MST_G1_corrsq = [0] * df.shape[0])
            # df = df.assign(MST_G1_corrsq_slope = [0] * df.shape[0])
            # df = df.assign(MST_G1_corrsq_slope_to_max = [0] * df.shape[0])
            # df = df.assign(MST_G1_corrsq_slope_1_10 = [0] * df.shape[0])
            # df = df.assign(MST_G1_errors_per_block = [0] * df.shape[0])
            # df = df.assign(MST_G1_abs_errors = [0] * df.shape[0])
            # df = df.assign(MST_G1_abs_corr_seq = [0] * df.shape[0])
            # df = df.assign(MST_G1_pos_of_first_best_block = [0] * df.shape[0])
            # df = df.assign(MST_G1_pos_of_last_best_block = [0] * df.shape[0])
            # df = df.assign(MST_G1_sequence_length = [0] * df.shape[0])
            # df = df.assign(MST_G1_q_real = [0] * df.shape[0])
            # df = df.assign(MST_G1_phi_real = [0] * df.shape[0])
            # df = df.assign(MST_G1_phi_real_slope = [0] * df.shape[0])
            # df = df.assign(MST_G1_q_fake_list = [0] * df.shape[0])
            # df = df.assign(MST_G1_q_fake_list_mean = [0] * df.shape[0])
            # df = df.assign(MST_G1_q_real_p = [0] * df.shape[0])
            # df = df.assign(MST_G1_q_real_t = [0] * df.shape[0])
        self.df = df
        #print(df.head)

# abs_corr_seq = [0] * self.df.shape[0])
#             df = df.assign(MST_corrsq = [0] * self.df.shape[0])
#             df = df.assign(MST_corrsq_slope = [0] * self.df.shape[0])
#             df = df.assign(MST_corrsq_slope_to_max = [0] * self.df.shape[0])
#             df = df.assign(MST_corrsq_slope_1_10 = [0] * self.df.shape[0])
#             df = df.assign(MST_errors_per_block = [0] * self.df.shape[0])
#             df = df.assign(MST_abs_errors = [0] * self.df.shape[0])
#             df = df.assign(MST_abs_corr_seq = [0] * self.df.shape[0])
#             df = df.assign(MST_pos_of_first_best_block = [0] * self.df.shape[0])
#             df = df.assign(MST_pos_of_last_best_block = [0] * self.df.shape[0])
#             df = df.assign(MST_sequence_length = [0] * self.df.shape[0])
#             df = df.assign(MST_q_real = [0] * self.df.shape[0])
#             df = df.assign(MST_phi_real = [0] * self.df.shape[0])
#             df = df.assign(MST_phi_real_slope = [0] * self.df.shape[0])
#             df = df.assign(MST_q_fake_list = [0] * self.df.shape[0])
#             df = df.assign(MST_q_fake_list_mean = [0] * self.df.shape[0])
#             df = df.assign(MST_q_real_p = [0] * self.df.shape[0])
#             df = df.assign(MST_q_real_t 


        # mydict = {
        #         'experiment' :              'MST',
        #         'ipi' :                     tolist_ck(self.ipi),
        #         'hits':                     tolist_ck(self.hits),
        #         'ipi_cor' :                 tolist_ck(self.ipi_cor),
        #         'sequence_length' :         self.sequence_length,
        #         'corrsq' :                  tolist_ck(self.corrsq),
        #         'corrsq_slope' :            tolist_ck(self.corrsq_slope),
        #         'corrsq_slope_to_max' :     tolist_ck(self.corrsq_slope_to_max), # regressionsgerade nur bis zum Maximum berechnet
        #         'corrsq_slope_1_10' :       tolist_ck(self.corrsq_slope_1_10), # regressionsgerade nur 1-10
        #         'errors_per_block'      :   tolist_ck(self.errors_per_block),
        #         'abs_errors'            :   sum(tolist_ck(self.errors_per_block)),
        #         'abs_corr_seq' :            sum(tolist_ck(self.corrsq)),
        #         'pos_of_first_best_block' : corrsq.index(max(corrsq)),
        #         'pos_of_last_best_block' :  abs((reverse_corrsq.index(max(corrsq)))-12),
        #         'abs_corr_sequence'     :   sum(tolist_ck(self.corrsq))
        #     }
        # dicMST = {
        #     "is_perform_analysis"       :   True,
        #     "is_estimate_network"       :   False,
        #     "is_perform_statistic"      :   False,
        #     "is_sim"                    :   False,
        #     "is_estimate_Q"             :   True,
        #     "is_test_Q_against_random"  :   True,
        #     "num_random_Q"              :   10,
        #     "is_clustering"             :   False,
        #     "num_random_Q"              :   10,
        #     "coupling_parameter"        :   0.3,
        #     "resolution_parameter"      :   0.9,
        #     "experiment_name"           :   "MST",
        #     "path_inputfiles"           :   ".\\Data_Rogens\\MST",
        #     "filepattern"               :   ["REST1", "REST2"],
        #     "_ids"                      :   ["MST_G1_", "MST_G2"],
        #     "sequence_length"           :   10,
        #     "path_outputfiles"          :   ".\\Data_Rogens\\Results",
        #     "is_multiprocessing"        :   False,
        #     "show_images"               :   False,
        #     "target_color"              :   0,
        #     "table"                     :   ".\\Data_Rogens\\Lernspiel_Auswertung_2020b.csv",
        # }
        
if __name__ == '__main__':
    table = LernTable("")
