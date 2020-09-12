import os, json, sys
import numpy as np
import pandas as pd
from numpy.random import randn
from numpy.random import seed
from numpy import mean
from numpy import var
from math import sqrt
import pickle
from scipy import stats 
from scipy.stats import ttest_1samp, ttest_ind, ttest_rel
import statistics
import matplotlib.pyplot as plt
import logging, socket
import statsmodels.api as sm
from scipy.stats import mannwhitneyu
from statsmodels.sandbox.regression.predstd import wls_prediction_std

# class Stat_Group():
#################################################
# Logging configuration
#################################################
computername = socket.gethostname()
if computername == "BigBang":
    mstfile = "G:\\Unity\\MST_JSAM\\analyse_csvs\\Data_Rogens\\MST\\17_TimQueißertREST1fertig.csv"
if computername == "XenonBang":
    dirname = "G:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\Results"
if computername == "Laptop-LittleBang":
    dirname = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\Results"

logfilename = os.path.join(dirname, "results.log")
logger_stat = logging.getLogger("")
logger_stat.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s :: %(module)s :: %(levelname)s :: %(name)s :: %(message)s')
file_handler_stat = logging.FileHandler(logfilename, 'w+')
file_handler_stat.setLevel(logging.DEBUG)
file_handler_stat.setFormatter(formatter)

c_handler = logging.StreamHandler(sys.stdout)
c_handler.setLevel(logging.DEBUG)
c_handler.setFormatter(formatter)

logger_stat.addHandler(file_handler_stat)
logger_stat.addHandler(c_handler)
logger_stat.debug("entering stats ....")

class Statistic_Exp_Dir():
    """ takes an directory with multiple files and 
        performes the statistik with the information in these files
        """
    def __init__(self, datadir, resultsdir, output_filename = "stats_output.txt"): #experiment_name = 'MST', groups = [], key = "cor_seqsum_lpn", level = "pn", paradigma = 0, is_independent = False):
        self.datadir = datadir
        self.resultsdir = resultsdir
        self.output_filename = output_filename
        self.all_exp = []
        self.groups = [] # a list of the groups... each group consists of a list of experiement classes
        self.print_output = []
        self.is_print_to_std = True
        self.first_write = True
        self.first_write
        # self.experiment_name = experiment_name
        # self.key = key
        # self.is_independent = is_independent
        # self.paradigma = paradigma
        # self.level = level
#        self.test_group_differences_ttest(key, self.is_independent, self.paradigma, self.level)
    def perform_all_available_analyses(self):
        self.read_exp_files_from_dir()
        self.create_groups()
        self.check_data_consistency()
        self.was_there_learning_in_each_experiment()
        self.estimate_q(is_q_fake_abs = True)
        self.estimate_phi()
        self.estimate_anova()


            

    def filter_experiments(self, experiment_names = [], days= [], vpns =[]):
        """ filter the experiments according to the given parameter
            return a list of the corresponding experiements"""
        exps = []
        for group in self.groups:
            for exp in group:
                is_exp = False
                is_day = False
                is_vpn = False
                if len(experiment_names) == 0:
                    is_exp = True
                else:
                    if exp.experiment_name in experiment_names:
                        is_exp = True
                if len(days) == 0:
                    is_day = True
                else:
                    if exp.day in days:
                        is_day = True
                if len(vpns) == 0:
                    is_vpn = True
                else:
                    if exp.vpn in vpns:
                        is_vpn = True
                if (is_exp and is_day and is_vpn):
                    exps.append(exp)
                    
        return exps

    def estimate_anova(self):
        """ Wyombs 2012
        We collected three behavioral variables during training: the time between key presses (i.e.,
        the vector of inter-key intervals), movement time (MT), and error. MT is the time elapsed
        from the initial to final key press. Error was scored as any trial not produced in the correct
        order as well as those trials not completed within the 8 s time limit. To test for learning, we
        entered the MT data for each subject, sequence, and session into a repeated-measures
        ANOVA (with subject treated as a random factor). To test for differences in error over
        training, we combined error for each frequent sequence and entered them for each subject
        and session using a repeated-measures ANOVA. """
        self.myprint("performing an ANOVA")

    # def create_one_csv(self):
    #     """ creates one big csv for further analysis with R"""
    #     self.all_exp = []
    #     self.groups = [] 
    #     self.read_exp_files_from_dir()
    #     self.create_groups()
    #     self.check_data_consistency()
    #     # create a dataframe with all important variables
    #     columnnames = [
    #         'experiment_name',
    #         'vpn',                                         # die Versuchspersonennummer
    #         'day',                                                               # DER Trainingstag
    #         'paradigma',                                    # falls an einem Tag unterschiedliche Interventionen erfolgten (MST_21 vs. MST_22 vs. MST_23) 
    #         'sequence_length',                           
    #         'filename',
    #         'root_dir',                                  
    #         'data_dir',                                  
    #         'is_delete_first',                            #! ein wesentlicher Unterschied ist noch, dass beim MST der erste ipi nicht geloescht wird      
    #         'all_ipi_lsln',                          
    #         'cor_ipi_lsln',                         
    #         'err_ipi_lsln',                        
    #         'all_hits_lsln',
    #         'all_ipi_lblsln',                        
    #         'cor_ipi_lblsln',                        
    #         'err_ipi_lblsln',                       
    #         'all_hits_lblsln',                      
    #         'all_ipi_lplsln',                     
    #         'cor_ipi_lplsln',                    
    #         'err_ipi_lplsln',                   
    #         'all_hits_lplsln',                  
    #         'all_ipi_lplblsln',                 
    #         'cor_ipi_lplblsln',                
    #         'err_ipi_lplblsln',                        
    #         'all_hits_lplblsln',                         
    #         'all_seqsum_lpn',                            
    #         'all_seqsum_lplbn',                          
    #         'all_seqtimesum_lplsn',                      
    #         'all_seqtimesum_lplblsn',                    
    #         'cor_seqsum_lpn',                            
    #         'cor_seqsum_lplbn',                          
    #         'cor_seqtimesum_lplsn',                      
    #         'cor_seqtimesum_lplblsn',                    
    #         'err_seqsum_lpn',                            
    #         'err_seqsum_lplbn',                          
    #         'err_seqtimesum_lplsn',                      
    #         'err_seqtimesum_lplblsn',                         
    #         'all_seqtimesum_slope_lpn',                 
    #         'all_seqtimesum_to_max_slope_lpn',           
    #         'cor_seqtimesum_slope_lpn',                  
    #         'cor_seqtimesum_to_max_slope_lpn',          
    #         'err_seqtimesum_slope_lpn',                  
    #         'err_seqtimesum_to_max_slope_lpn',          
    #         'all_seqtimesum_per_block_slope_lpn',        
    #         'all_seqtimesum_per_block_to_max_slope_lpn', 
    #         'cor_seqtimesum_per_block_slope_lpn',        
    #         'cor_seqtimesum_per_block_to_max_slope_lpn',  
    #         'err_seqtimesum_per_block_slope_lpn',        
    #         'err_seqtimesum_per_block_to_max_slope_lpn', 
    #         'all_seqnum_per_block_slope_lpn',            
    #         'cor_seqnum_per_block_slope_lpn',             
    #         'err_seqnum_per_block_slope_lpn',            
    #         'net_A',                                     
    #         'net_C',                                     
    #         'net_c',                                     
    #         'net_ipi',                                   
    #         'net_is_estimate_clustering',                
    #         'net_k',                                     
    #         'net_kappa',                                 
    #         'net_m',                                     
    #         'net_my2',                                  
    #         'net_phi',                                   
    #         'net_phi_real',                             
    #         'net_phi_fake_list',                        
    #         'net_q_real',                               
    #         'net_q_real_t',                             
    #         'net_q_real_p',                              
    #         'net_q_fake_list',                          
    #         'net_g_real',                             
    #         'net_g_fake_list',                          
    #         'net_is_adapt_communities_across_trials',    
    #         'net_is_estimate_Q',                        
    #         'net_num_random_Q',                          
    #         'net_resolution_parameter'                 
    #     ]

    #     columnnames = [
    #         'experiment_name',
    #         'vpn',                                         # die Versuchspersonennummer
    #         'day',                                                               # DER Trainingstag
    #         'paradigma',                                    # falls an einem Tag unterschiedliche Interventionen erfolgten (MST_21 vs. MST_22 vs. MST_23) 
    #         'sequence_length',                           
    #         'filename',
    #         'root_dir',                                  
    #         'data_dir',                                  
    #         'is_delete_first',                            #! ein wesentlicher Unterschied ist noch, dass beim MST der erste ipi nicht geloescht wird      
    #         'all_ipi_lsln',                          
    #         'cor_ipi_lsln',                         
    #         'err_ipi_lsln',                        
    #         'all_hits_lsln',
    #         'all_ipi_lblsln',                        
    #         'cor_ipi_lblsln',                        
    #         'err_ipi_lblsln',                       
    #         'all_hits_lblsln',                      
    #         'all_ipi_lplsln',                     
    #         'cor_ipi_lplsln',                    
    #         'err_ipi_lplsln',                   
    #         'all_hits_lplsln',                  
    #         'all_ipi_lplblsln',                 
    #         'cor_ipi_lplblsln',                
    #         'err_ipi_lplblsln',                        
    #         'all_hits_lplblsln',                         
    #         'all_seqsum_lpn',                            
    #         'all_seqsum_lplbn',                          
    #         'all_seqtimesum_lplsn',                      
    #         'all_seqtimesum_lplblsn',                    
    #         'cor_seqsum_lpn',                            
    #         'cor_seqsum_lplbn',                          
    #         'cor_seqtimesum_lplsn',                      
    #         'cor_seqtimesum_lplblsn',                    
    #         'err_seqsum_lpn',                            
    #         'err_seqsum_lplbn',                          
    #         'err_seqtimesum_lplsn',                      
    #         'err_seqtimesum_lplblsn',                         
    #         'all_seqtimesum_slope_lpn',                 
    #         'all_seqtimesum_to_max_slope_lpn',           
    #         'cor_seqtimesum_slope_lpn',                  
    #         'cor_seqtimesum_to_max_slope_lpn',          
    #         'err_seqtimesum_slope_lpn',                  
    #         'err_seqtimesum_to_max_slope_lpn',          
    #         'all_seqtimesum_per_block_slope_lpn',        
    #         'all_seqtimesum_per_block_to_max_slope_lpn', 
    #         'cor_seqtimesum_per_block_slope_lpn',        
    #         'cor_seqtimesum_per_block_to_max_slope_lpn',  
    #         'err_seqtimesum_per_block_slope_lpn',        
    #         'err_seqtimesum_per_block_to_max_slope_lpn', 
    #         'all_seqnum_per_block_slope_lpn',            
    #         'cor_seqnum_per_block_slope_lpn',             
    #         'err_seqnum_per_block_slope_lpn',            
    #         'net_A',                                     
    #         'net_C',                                     
    #         'net_c',                                     
    #         'net_ipi',                                   
    #         'net_is_estimate_clustering',                
    #         'net_k',                                     
    #         'net_kappa',                                 
    #         'net_m',                                     
    #         'net_my2',                                  
    #         'net_phi',                                   
    #         'net_phi_real',                             
    #         'net_phi_fake_list',                        
    #         'net_q_real',                               
    #         'net_q_real_t',                             
    #         'net_q_real_p',                              
    #         'net_q_fake_list',                          
    #         'net_g_real',                             
    #         'net_g_fake_list',                          
    #         'net_is_adapt_communities_across_trials',    
    #         'net_is_estimate_Q',                        
    #         'net_num_random_Q',                          
    #         'net_resolution_parameter'                 
    #     ]
    #     df = pd.DataFrame(columns=columnnames)
    #     # perform an loop to fill all experiments to it
    #     for i in range(5):
    #         df.loc[i, 'lib'] = 'name' + str(i)# 

    def read_exp_files_from_dir(self):
        """ read all files from one directory and append them to self.all_exp
        """
        files = [os.path.join(self.datadir, f) for f in os.listdir(self.datadir) if os.path.isfile(os.path.join(self.datadir, f))]
        for file in files:
            with open(file, 'rb') as fp:
                self.all_exp.append(pickle.load(fp))

    def create_groups(self):
        """ group the experiment data according to the performed experiment
        """
        # estimate the number of group
        self.experiment_names = []
        for exp in self.all_exp:
            if not(exp.experiment_name in self.experiment_names):
                self.experiment_names.append(exp.experiment_name)
        self.num_groups = len(self.experiment_names)
        
        for i in range(self.num_groups):
            self.groups.append([])
        for exp in self.all_exp:
            g = self.groups[self.experiment_names.index(exp.experiment_name)]
            g.append(exp)
        
        self.myprint(f"found {self.num_groups} groups in the given directory")
        #logger_stat.debug(tmp)
        for gr in range(self.num_groups):
            self.myprint(f"Group {gr} with name = {self.experiment_names[gr]} ({len(self.groups[gr])} files)")
            exp = self.groups[gr][0]
            self.myprint(f"number of Paradigma: {len(exp.cor_seqsum_lpn)}")
            self.myprint(f"... with number of blocks:", end=" ")
            for i in range(len(exp.cor_seqsum_lpn)): 
                self.myprint(f"{len(exp.all_seqsum_lplbn[i])}", end=" ")
            self.myprint(f" ")

    def check_data_consistency(self):
        """ checking that all experiment of a given type have the same number 
             paradigma and blocks
        """

        #logger_stat.debug(tmp)
        self.myprint("checking dataconsistency ...")
        self.myprint("checking that every experiment file of a given type and day has the same number of paradigma")
        for gr in range(self.num_groups):
            subj_counter = 0
            self.myprint("____________________________________")
            self.myprint(f"analysing Group {self.experiment_names[gr]}")
            for exp in self.groups[gr]:
                num_p = len(exp.cor_seqsum_lpn)
                num_b = []
                for i in range(num_p): 
                    num_b.append(exp.all_seqsum_lplbn[i])
                if subj_counter>0:
                    
                    if (not(num_p==num_p_old) or not(num_b==num_b_old)):
                        # in SEQ and SRTT there are always the same number of sequences per block
                        if (self.experiment_names[gr]=="SEQ" or self.experiment_names[gr]=="SRTT"):
                            self.myprint("DIFFERENCE")
                        if (self.experiment_names[gr]=="MST"):
                            if not(len(num_b)==len(num_b_old)):
                                self.myprint("DIFFERENCE")
                        #self.myprint(f"difference detected in group{gr} subj{subj_counter}  num_p = {num_p} num_bloecke = {num_b} .... to")
                        #self.myprint(f"difference detected in group{gr} subj{subj_counter-1}  num_p = {num_p_old} num_bloecke = {num_b_old}")
                else:
                    num_p_old = num_p
                    num_b_old = num_b
                self.myprint(f"subj{subj_counter: >4} file={exp.filename: >10} num_p = {num_p} num_bloecke = {num_b:} .... to")
                
                subj_counter +=1            

        self.myprint("checking dataconsistency finished")
        self.myprint("______________________________________________")
        

    def myprint(self, mystring, end = "\n"):
        if not(end=="\n"):
            mystring.strip("\n")
        if self.is_print_to_std:
            print(mystring, end = end)

        # try:
        #     last_char = self.print_output[-1][-1]
        # except:
        #     last_char = "\n"
        # if last_char == "\n":
        self.print_output.append(mystring + end)
        # else:
        #     self.print_output[-1] = self.print_output[-1] + mystring + end
    
            
        if self.first_write:
            with open(os.path.join(self.resultsdir, self.output_filename), "w") as f:
                f.write(mystring)
            self.first_write = False
        else:    

            with open(os.path.join(self.resultsdir, self.output_filename), "a") as f:
                f.write(mystring)
                f.write(end)

    """We collected three behavioral variables during training: the time between key presses (i.e.,
    the vector of inter-key intervals), movement time (MT), and error. MT is the time elapsed
    from the initial to final key press. Error was scored as any trial not produced in the correct
    order as well as those trials not completed within the 8 s time limit. To test for learning, we
    entered the MT data for each subject, sequence, and session into a repeated-measures
    ANOVA (with subject treated as a random factor). To test for differences in error over
    training, we combined error for each frequent sequence and entered them for each subject
    and session using a repeated-measures ANOVA. For all statistical tests, we set a probability
    threshold of P < 0.05 for the rejection of the null hypothesis.
        x #      phi
                    phi_real':             self.phi_real,
                    phi_fake_list
        n #     'phi_real_slope':       phi_real_slope,
        y #     'q_real':               self.q_real,
        y #     'q_real_t':             self.q_real_t,
        y #     'q_real_p':             self.q_real_p,
        y #     'q_fake_list':          self.q_fake_list,
        n #     'q_fake_list_mean':     sum(self.q_fake_list)/len(self.q_fake_list),
        y #     'g_real':               self.tolist_ck(self.g_real),
        y #     'g_fake_list':          self.tolist_ck(self.g_fake_list), # arrays verschachtelt in einer Liste
        y #     'A':                    self.A.tolist()
        C
        ipi
        k
        kappa
        m
        my2
            # }
    """
        
    def estimate_q(self, is_q_fake_abs = True):
        """ is_q_fake_abs whether the difference between shuffeled an real Q is 
            used or whether the absolute value will be used
        """
        self.myprint(" ")
        self.myprint("__________________________________________________________")
        self.myprint("________________________Q_________________________________")
        self.myprint("__________________________________________________________")
        self.myprint("We quantified chunking within each sequence by the optimized modularity Qmulti–trial of the")
        self.myprint("sequence networks. Modularity in this case measures the separability between clusters of")
        self.myprint("IKIs. Higher values of Q indicate a greater ease in separating chunks.")
        self.myprint("___________MST_______")
        exp_list = self.filter_experiments(experiment_names=["MST"], days=[1], vpns=[])
        self.group_q(exp_list, "MST Day 1", q_fake_abs = is_q_fake_abs)
        exp_list = self.filter_experiments(experiment_names=["MST"], days=[2], vpns=[])
        self.group_q(exp_list, "MST Day 2", q_fake_abs = is_q_fake_abs)
        self.myprint("___________SRTT_______")
        exp_list = self.filter_experiments(experiment_names=["SRTT"], days=[1], vpns=[])
        self.group_q(exp_list, "SRTT Day 1", q_fake_abs = is_q_fake_abs)
        exp_list = self.filter_experiments(experiment_names=["SRTT"], days=[2], vpns=[])
        self.group_q(exp_list, "SRTT Day 2", q_fake_abs = is_q_fake_abs)
        self.myprint("___________SEQ_______")
        exp_list = self.filter_experiments(experiment_names=["SEQ"], days=[1], vpns=[])
        self.group_q(exp_list, "SEQ Day 1", q_fake_abs = is_q_fake_abs)
        exp_list = self.filter_experiments(experiment_names=["SEQ"], days=[2], vpns=[])
        self.group_q(exp_list, "SEQ Day 2", q_fake_abs = is_q_fake_abs)
        self.myprint("end estimation group q")


    def group_q(self,exp_list, desc, q_fake_abs = False):
        """ in case of q_fake_abs = True then the abs difference will be computed
            after z-score correction 
            otherwise the simple difference will be used (this is not really correcte becaus different distributions)
        """
        if not exp_list:
            self.myprint("not experiments for {desc}")
            return
        subj_q = [] # a list 
        subj_q_fake = []
        subj_q_fake_z = []
        subj_q_abs = []
        subj_q_z = []
        print(len(exp_list))
        for exp in exp_list:
            subj_q_abs.append(abs(exp.net.Q_list[0] - statistics.mean(exp.net.Q_list[1:])))
            subj_q.append(exp.net.Q_list[0])
            subj_q_fake.append(statistics.mean(exp.net.Q_list[1:]))
            stderr=statistics.stdev(exp.net.Q_list[1:])/sqrt(len(exp.net.Q_list[1:]))
            subj_q_z.append((exp.net.Q_list[0]-statistics.mean(exp.net.Q_list[1:]))/stderr)
            # fuege jeden normalisieren fake wert in Form eines Z Wertes nun ein
            for f in exp.net.Q_list[1:]:
                subj_q_fake_z.append((f-statistics.mean(exp.net.Q_list[1:]))/stderr)
        if q_fake_abs:
            self.myprint(f"Subject z-score for real Q ")
            self.myprint(f"{str(subj_q_z)}")
            self.myprint(f"with mean = {statistics.mean(subj_q_z)}")
            self.myprint(exp.net.print_Q_parts())
            G1 = [abs(elem) for elem in subj_q_z]
            G2 = [abs(elem) for elem in subj_q_fake_z]
            #G2 = abs(subj_q_fake_z)
            #t, p = stats.ttest_ind(G1, G2)
            m = [statistics.mean(G1), statistics.mean(G2)]
            std = [statistics.stdev(G1), statistics.stdev(G2)]
            #self.print_pt_2g(key=desc, t=t,p=p, mymean = m, std=std)
            # data1 = [0.873, 2.817, 0.121, -0.945, -0.055, -1.436, 0.360, -1.478, -1.637, -1.869]
            # data2 = [1.142, -0.432, -0.938, -0.729, -0.846, -0.157, 0.500, 1.183, -1.075, -0.169]
            t, p = mannwhitneyu(G1, G2)
            
            self.print_pt_2g(key=desc, t=t,p=p, mymean = m, std=std)

#             G1 = np.array(abs(subj_q_z))
#             G2 = np.array(abs(subj_q_fake_z))
# #            G1 = np.array(subj_q_abs)
# #            G1 = subj_q_abs
# #            self.myprint(str(G1))
#             t, p = stats.ttest_1samp(G1,0.0)
#             m = G1.mean()
#             #m = statistics.mean(G1)
#             std = G1.std()
# #           std = statistics.stdev(G1)
#             self.print_pt_1g(desc, t,p, m, std)

        if not q_fake_abs:
            G1 = subj_q
            G2 = subj_q_fake
            t, p = stats.ttest_rel(G1, G2)
            m = [statistics.mean(G1), statistics.mean(G2)]
            std = [statistics.stdev(G1), statistics.stdev(G2)]
            self.print_pt_2g(key=desc, t=t,p=p, mymean = m, std=std)
        
    

    def estimate_phi(self):
        pass

    def was_there_learning_in_each_experiment(self):
        self.myprint("Question 1: Was there learning?")
        self.myprint("1.1. is there a linear increase in the number of correct sequences per block per paradigma (linear Regression)?")
        
        for group_idx in range(len(self.groups)):
            exp_name = self.experiment_names[group_idx]
            if exp_name == "MST":
                self.myprint("___________________________________________________")
                self.myprint("START____MST______________________________________")
                self.myprint("MST")
                self.myprint("1.1. is there a linear increase in the number of correct sequences per block per paradigma (linear Regression)?")
                self.myprint(".... for day 1...")
                exp_list = self.filter_experiments(experiment_names=["MST"], days=[1], vpns=[])
                self.estimate_linear_regression(exp_list, "cor_seqsum_lplbn", 0, mean_last_dim = False, num_blocks=10)
                self.myprint(".... for day 2...")
                exp_list = self.filter_experiments(experiment_names=["MST"], days=[2], vpns=[])
                self.estimate_linear_regression(exp_list, "cor_seqsum_lplbn", 0, mean_last_dim = False, num_blocks=10)
                self.myprint("1.1. is there a linear decrease in the Time to perform an sequence per block per paradigma (linear Regression)?")
                self.myprint(".... for day 1...")
                exp_list = self.filter_experiments(experiment_names=["MST"], days=[1], vpns=[])
                self.estimate_linear_regression(exp_list, "cor_seqtimesum_lplblsn", 0, mean_last_dim = True, num_blocks=10)
                self.myprint(".... for day 2...")
                exp_list = self.filter_experiments(experiment_names=["MST"], days=[2], vpns=[])
                self.estimate_linear_regression(exp_list, "cor_seqtimesum_lplblsn", 0, mean_last_dim = True, num_blocks=10)
                self.myprint("now use the slope of each subject and perform a t-test for the group")
                exp_list = self.filter_experiments(experiment_names=["MST"], days=[1], vpns=[])
                self.ttest_one_group(exp_list, "cor_seqtimesum_slope_lpn", 0)          
                exp_list = self.filter_experiments(experiment_names=["MST"], days=[2], vpns=[])
                self.ttest_one_group(exp_list, "cor_seqtimesum_slope_lpn", 0)
                self.myprint("END____MST______________________________________")
                self.myprint("___________________________________________________")
                self.myprint(" ")
            if exp_name == "SEQ":
                self.myprint("___________________________________________________")
                self.myprint("START____SEQ______________________________________")
                self.myprint("SEQ")
                # self.myprint("1.1. is there a linear decrease in the number of correct sequences per block per paradigma (linear Regression)?")
                # self.myprint(".... for day 1...")
                # exp_list = self.filter_experiments(experiment_names=["SEQ"], days=[1], vpns=[])
                # self.estimate_linear_regression(exp_list, "cor_seqsum_lplbn", 0)
                # self.myprint(".... for day 2...")
                # exp_list = self.filter_experiments(experiment_names=["SEQ"], days=[2], vpns=[])
                # self.estimate_linear_regression(exp_list, "cor_seqsum_lplbn", 0)
                self.myprint("1.1. is there a linear decrease in the Time to perform an sequence per block per paradigma (linear Regression)?")
                self.myprint(".... for day 1...")
                exp_list = self.filter_experiments(experiment_names=["SEQ"], days=[1], vpns=[])
                print([e.filename for e in exp_list])
                self.estimate_linear_regression(exp_list, "cor_seqtimesum_lplblsn", 0, mean_last_dim = True, num_blocks=10)
                self.myprint(".... for day 2...")
                exp_list = self.filter_experiments(experiment_names=["SEQ"], days=[2], vpns=[])
                print([e.filename for e in exp_list])
                self.estimate_linear_regression(exp_list, "cor_seqtimesum_lplblsn", 0, mean_last_dim = True, num_blocks=10)
                self.myprint("now use the slope of each subject and perform a t-test for the group")
                exp_list = self.filter_experiments(experiment_names=["SEQ"], days=[1], vpns=[])
                self.ttest_one_group(exp_list, "cor_seqtimesum_slope_lpn", 0)          
                exp_list = self.filter_experiments(experiment_names=["SEQ"], days=[2], vpns=[])
                self.ttest_one_group(exp_list, "cor_seqtimesum_slope_lpn", 0)
                self.myprint("END____SEQ______________________________________")
                self.myprint("___________________________________________________")
                self.myprint(" ")
            if exp_name == "SRTT":
                self.myprint("___________________________________________________")
                self.myprint("START____SRTT______________________________________")
                self.myprint("SRTT")
                self.myprint("1.1. is there a linear decrease in the Time to perform an sequence per block per paradigma (linear Regression)?")
                self.myprint(".... for day 1...")
                exp_list = self.filter_experiments(experiment_names=["SRTT"], days=[1], vpns=[])
                self.estimate_linear_regression(exp_list, "cor_seqtimesum_lplblsn", 0, mean_last_dim = True, num_blocks=6)
                self.myprint(".... for day 2...")
                exp_list = self.filter_experiments(experiment_names=["SRTT"], days=[2], vpns=[])
                self.estimate_linear_regression(exp_list, "cor_seqtimesum_lplblsn", 0, mean_last_dim = True, num_blocks=6)
                self.myprint("1.1. is there a linear decrease in the Time to perform an sequence per block per paradigma (linear Regression) ALLL?")
                self.myprint(".... for day 1...")
                exp_list = self.filter_experiments(experiment_names=["SRTT"], days=[1], vpns=[])
                self.estimate_linear_regression(exp_list, "all_seqtimesum_lplblsn", 0, mean_last_dim = True, num_blocks=6)
                self.myprint(".... for day 2...")
                exp_list = self.filter_experiments(experiment_names=["SRTT"], days=[2], vpns=[])
                self.estimate_linear_regression(exp_list, "all_seqtimesum_lplblsn", 0, mean_last_dim = True, num_blocks=6)   

                self.myprint("now use the slope of each subject and perform a t-test for the group")
                exp_list = self.filter_experiments(experiment_names=["SRTT"], days=[1], vpns=[])
                self.ttest_one_group(exp_list, "cor_seqtimesum_slope_lpn", 0)          
                exp_list = self.filter_experiments(experiment_names=["SRTT"], days=[2], vpns=[])
                self.ttest_one_group(exp_list, "cor_seqtimesum_slope_lpn", 0)          
                self.myprint("END____SRTT______________________________________")
                self.myprint("_________________________________________________")
                self.myprint(" ")
                

    def ttest_one_group(self, exp_list, key, paradigma, mean_last_dim = False, is_independent = True):
        # reduce a list of lists to a list by averaging
        subj_values = [] # a list 
        for exp in exp_list:
            v = getattr(exp,key)
            t = v[paradigma][0]
        
            if mean_last_dim:
                t = self.list_of_list_to_list(t)
            subj_values.append(t)

        G1 = np.array(subj_values)
       
        # G1 = self.list_of_list_to_list(data[0])
        # G2 = self.list_of_list_to_list(data[1])
        self.myprint(str(G1))
        t, p = stats.ttest_1samp(G1,0.0)
        m = G1.mean()
        #m = statistics.mean(G1)
        std = G1.std()
#        std = statistics.stdev(G1)
        
        self.print_pt_1g(key, t,p, m, std)

    def print_pt_1g(self,key, t,p, mymean, std):
        self.myprint(f"{key} t-test different from 0  p={p} t={t}, m={mymean}, std={std}")

    def estimate_linear_regression(self, exp_list, key, paradigma, mean_last_dim = False, num_blocks=6):
        """ performing linear regression with statsmodels"""
        subj_values = [] # a list 
        
        for exp in exp_list:
            v = getattr(exp,key)
            t = v[paradigma]
            print(f"the data of file {exp.filename}  and parameter={key}... {t}")
            if mean_last_dim:
                t = self.list_of_list_to_list(t)
            if len(t)==(num_blocks-1):
                t.append(mean(t))
            subj_values.append(t)
            # print(len(t))
            # print(exp.experiment_name)
            # print(exp.filename)

        X = np.array(subj_values)
        print(X)
        #Xm = np.mean(X,axis=0)
        Xm = np.sum(X,axis=0)
        Xm =sm.add_constant(Xm, prepend=False)
        print(Xm)
        y = np.arange(0,Xm.shape[0],1)
        mod = sm.OLS(y,Xm)
        self.myprint("Regression across the mean of all subjects for each blocks ...")
        self.myprint(str(Xm))
        res = mod.fit()
        self.myprint(res.summary().as_text())

    def test_group_differences_ttest(self, key, is_independent, paradigma, level):
        # ich laufe ueber die Buchstaben der levelbeschreibung und ziehe die richtigen Daten heraus
        values = self.get_target_values_by_key(key)
        for i in range(len(level)):
            if level[i]== 'p':
                values = self.filter_target_values_by_paradigma(values, paradigma)
            if level[i]=='n':
                self.test_group_differences_two_groups(key, values, is_independent=is_independent)

#        d = self.get_target_values_by_key_and_level(key, paradigma, level)
 #       if len(d)==2:
            
    

    def get_target_values_by_key(self, key):
        """ get the target attributes out of the experiment objects 
            and put these into a list for each group 
        """
        target_val = []
        for group in self.groups:
            subject_list = []
            for subj_exp in group.subj_exp_list:
                exp_value = getattr(subj_exp, key)
                subject_list.append(exp_value)
            target_val.append(subject_list)
        return target_val

    def filter_target_values_by_paradigma(self,values, paradigma):
        new_val = []
        for attribute_list in values:
            new_attribute_list = []
            for attribute in attribute_list:
                new_attribute_list.append(attribute[paradigma])
            new_val.append(new_attribute_list)
        return new_val


    

    def list_of_list_to_list(self, input_list):
        # if input_list is a list of list then it will be transformed to a list
        # by averaging the second dimension
        if any(isinstance(el, list) for el in input_list):
            input_list = [statistics.mean(f) for f in input_list]
        return input_list



    def test_group_differences_two_groups(self, key, data, is_independent=True):
        # reduce a list of lists to a list by averaging
        G1 = self.list_of_list_to_list(data[0])
        G2 = self.list_of_list_to_list(data[1])
            
        if is_independent:
            t, p = stats.ttest_ind(G1, G2)
        else:
            t, p = stats.ttest_rel(G1, G2)
        m = [statistics.mean(G1), statistics.mean(G2)]
        std = [statistics.stdev(G1), statistics.stdev(G2)]

        self.print_pt_2g(key=key, t=t,p=p, mymean = m, std=std)


    def get_target_values_by_key_level_1(self, key, paradigma):
        # extracts from the dictionaries of all groups the value
        # with key = key
        # returns a list with groups, the group list consists of a list with the key elements
        target_val = []
        for group in self.groups:
            subject_list = []
            for subj_exp in group.subj_exp_list:
                exp_value = getattr(subj_exp, key)[paradigma]
                print(exp_value)
                subject_list.append(exp_value)
            target_val.append(subject_list)
        return target_val


    def print_pt_2g(self, key, t, p, mymean=0, std=0):
        mymean = [float(m) for m in mymean]
        std = [float(s) for s in std]
        self.myprint(f"{key} p = {p:.7}  with t = {t:.3}  (mean = {mymean[0]:.3} +- {std[0]:.4}  vs. {mymean[1]:.3} +- {std[1]:.4}")

    def show_group_differences(self, key):
        data = self.get_target_values_by_key(key)
        data = np.asarray(data)
        print(f"Group Results of {key}")
        df = pd.DataFrame(data.T, columns = [self._ids[0], self._ids[1]])
        print(df.head(30))

    def plot_one_group_sequence(self, key):
        data = self.get_target_values_by_key(key)
        #print(data)
        #print("---")
        data = data[0]
        #print(np.asarray(data))
        #print(data)
        #print(data.shape)
        for subj in data:
            plt.plot(subj)
        
        plt.show()
        # plt.plot( 'x', 'y1', data=data, marker='o', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=4)
        # plt.plot( 'x', 'y2', data=df, marker='', color='olive', linewidth=2)
        # plt.plot( 'x', 'y3', data=df, marker='', color='olive', linewidth=2, linestyle='dashed', label="toto")
        # plt.legend()

    
if __name__ == "__main__":
    # seed random number generator
    experiment_name = 'MST'
    experiment_name = 'ASTEROID'
    _ids = ["MST_G1_", "MST_G2_"]
    _ids = ["ASTEROID_G1_", "ASTEROID_G2_"]
    my_stat = Statistic(experiment = experiment_name, group_list= [], data_path = ".\\Data_python", _ids = _ids)
    #my_stat.test_group_differences_ttest('corrsq_slope')
    my_stat.test_group_differences_ttest('success_per_block_slope', is_independent=False)
    my_stat.test_group_differences_ttest('abs_success', is_independent=False)
    my_stat.show_group_differences('abs_success')
    my_stat.show_group_differences('success_per_block_slope')
