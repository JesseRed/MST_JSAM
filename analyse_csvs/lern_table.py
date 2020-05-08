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
import statistics

logger = logging.getLogger(__name__)

class LearnTable():
    ''' Verwaltung der Table fuer die Doktoranden 
        Idee: wir haben die Tabelle mit den Daten wir suchen die notwendigen Informationen fuer 
                das Experiment heraus. Dann laden wir die Daten ein bzw. berechnen diese 
                und tragen dann die ExperimentErgebnisse wieder in die Tabelle ein

    ''' 
    
    def __init__(self, table_file_name):

        self.table_file_name = table_file_name
        self.outcome_parameters = ['slope', 'slope_to_max', 'best_time','best_seq_pos','sum_cor_seq',
            'q_real','q_fake_list', 'q_fake_list_mean', 'q_fake_list_std','phi_real', 'phi_real_slope', 'q_real_t', 'q_real_p']

        self.experiment_name_list = ["MST","SEQ","SRTT"]
        self.sequence_length_list = [5,8,10]
        self.df = pd.read_csv(self.table_file_name, sep = '|', engine= "python" )
        self.create_all_columns()
        self.fill_table()
        print(self.df.head())

    def fill_table(self):
        for idx in range(self.df.shape[0]):
            vpn = int(self.df.loc[idx,'VPN'])
            print(f"engaging table row number: {idx} with VPN = {vpn}")
        #for idx in range(16,19):# self.df.shape[0]):
            for exp_name in self.experiment_name_list:
                try:
                    vpn_file_list = self.get_vpn_filenames(exp_name, vpn)
                except:
                    print(f"error in get_vpn_filenames {self.df.loc[idx,'Klarname']} in row {idx} ")
                for file_idx, file in enumerate(vpn_file_list):
                    print(f"estimating {exp_name} for subject {self.df.loc[idx,'Klarname']}")
                    if exp_name == "MST":
                        try:
                            subj_class = MST(fullfilename = file, sequence_length = 5)                    
                        except:
                            print(f"error in MST preparation of Subject {self.df.loc[idx,'Klarname']} in row {idx} ")
                    if exp_name == 'SEQ':
                        try:
                            subj_class = SEQ(fullfilename = file, sequence_length = 8)
                        except:
                            print(f"error in MST preparation of Subject {self.df.loc[idx,'Klarname']} in row {idx} ")
                    if exp_name == 'SRTT':
                        try:
                            subj_class = SRTT(fullfilename = file, sequence_length = 10)
                        except:
                            print(f"error in MST preparation of Subject {self.df.loc[idx,'Klarname']} in row {idx} ")
                    
                    try:                        
                        subj_exp = Experiment(subj_class.experiment_name, vpn, subj_class.day, subj_class.sequence_length, is_load=False, df = subj_class.df)
                    except:
                        print(f"error in experiment estimation {self.df.loc[idx,'Klarname']} in row {idx} and experiment {exp_name}")
#                    try:
                    subj_exp.add_network_class(coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= False, is_estimate_Q= True, num_random_Q=10)
#                    except Exception as error:    
#                        print(f"error in network estimation {self.df.loc[idx,'Klarname']} in row {idx} and experiment {exp_name} filename = {file}")
#                        print(f"error = {repr(error)}")
                    try:
                        subj_exp.save()
                    except:
                        print(f"error in experiment saving {self.df.loc[idx,'Klarname']} in row {idx} and experiment {exp_name}")
                    try:
                        self.add_experiment_to_table(subj_exp, idx)
                    except:
                        print(f"subject {self.df.loc[idx,'Klarname']} in row {idx} and experiment {exp_name} could not be written correctly ")

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
            try:
                cor_seqtimesum_slope_lpn = exp.cor_seqtimesum_slope_lpn
                #print(cor_seqtimesum_slope_lpn)
                slope = cor_seqtimesum_slope_lpn[0][0]
            except:
                print(f"error in get_parameter_from_experiment with cor_seqtime_sum_slope_lpn = {exp.cor_seqtimesum_slope_lpn}")
                #raise ValueError("bad value of cor_seqtimesum_slope_lpn")
                raise ValueError("slope value error")
            return slope
            
        if parameter == 'slope_to_max':
            try:
                slope = exp.cor_seqtimesum_to_max_slope_lpn[0][0]
            except:
                print(f"error in get_parameter_from_experiment with exp.cor_seqtimesum_to_max_slope_lpn = {exp.cor_seqtimesum_to_max_slope_lpn}")
                #raise ValueError("bad value of cor_seqtimesum_slope_lpn")
                raise ValueError("slope_to_max value error")
            return slope

        if parameter == 'best_time':
            try:
                best_time = min(min(exp.cor_seqtimesum_lplblsn[0]))
            except:
                print(f"error in get_parameter_from_experiment with exp.cor_seqtimesum_lplblsn = {exp.cor_seqtimesum_lplblsn}")
                raise ValueError("best_time value error")
            return best_time
        

        if parameter == 'best_seq_pos':
            try:
                minimum = 999999999999999
                list2d = exp.cor_seqtimesum_lplblsn[0]
                for i, list1d in enumerate(list2d):
                    for j, num in enumerate(list1d):
                        if num and num<minimum:
                            block_min, within_block_min, minimum = i, j, num
            except:
                print(f"error in get_parameter_from_experiment with best_seq_pos and exp.cor_seqtimesum_lplblsn = {exp.cor_seqtimesum_lplblsn}")
                raise ValueError("best_seq_pos value error")

            return block_min
            
        if parameter == 'sum_cor_seq':
            try:
                sum_cor_seq = exp.cor_seqsum_lpn[0]
            except:
                print(f"error in get_parameter_from_experiment with sum_cor_seq and exp.cor_seqsum_lpn = {exp.cor_seqsum_lpn}")
                raise ValueError("sum_cor_seq value error")
            return sum_cor_seq
            

        if parameter == 'q_real':
            try:
                q_real = exp.net.q_real
            except:
                print(f"error in get_parameter_from_experiment with q_real ")
                raise ValueError("q_real value error")
            return q_real
                
        if parameter == 'phi_real':
            phi_real = str(exp.net.phi_real)
            return phi_real
        
        if parameter == 'q_fake_list':
            return str(exp.net.q_fake_list)
        

        if parameter == 'q_fake_list_mean':
            return  sum(exp.net.q_fake_list)/len(exp.net.q_fake_list)
        
        if parameter == 'q_fake_list_std':
            return  statistics.stdev(exp.net.q_fake_list)
        
        if parameter == 'phi_real_slope':
            x = np.arange(len(exp.net.phi_real)-1)
            y = exp.net.phi_real[1:]
            phi_real_slope,b = np.polyfit(x, y, 1)
            return phi_real_slope
        
        if parameter == 'q_real_t':
            return exp.net.q_real_t

        if parameter == 'q_real_p':
            return exp.net.q_real_p

        
        
        
          #'phi_real':             self.phi_real,
    #             'phi_real_slope':       phi_real_slope,
    #             'q_real':               self.q_real,
    #             'g_real':               tolist_ck(self.g_real),
    #         self.q_real_t, 
    # self.q_real_p 
    # self.q_fake_list
    # self.q_real)
    #      'q_fake_list_mean': 
    #     sum(self.q_fake_list)/len(self.q_fake_list),
    # 
        # phi_fake_list_arr = np.asarray(self.phi_fake_list)
        # phi_fake_list_mean = np.nanmean(phi_fake_list_arr,axis=0)
        # phi_fake_list_std = np.nanstd(phi_fake_list_arr,axis=0)
        # x = np.arange(len(self.phi_real)-1)
        # y = self.phi_real[1:]
        # phi_real_slope,b = np.polyfit(x, y, 1)
        # filename = 'net_results_x2.json'# + self.filename
        # results = {
        #     'input_file':           '04_2_SRTT_2020-02-06_12-17-15.txt',
        #     'ipi':                  self.ipi.tolist(),
        #     'date_of_analysis':     datetime.today().strftime('%Y-%m-%d'),
        #     '':             self.phi_real,
        #     'phi_real_slope':       phi_real_slope,
        #     'q_real':               self.q_real,
        #     'q_real_t':             self.q_real_t,
        #     'q_real_p':             self.q_real_p,
        #     'q_fake_list':          self.q_fake_list,
        #     'q_fake_list_mean':     sum(self.q_fake_list)/len(self.q_fake_list),
        #     'g_real':               self.tolist_ck(self.g_real),
        #     'g_fake_list':          self.tolist_ck(self.g_fake_list), # arrays verschachtelt in einer Liste
        #     'A':                    self.A.tolist()
        # }


        # der speichername im Experiment setzt ich wie folgt zusammen
        # VPN_experiment_name_day_sequence_length
        # z.B. 15_MST_1_5 ... keine Endung da pickle file
        # die files sind im relativen Ordner  dirname = os.path.join(os.path.dirname(__file__),'Experimet_data')
        #with open(os.path.join(dirname,self.filename),'wb') as fp:
        #    pickle.dump(self, fp)
    
    def get_vpn_filenames(self, subdirectory, vpn):
        basepath = os.path.join(".\\Data_Rogens", subdirectory)
        filelist = os.listdir(basepath)
        files = [os.path.join(basepath,file) for file in filelist if file.split('_')[0]==str(vpn)]
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
