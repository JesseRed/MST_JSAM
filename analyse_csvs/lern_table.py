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
#import experiments_config #import estimate_Rogens
import logging, json
from experiment import Experiment
import statistics
#import parallel_functions 
import multiprocessing as mp
import pickle

logger = logging.getLogger(__name__)


class LearnTable():
    ''' Verwaltung der Table fuer die Doktoranden 
        Idee: wir haben die Tabelle mit den Daten wir suchen die notwendigen Informationen fuer 
                das Experiment heraus. Dann laden wir die Daten ein bzw. berechnen diese 
                und tragen dann die ExperimentErgebnisse wieder in die Tabelle ein

    ''' 
    
    def __init__(self, table_file_name, sep = '|'):
 
        self.table_file_name = table_file_name
        # self.outcome_parameters = ['slope', 'slope_to_max', 'best_time','best_seq_pos','sum_cor_seq',
        #                             'q_real','q_fake_list', 'q_fake_list_mean', 'q_fake_list_std','phi_real', 'phi_real_slope', 'q_real_t', 'q_real_p']
        # wenn an dem Parameter das Wort "PROBLOCK" steht dann sollen die Werte fuer jeden Block getrennt ausgegeben werden 
        self.outcome_parameters = ['slope', 'slope_to_max', 'best_time','best_seq_pos','sum_cor_seq']
        self.outcome_parameters_PROBLOCK = ['all_seqsum_lplbn', 'cor_seqsum_lplbn', 'err_seqsum_lplbn'] #, 'all_ipi_lblsln', 'cor_ipi_lblsln', 'err_ipi_lblsln']
        # self.experiment_name_list = experiment_name_list  # ["MST", "SEQ", "SRTT"]
        
        self.sep = sep
        self.table_file_name_output = os.path.splitext(self.table_file_name)[0] + "_output.csv"
        self.df = pd.read_csv(self.table_file_name, sep = self.sep, encoding='latin1' )
        
    def add_estimated_results_to_learn_table(self,
                                             results_directory = ".//Results3//Estimated_results",
                                             experiment_name_list = ["MST_1", "MST_2", "SEQ_1", "SEQ_2", "SRTT_1", "SRTT_2"]
                                            ):
        print(f"starting add_estimated_results_to_learn_table with parameter: ")
        print(f"results_directory = {results_directory}")
        print(f"experiment_name_list = {experiment_name_list}")
        self.results_directory = results_directory
        self.experiment_name_list = experiment_name_list

        self.create_all_columns()
        # get the filelist
        filelist =  [file for file in os.listdir(results_directory) if (any(list_elem in file for list_elem in self.experiment_name_list ))]
        # itereate through the table        
        for row_index in range(self.df.shape[0]):
            vpn = int(self.df.loc[row_index,'VPN'])
            print(f"engaging table row number: {row_index} with VPN = {vpn}")

            subj_file_list = [f for f in filelist if (f.partition("_")[0]==(str(vpn)))]
            print(f"vpn = {str(vpn)} ... files: {subj_file_list}")
            for subj_file in subj_file_list:
                # lade das experiment
                with open(os.path.join(self.results_directory, subj_file),'rb') as fp:
                    subj_exp = pickle.load(fp)
                # das column prefix ergibt sich aus der experiment_name_list die aufschluesselt
                # ob z.B. bestimmte unterschiedliche Paradigmen dennoch in einer Spalte zusammengefasst werden sollen
                column_prefixes = [prefix for prefix in self.experiment_name_list if (prefix in subj_file)]
                if not(len(column_prefixes)==1):
                    print(f"problem with naming convention ... experiment_name_list not unambiguous {self.experiment_name_list} vs. {subj_file} ({column_prefixes})")
                else:
                    column_prefix = column_prefixes[0]
                self.add_experiment_to_table(subj_exp, row_index, column_prefix)
        self.df.to_csv(self.table_file_name_output, index = False, sep = self.sep, encoding='latin1')
        
        #self.fill_table_from_result_files()


    def create_all_columns(self):
        pass
        # for seq_length, exp in zip(self.sequence_length_list, self.experiment_name_list):
        #     for day in ['1','2']:
        #         base_name = exp + '_' + str(day) + '_' + str(seq_length)
        #         for parameter in self.outcome_parameters:
        #             col_name = base_name + '_' + parameter
        #             if not col_name in self.df:
        #                 self.df[col_name] = ''


    def add_experiment_to_table(self, subj_exp, row_index, column_prefix): 
        # experiment_name = subj_exp.experiment_name
        # vpn = subj_exp.vpn
        # day = subj_exp.day
        # sequence_length = subj_exp.sequence_length
        # #self.test_that_columns_exist(experiment_name,vpn,day,sequence_length)
        # base_name = experiment_name + '_' + str(day) + '_' + str(sequence_length)
        base_name = column_prefix
        for parameter in self.outcome_parameters:
            col_name = base_name + '_' + parameter
            self.df.loc[row_index,col_name] = self.get_parameter_from_experiment(subj_exp, parameter)

        for parameter in self.outcome_parameters_PROBLOCK:
            # parameter muessen echte Parameter des experiment files sein
            #self.outcome_parameters_PROBLOCK = ['all_seqsum_lplbn', 'cor_seqsum_lplbn', 'err_seqsum_lplbn', ]
            att = getattr(subj_exp, parameter)
            if '_lplbn' in parameter:
                num_paradigmen = len(att)
                for paradigm_idx in range(num_paradigmen):
                    number_of_blocks = len(att[paradigm_idx])
                    for block_idx in range(number_of_blocks):
                        col_name = base_name + '_' + parameter + '_Paradigma' + str(paradigm_idx+1) + '_Block' + str(block_idx+1)
                        self.df.loc[row_index, col_name] = att[paradigm_idx][block_idx]
            if 'ipi_lblsln' in parameter:
                print('in')
                number_of_blocks = len(att)
                for block_idx in range(number_of_blocks):
                    col_name = base_name + '_' + parameter[0:3] + "Tastendruecke" + '_Block' + str(block_idx+1)
                    druecker_pro_block = 0
                    for num_seq in range(len(att[block_idx])):
                        druecker_pro_block += len(att[block_idx][num_seq])
#                        for num_n in range(len(att[block_idx][num_seq])):
#                            druecker_pro_block += 1
                    self.df.loc[row_index, col_name] = druecker_pro_block
                    print(f"druecker pro block = {druecker_pro_block}")


                



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


    def fill_table_from_result_files(self):
        results = []
        arg_list = []
        for idx in range(self.df.shape[0]):
            vpn = int(self.df.loc[idx,'VPN'])
            print(f"engaging table row number: {idx} with VPN = {vpn}")
            
            mydict = {'idx': idx, 'df': self.df, 'experiment_name_list': self.experiment_name_list, 'vpn': vpn}
            arg_list.append(mydict)

        pool = mp.Pool(10) #mp.cpu_count())

        results = pool.map(parallel_functions.estimate_and_fill_one_row_in_learn_table, [args for args in arg_list])
        print(results)

    def fill_table(self):
        results = []
        arg_list = []
        for idx in range(self.df.shape[0]):
            vpn = int(self.df.loc[idx,'VPN'])
            print(f"engaging table row number: {idx} with VPN = {vpn}")
            
            mydict = {'idx': idx, 'df': self.df, 'experiment_name_list': self.experiment_name_list, 'vpn': vpn}
            arg_list.append(mydict)

        pool = mp.Pool(10) #mp.cpu_count())

        results = pool.map(parallel_functions.estimate_and_fill_one_row_in_learn_table, [args for args in arg_list])
        print(results)



        
if __name__ == '__main__':
    filename = "H:\\Unity\\MST_JSAM\\analyse_csvs\\Data_Rogens\\Lernspiel_Auswertung_2020b.csv"
    filename = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\Lernspiel_Auswertung_2020b.csv"
    table = LearnTable(filename)
    table.add_estimated_results_to_learn_table()
    print(table.df)
