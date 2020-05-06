import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from os import listdir, rename
from os.path import isfile, join
from mst import MST
from seq import SEQ
from srtt import SRTT
from group import Group
from scipy import stats 
from myplots import my_violinplot, set_axis_style
from my_statistics import cohend
from statistic_ck import Statistic
import experiments_config #import estimate_Rogens
import logging, json
from experiment import Experiment

logger = logging.getLogger(__name__)

class LearnTable():
    ''' Verwaltung der Table fuer die Doktoranden 
        Idee: wir haben die Tabelle mit den Daten wir suchen die notwendigen Informationen fuer 
                das Experiment heraus. Dann laden wir die Daten ein bzw. berechnen diese 
                und tragen dann die ExperimentErgebnisse wieder in die Tabelle ein

    ''' 
    
    def __init__(self, table_file_name):

        self.table_file_name = table_file_name
        self.outcome_parameters = ['slope', 'slope_to_max', 'best_time','best_seq_pos','sum_cor_seq']
        self.experiment_name_list = ["MST","SEQ","SRTT"]
        self.sequence_length_list = [5,8,10]
        self.df = pd.read_csv(self.table_file_name, sep = '|', engine= "python" )
        self.create_all_columns()
        self.fill_table()
        print(self.df.head())

    def fill_table(self):
        for idx in range(self.df.shape[0]):
        #for idx in range(16,19):# self.df.shape[0]):
            vpn = int(self.df.loc[idx,'VPN'])
            for exp_name in self.experiment_name_list:
                vpn_file_list = self.get_vpn_filenames(exp_name, vpn)
                for file_idx, file in enumerate(vpn_file_list):
                    if exp_name == "MST":
                        subj_class = MST(fullfilename = file, sequence_length = 5)                    
                    if exp_name == 'SEQ':
                        subj_class = SEQ(fullfilename = file, sequence_length = 8)
                    if exp_name == 'SRTT':
                        subj_class = SRTT(fullfilename = file, sequence_length = 10)
   
                        
                    subj_exp = Experiment(subj_class.experiment_name, vpn, subj_class.day, subj_class.sequence_length, is_load=False, df = subj_class.df)
                    subj_exp.save()
                    print(f"in ifll_table")
                    self.add_experiment_to_table(subj_exp, idx)
        
        self.df.to_csv('.\\learn_table_output.csv', index = False, sep = '\t')


    def add_experiment_to_table(self, subj_exp, row_index): 
        experiment_name = subj_exp.experiment_name
        vpn = subj_exp.vpn
        day = subj_exp.day
        sequence_length = subj_exp.sequence_length
        #self.test_that_columns_exist(experiment_name,vpn,day,sequence_length)
        base_name = experiment_name + '_' + str(day) + '_' + str(sequence_length)
        for parameter in self.outcome_parameters:
            col_name = base_name + '_' + parameter
            self.df.loc[row_index,col_name] = self.get_parameter_from_experiment(subj_exp, parameter)

                



    def get_parameter_from_experiment(self, exp, parameter):
        #['slope', 'slope_to_max', 'best_time','best_seq_pos','sum_cor_seq']
        if parameter == 'slope':
            cor_seqtimesum_slope_lpn = exp.cor_seqtimesum_slope_lpn
            #print(cor_seqtimesum_slope_lpn)
            slope = cor_seqtimesum_slope_lpn[0][0]
            return slope
            
        if parameter == 'slope_to_max':
            slope = exp.cor_seqtimesum_to_max_slope_lpn[0][0]
            return slope

        if parameter == 'best_time':
            return min(min(exp.cor_seqtimesum_lplblsn[0]))
        

        if parameter == 'best_seq_pos':
            minimum = 999999999999999
            list2d = exp.cor_seqtimesum_lplblsn[0]
            for i, list1d in enumerate(list2d):
                for j, num in enumerate(list1d):
                    if num and num<minimum:
                        block_min, within_block_min, minimum = i, j, num
            return block_min
            
        if parameter == 'sum_cor_seq':
            return exp.cor_seqsum_lpn[0]
            

        # der speichername im Experiment setzt ich wie folgt zusammen
        # VPN_experiment_name_day_sequence_length
        # z.B. 15_MST_1_5 ... keine Endung da pickle file
        # die files sind im relativen Ordner  dirname = os.path.join(os.path.dirname(__file__),'Experimet_data')
        #with open(os.path.join(dirname,self.filename),'wb') as fp:
        #    pickle.dump(self, fp)
    
    def get_vpn_filenames(self, subdirectory, vpn):
        basepath = os.path.join(".\\Data_Rogens", subdirectory)
        filelist = os.listdir(basepath)
        files = [os.path.join(basepath,file) for file in filelist if file.startswith(str(vpn))]
        return files 

    def create_all_columns(self):
        
        for seq_length, exp in zip(self.sequence_length_list, self.experiment_name_list):
            for day in ['1','2']:
                base_name = exp + '_' + str(day) + '_' + str(seq_length)
                for parameter in self.outcome_parameters:
                    col_name = base_name + '_' + parameter
                    if not col_name in self.df:
                        self.df[col_name] = ''

    def test_that_columns_exist(self, experiment_name,vpn,day,sequence_length):
        base_name = experiment_name + '_' + str(day) + '_' + str(sequence_length)

        for parameter in self.outcome_parameters:
            col_name = base_name + '_' + parameter
            if not col_name in self.df:
                self.df[colname] = ''


        """   outcomeparameter zu Berechnen
        Anstieg insgesamt
        Anstieg zum Maximum
        Maximum
        Gesamtzahl korrekter Sequenzen
        Veraenderung der Outcomeparameter von Tag_1 zu Tag_2
        Fehlerhafte Sequenzen pro Block
        """
        

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

        


        
if __name__ == '__main__':
    filename = "H:\\Unity\\MST_JSAM\\analyse_csvs\\Data_Rogens\\Lernspiel_Auswertung_2020b.csv"
    table = LearnTable(filename)
    print(table.df)
