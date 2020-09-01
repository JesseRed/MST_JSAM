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
from multiprocessing import Pool # ProcessingPool as Pool

logger = logging.getLogger(__name__)
mp_output = multiprocessing.Queue()



# def get_and_save_data_for_one_subj(self, filename):

#     if self.experiment == 'MST':
#         logger.info(f"Experiment = MST")
#         subj_class = MST(fullfilename = filename, sequence_length = self.sequence_length, path_output = self.path_outputfiles, _id = self._id)
#     if self.experiment == 'SEQ':
#         subj_class = SEQ(fullfilename = filename, sequence_length = self.sequence_length, path_output = self.path_outputfiles, _id = self._id)
#     if self.experiment == 'SRTT':
#         subj_class = SRTT(fullfilename = filename, path_output = self.path_outputfiles, _id = self._id)
#     #    subj_class = SRTT(filename)
#     if self.experiment == 'ASTEROID':
#         subj_class = ASTEROID(fullfilename = filename, path_output = self.path_outputfiles, _id = self._id)
#     if self.is_estimate_network:
#         subj_class.add_network_class(coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= self.is_clustering, is_estimate_Q= self.is_estimate_Q, num_random_Q=self.num_random_Q)
    
#     subj_class.save()
#     mp_output.put(subj_class)


def get_and_save_data_for_one_subj(filename, experiment="MST", is_estimate_network=False, sequence_length=8, path_outputfiles="./tmp", _id=0, coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= False, is_estimate_Q= False, num_random_Q=5):
    print(f"in get_and_save_data_for_one_subj")
    if experiment == 'MST':
        print(f"estimate MST")
        subj_class = MST(fullfilename = filename, sequence_length = sequence_length, path_output = path_outputfiles, _id = _id)
        print(f"after estimation of MST")
    if experiment == 'SEQ':
        subj_class = SEQ(fullfilename = filename, sequence_length = sequence_length, path_output = path_outputfiles, _id = _id)
    if experiment == 'SRTT':
        subj_class = SRTT(fullfilename = filename, path_output = path_outputfiles, _id = _id)
    if experiment == 'ASTEROID':
        subj_class = ASTEROID(fullfilename = filename, path_output = path_outputfiles, _id = _id)

    subj_exp = Experiment(subj_class.experiment_name, subj_class.vpn, subj_class.day, subj_class.sequence_length, path_outputfiles, is_load=False, df=subj_class.df)

    if is_estimate_network:
        subj_exp.add_network_class(coupling_parameter = coupling_parameter, resolution_parameter = resolution_parameter, is_estimate_clustering= is_estimate_clustering, is_estimate_Q= is_estimate_Q, num_random_Q= num_random_Q)
            
    subj_exp.save()
    

class Group():
    def __init__(self, experiment_name = 'MST', path_inputfiles="./Data MST", filepattern="Tag1", 
        path_outputfiles = ".\\Data_python", _id = None, sequence_length=10, 
        is_estimate_network = False, is_clustering = False, is_estimate_Q = False,
        num_random_Q = 10, coupling_parameter = 0.3, resolution_parameter = 0.9,
        is_multiprocessing = False, show_images = False, target_color = 8,
        num_processes = 6):

        self.experiment_name = experiment_name
        self.path_inputfiles = path_inputfiles
        self.sequence_length = sequence_length # only relevant for MST
        self.filepattern = filepattern
        self.path_outputfiles = path_outputfiles
        self.is_estimate_network = is_estimate_network
        self.is_clustering = is_clustering
        self.is_estimate_Q = is_estimate_Q
        self.num_random_Q = num_random_Q
        self.coupling_parameter = coupling_parameter
        self.resolution_parameter = resolution_parameter
        self.is_multiprocessing = is_multiprocessing
        self.target_color = target_color
        self.show_images = show_images
        self.files = self.get_group_files()
        self.subj_exp_list = []
        self.num_processes = num_processes
                                                                                                    
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
        if self.is_multiprocessing:
            #self.get_data_multiprocessing()
            self.get_and_save_data_multiprocess3()
        else:
            self.get_data_singleprocessing()

    def get_data_singleprocessing(self):
        # self.improvement = []
        # self.corrsq = []
        logger.info(f"entering get_data_singleprocessing")
        for filename in self.files:
            if self.experiment_name == 'MST':
                subj_class = MST(fullfilename = filename, sequence_length = self.sequence_length, path_output = self.path_outputfiles, _id = self._id)
            if self.experiment_name == 'SEQ':
                subj_class = SEQ(fullfilename = filename, sequence_length = self.sequence_length, path_output = self.path_outputfiles, _id = self._id, show_images = self.show_images, target_color = self.target_color)
            if self.experiment_name == 'SRTT':
                subj_class = SRTT(fullfilename = filename, path_output = self.path_outputfiles, _id = self._id, sequence_length = self.sequence_length)
            #    subj_class = SRTT(filename)
            if self.experiment_name == 'ASTEROID':
                subj_class = ASTEROID(fullfilename = filename, path_output = self.path_outputfiles, _id = self._id)
            
            # alle individuellen Klassen haben die gleichen Attribute die an die Experimentklasse uebergeben werden
            subj_exp = Experiment(subj_class.experiment_name, subj_class.vpn, subj_class.day, subj_class.sequence_length, self.path_outputfiles, is_load=False, df=subj_class.df)

            if self.is_estimate_network:
                subj_exp.add_network_class(coupling_parameter = 0.03, resolution_parameter = 0.9, is_estimate_clustering= self.is_clustering, is_estimate_Q= self.is_estimate_Q, num_random_Q=self.num_random_Q)
            
            subj_exp.save()

            self.subj_exp_list.append(subj_exp)
        #     self.corrsq.append(mst.corrsq)
        #     self.improvement.append(mst.improvement)



    # @staticmethod
    # def set_global_self():
    #     global class_instance
    #     if not class_instance:
    #         class_instance = 


    # def get_and_save_data_multiprocess(self):
    #     """ get original data from every mst.csv file 
    #         estimate all required parameters and save them
    #         to a result file
    #         split these operations to multiprossess = number of CPUs
    
    #     """  
      
    #     filelist = self.files
    #     print(f"filelist = {filelist} with len = {len(filelist)}")
    #     # Setup a list of processes that we want to run
    #     processes = [multiprocessing.Process(target=get_and_save_data_for_one_subj, args=(filename, self.experiment_name, self.is_estimate_network , self.sequence_length, self.path_outputfiles, self._id, self.coupling_parameter, self.resolution_parameter, self.is_clustering, self.is_estimate_Q, self.num_random_Q)) for filename in filelist]
    #     for filename in filelist:
    #         print(f"starting with filename = {filename}")
    #         get_and_save_data_for_one_subj(filename, self.experiment_name, self.is_estimate_network , self.sequence_length, self.path_outputfiles, self._id, self.coupling_parameter, self.resolution_parameter, self.is_clustering, self.is_estimate_Q, self.num_random_Q)
    
    def get_and_save_data_multiprocess2(self):
        """ get original data from every mst.csv file 
            estimate all required parameters and save them
            to a result file
            split these operations to multiprossess = number of CPUs"""
        # for i in range(0,len(self.files),5):
        #     start = i
        #     stop = i + 5
        #     if stop>=len(self.files):
        #         stop = len(self.files)
        #     filelist = self.files[start:stop]

        filelist = self.files
        print(f"filelist = {filelist} with len = {len(filelist)}")
        # Setup a list of processes that we want to run
        for filename in filelist:
            get_and_save_data_for_one_subj(filename, self.experiment_name, self.is_estimate_network , self.sequence_length, self.path_outputfiles, self._id, self.coupling_parameter, self.resolution_parameter, self.is_clustering, self.is_estimate_Q, self.num_random_Q)
    
            #Get process results from the output queue
            #self.subj_exp_list = [mp_output.get() for p in processes]
            #print("results after multiprocessor")
            #print(type(self.subj_exp_list))
            #print(type(self.subj_exp_list[0]))

        # for filename in self.files:
        #     multiprocessing.Process(target=get_and_save_data_for_one_subj, args=(self,filename)).start()       
        # with multiprocessing.Pool(initializer = set_global_self) as pool:
        #     pool.map(get_and_save_data_for_one_subj, self.files)

    def get_and_save_data_multiprocess3(self):
        """ get original data from every mst.csv file 
            estimate all required parameters and save them
            to a result file
            split these operations to multiprossess = number of CPUs
    
        """  
        logger.info(f"entering get_and_save_data_multiprocess")
        a = 0
        
        for i in range(0,len(self.files),self.num_processes):
            start = i
            stop = i + self.num_processes
            if stop>=len(self.files):
                stop = len(self.files)
            filelist = self.files[start:stop]

            #filelist = self.files
            print(f"filelist = {filelist} with len = {len(filelist)}")
            # Setup a list of processes that we want to run
            processes = [multiprocessing.Process(target=get_and_save_data_for_one_subj, args=(filename, self.experiment_name, self.is_estimate_network , self.sequence_length, self.path_outputfiles, self._id, self.coupling_parameter, self.resolution_parameter, self.is_clustering, self.is_estimate_Q, self.num_random_Q)) for filename in filelist]
            # processes = []
            # for filename in filelist:
            #     #proc = multiprocessing.Process(target = parallel2)
            #     proc = multiprocessing.Process(target=get_and_save_data_for_one_subj, args=(filename, self.experiment_name, self.is_estimate_network , self.sequence_length, self.path_outputfiles, self._id, self.coupling_parameter, self.resolution_parameter, self.is_clustering, self.is_estimate_Q, self.num_random_Q))
            #     processes.append(proc)
            #     print(f"now starting process with filename = {filename}")
            #     proc.start()

            # Run processes
            for p in processes:
                logger.debug(f"now starting Process: {p.name}")
                print(f"now starting Process: {p.name}")
                p.start()

            # Exit the completed processes
            print(f"now joining processes")
            for p in processes:
                print(f"whaiting for Process: {p.name}")
                p.join()

        #Get process results from the output queue
        #self.subj_exp_list = [mp_output.get() for p in processes]
        print("results after multiprocessor")
            #print(type(self.subj_exp_list))
            #print(type(self.subj_exp_list[0]))

        # for filename in self.files:
        #     multiprocessing.Process(target=get_and_save_data_for_one_subj, args=(self,filename)).start()       
        # with multiprocessing.Pool(initializer = set_global_self) as pool:
        #     pool.map(get_and_save_data_for_one_subj, self.files)

    
    def perform_network_analysis(self):
        for subj in self.subj_exp_list:
            subj.add_network_class()

    def save_data(self):
        for subj in self.subj_exp_list:
            subj.save()

        # print(f"cor = {self.improvement}")
        # print(f"improvement = {self.improvement}")
        # print(f"mittelwert der improvement = {np.mean(self.improvement)}")
        # print(f"Standardabweichung der lersteigung = {np.std(self.improvement)}")

if __name__ == '__main__':
    print(f"Gruppe 1")
    # seq_group1 = Group(experiment = 'SEQ', path_inputfiles = ".\\Data\\SEQ", filepattern="Elisabeth", path_outputfiles = ".\\Data_python", sequence_length = 8, is_estimate_network=True)
    seq_group1 = Group(experiment = 'MST', path_inputfiles = ".\\Data\\MST", filepattern="Elisabeth", path_outputfiles = ".\\Data_python", sequence_length = 8, is_estimate_network=True)
    # seq_group1 = Group(experiment = 'SRTT', path_inputfiles = ".\\Data\\SRTT", filepattern="Elisabeth", path_outputfiles = ".\\Data_python", sequence_length = 8, is_estimate_network=True)
    seq_group1.get_data()
    seq_group1.save_data()
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
