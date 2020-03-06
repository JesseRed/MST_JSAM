import pandas as pd
import numpy as np
from os import listdir, rename
import os
from os.path import isfile, join
from random import random
from scipy.linalg import cholesky
from scipy.stats import pearsonr

class SIM():
    def __init__(self, paradigm_name, inputfile, outputfile):
        # whether in the adaptation process it will be tried to set the
        # node in the next trial to the same node of the previous
        self.paradigm_name = paradigm_name
        self.inputfile = inputfile
        self.outputfile = outputfile
        if paradigm_name=='MST':
            self.create_MST()
        if paradigm_name == 'SRTT':
            self.create_SRTT()
    
    def create_MST(self):


        print(f"create MST file")

        # Correlation matrix
        corr_mat= np.array([[1.0, 0.7, 0.2, 0.1],
                            [0.7, 1.0, 0.8, 0.2],
                            [0.2, 0.8, 1.0, 0.4],
                            [0.1, 0.2, 0.4, 1.0]])
        # 0-1 0.6
        # 0-2 0.3
        # 1-3 0.2
        # Compute the (upper) Cholesky decomposition matrix
        upper_chol = cholesky(corr_mat)

        # Generate 3 series of normally distributed (Gaussian) numbers
        rnd = np.random.normal(0.0, 1.0, size=(1000000, 4))

        # Finally, compute the inner product of upper_chol and rnd
        cor_samples = rnd @ upper_chol

        
        chunk_length = 4
        df = pd.read_csv(self.inputfile, sep = ';' )
        t_org = []
        b_org = []
       
        # wir passen nur die Zeiten an 
        for idx, row in df.iterrows():

            t_org.append(float(row["Time Since Block start"].replace(',','.')))
            b_org.append(int(row["BlockNumber"]))
        t_new = []
        # ersetze nun die Zeiten
        block_idx = 1
        z = 0
        t_last = 0
        sample_idx = 0 # die Idx aus der correlierten Zufallsvariablen
        if chunk_length == 4:
            #while idx < len(t_org)-5
            for idx in range(len(t_org)):
                if block_idx!=b_org[idx]:
                    block_idx+=1
                    z = 0
                else:
                    
                    if z ==0:   
                        tmp = t_org[idx]
                    if z == 1:
                        tmp = t_last+ cor_samples[sample_idx,0]
                    if z == 2:
                        tmp = t_last+ cor_samples[sample_idx,1]
                    if z == 3:
                        tmp = t_last+ cor_samples[sample_idx,2]
                    if z == 4:
                        tmp = t_last+ cor_samples[sample_idx,3]

                z+=1
                if z==5:
                    z=0
                    sample_idx+=1
                t_last = tmp
                t_new.append(tmp)

        for idx in range(df.shape[0]):
             # wir passen nur die Zeiten an 
            df.iloc[idx,2]= str(t_new[idx])

        print(df.head(12))
        df.to_csv(self.outputfile, sep=';', index=False)

    def create_SRTT(self):
        print(f"create SRTT file ... still not implemented")

        