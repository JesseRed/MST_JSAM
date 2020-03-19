import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, rename
import os
from os.path import isfile, join
from statistics import mean, stdev
import statistics
import networkx
import time
from filehandler import FileHandler
from helper_functions import tolist_ck


class ASTEROID():
    def __init__(self, fullfilename=".\\Data_Asteroid\\VPnr_1_Julia​Wolff​Asteroid1_date_20191207100421_fertig.csv", path_output=".\\Data_python", _id="nox_id"):
        self.fullfilename = fullfilename
        base = os.path.basename(self.fullfilename)
        self.filename = os.path.splitext(base)[0]
        # print(f"filename = {self.filename}")
        self.path_output = path_output
        self._id = _id
        self.filehandler = FileHandler(path_output=self.path_output, filename=self.filename, time_identifier=_id)
        self.df = pd.read_csv(self.fullfilename, sep=";", engine = 'python')
        self.abs_success, self.success_per_block, self.success_per_trial = self.get_success_rate()
        self.success_per_block_slope = self.estimate_slope(self.success_per_block)
        self.success_per_trial_slope = self.estimate_trial_slope(self.success_per_trial)
        self.mydict = self.create_dict()
        
        #self.estimate_chunks() 

    def save(self):
        mydict = self.create_dict()
        self.filehandler.write(mydict)

    def create_dict(self):
        ''' generating a dictionary with all available information of this class
        '''
        mydict = {
            'experiment':              'ASTEROID',
            # 'ipi' :                     tolist_ck(self.ipi),
            # 'hits':                     tolist_ck(self.hits),
            # 'ipi_cor' :                 tolist_ck(self.ipi_cor),
            'abs_success' :            self.abs_success,
            'success_per_block':       tolist_ck(self.success_per_block),
            'success_per_trial':       tolist_ck(self.success_per_trial),
            'success_per_block_slope': tolist_ck(self.success_per_block_slope),
            'success_per_trial_slope': tolist_ck(self.success_per_trial_slope)
        }
        # ergaenze die Network Daten falls vorhanden
        if hasattr(self, 'net'):
            net_dict = self.net.get_results_as_json()
            mydict.update(net_dict)
        return mydict

    def add_network_class(self, coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= True, is_estimate_Q= False, num_random_Q=0):
        print(f"no network class implemented for the MST paradigm")
        # self.net = Network(self.ipi_cor, coupling_parameter = coupling_parameter,  resolution_parameter = resolution_parameter,is_estimate_clustering= is_estimate_clustering, is_estimate_Q= is_estimate_Q, num_random_Q=num_random_Q)
        # self.net.filename = self.fullfilename

    def get_success_rate(self):
        success_per_block = []
        success_per_trial = []
        hits_in_last_block = 0
        hits_in_last_trial = 0
        for block in np.nditer(pd.unique(self.df['Block'])):
            df_block = self.df.loc[self.df['Block']==block,:]
            success_per_block.append(max(df_block['NumberOfHits'])-hits_in_last_block)
            hits_in_last_block = max(df_block['NumberOfHits'])
            success_per_trial_in_block = []
            for trial in np.nditer(pd.unique(df_block['SequenzNum'])):
                max_hits_in_trial = max(df_block.loc[df_block['SequenzNum']==trial,'NumberOfHits'])
                success_per_trial_in_block.append(max_hits_in_trial-hits_in_last_trial)
                hits_in_last_trial = max_hits_in_trial
            success_per_trial.append(success_per_trial_in_block)
        abs_success = max(self.df['NumberOfHits'])
        return abs_success, success_per_block, success_per_trial

    def estimate_trial_slope(self, y):
        # von interesse ist hier die slope ueber die bloecke in jedem trial
        arr = np.asarray(y)
        slopes = []
        for trial in range(arr.shape[1]):
            l = list(arr[:, trial])
            slopes.append(self.estimate_slope(l))
        return slopes
    
    def estimate_slope(self, y):
        x = np.arange(len(y))
        slope, b = np.polyfit(x, y, 1)
        return slope

if __name__ == '__main__':
    ast = ASTEROID()
    print(f"success per block = {ast.success_per_block}")
    print(f"success per trial = {ast.success_per_trial}")
    print(f"success per block_slope = {ast.success_per_block_slope}")
    print(f"success per trial slope = {ast.success_per_trial_slope}")
    ast.save()


