import logging
from multiprocessing import Process
logger = logging.getLogger(__name__)

# def get_and_save_data_multiprocess(self):
#     """ get original data from every mst.csv file 
#         estimate all required parameters and save them
#         to a result file
#         split these operations to multiprossess = number of CPUs

#     """  
#     logger.info(f"entering get_and_save_data_multiprocess")
#     a = 0
    
#     for i in range(0,len(self.files),5):
#         start = i
#         stop = i + 5
#         if stop>=len(self.files):
#             stop = len(self.files)
        
#         filelist = self.files[start:stop]
#         # Setup a list of processes that we want to run
#         processes = [multiprocessing.Process(target=get_and_save_data_for_one_subj, args=(self,filename)) for filename in filelist]

#         # Run processes
#         for p in processes:
#             logger.debug(f"now starting Process: {p.name}")
#             p.start()

#         # Exit the completed processes
#         for p in processes:
#             logger.debug(f"now joining Process: {p.name}")
#             p.join()


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
#     # mp_output.put(subj_class)

def print_func(continent='Asia', continent2 = "Europe"):
    print(f'The name of continent is : {continent} , {continent2}')

if __name__ == "__main__":  # confirms that the code is under main function
    names = ['America', 'Europe', 'Africa']
    procs = []
    # proc = Process(target=print_func)  # instantiating without any argument
    # procs.append(proc)
    # proc.start()

    # instantiating process with arguments
    print(names)
    for name in names:
        print(f"start process with the name = {name}")
        proc = Process(target=print_func, args=(name, name))
        procs.append(proc)
        proc.start()

    # complete the processes
    for proc in procs:
        proc.join()