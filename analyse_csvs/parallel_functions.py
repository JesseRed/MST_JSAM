from mst import MST
from seq import SEQ
from srtt import SRTT
from experiment import Experiment
import os
import time
import pandas as pd
import numpy as np
import statistics

outcome_parameters = ['slope', 'slope_to_max', 'best_time','best_seq_pos','sum_cor_seq',
            'q_real','q_fake_list', 'q_fake_list_mean', 'q_fake_list_std','phi_real',
            'phi_real_slope', 'q_real_t', 'q_real_p']

def estimate_and_fill_one_row_in_learn_table(args_dict):
    idx = args_dict['idx']
    df  = args_dict['df']
    experiment_name_list = args_dict['experiment_name_list']
    vpn = args_dict['vpn']

    status_string = "all ok"
    #for idx in range(16,19):# self.df.shape[0]):
    for exp_name in experiment_name_list:
        try:
            vpn_file_list = get_vpn_filenames(exp_name, vpn)
        except:
            status_string = (f"error in get_vpn_filenames {df.loc[idx,'Klarname']} in row {idx} ")
            print(status_string)

        for file_idx, file in enumerate(vpn_file_list):
            print(f"estimating {exp_name} for subject {df.loc[idx,'Klarname']}")
            if exp_name == "MST":
                try:
                    subj_class = MST(fullfilename = file, sequence_length = 5)                    
                except:
                    status_string = (f"error in MST preparation of Subject {df.loc[idx,'Klarname']} in row {idx} ")
                    print(status_string)
            if exp_name == 'SEQ':
                try:
                    subj_class = SEQ(fullfilename = file, sequence_length = 8)
                except:
                    status_string = (f"error in MST preparation of Subject {df.loc[idx,'Klarname']} in row {idx} ")
                    print(status_string)
            if exp_name == 'SRTT':
                try:
                    subj_class = SRTT(fullfilename = file, sequence_length = 10)
                except:
                    status_string = (f"error in MST preparation of Subject {df.loc[idx,'Klarname']} in row {idx} ")
                    print(status_string)
            try:                        
                subj_exp = Experiment(subj_class.experiment_name, vpn, subj_class.day, subj_class.sequence_length, is_load=False, df = subj_class.df)
            except:
                status_string = (f"error in experiment estimation {df.loc[idx,'Klarname']} in row {idx} and experiment {exp_name}")
                print(status_string)
#                    try:
            subj_exp.add_network_class(coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= False, is_estimate_Q= True, num_random_Q=10)
#                    except Exception as error:    
#                        print(f"error in network estimation {self.df.loc[idx,'Klarname']} in row {idx} and experiment {exp_name} filename = {file}")
#                        print(f"error = {repr(error)}")
            try:
                subj_exp.save()
            except:
                status_string = (f"error in experiment saving {df.loc[idx,'Klarname']} in row {idx} and experiment {exp_name}")
                print(status_string)

            is_not_saved = True
            save_counter = 0
            while is_not_saved:
                try:
                    cur_df = pd.read_csv('.\\learn_table_output.csv', sep = '\t', engine= "python" )
                    cur_df = add_experiment_to_table(subj_exp, idx, cur_df)
                    cur_df.to_csv('.\\learn_table_output.csv', index = False, sep = '\t')
                    is_not_saved = False
                except Exception as error:
                    print('problem with saving ... try again')
                    print(error)
                    time.sleep(2)
                    save_counter += 1
                    if save_counter >10:
                        is_not_saved = False
                        status_string = (f"failed to save the csv file")

    return status_string       
        # try:
        #         add_experiment_to_table(subj_exp, idx)
        #     except:
        #         print(f"subject {df.loc[idx,'Klarname']} in row {idx} and experiment {exp_name} could not be written correctly ")
        # try:
        #     df.to_csv('.\\learn_table_output.csv', index = False, sep = '\t')
        # except:
        #     save_file_name = '.\\learn_table_output' + str(vpn) + '.csv'
        #     df.to_csv('.\\learn_table_output.csv', index = False, sep = '\t')


def get_vpn_filenames(subdirectory, vpn):
    basepath = os.path.join(".\\Data_Rogens", subdirectory)
    filelist = os.listdir(basepath)
    files = [os.path.join(basepath,file) for file in filelist if file.split('_')[0]==str(vpn)]
    return files 


def add_experiment_to_table(subj_exp, row_index, df): 
    experiment_name = subj_exp.experiment_name
    vpn = subj_exp.vpn
    day = subj_exp.day
    sequence_length = subj_exp.sequence_length
    #self.test_that_columns_exist(experiment_name,vpn,day,sequence_length)
    base_name = experiment_name + '_' + str(day) + '_' + str(sequence_length)
    for parameter in outcome_parameters:
        col_name = base_name + '_' + parameter
        print(f"add to table {row_index}, {col_name}")
        df.loc[row_index,col_name] = get_parameter_from_experiment(subj_exp, parameter)
    return df


def get_parameter_from_experiment(exp, parameter):
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
