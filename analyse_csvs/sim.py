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
        if paradigm_name == 'SEQ':
            self.create_SEQ()
        if paradigm_name == 'SEQsimple':
            self.create_SEQsimple()
        if paradigm_name == 'SEQdirect':
            self.create_SEQdirect()
    
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
            
            #t_org.append(float(row["Time Since Block start"]))
            t_org.append(float(row["Time Since Block start"].replace(',','.')))
            b_org.append(int(row["BlockNumber"]))
        t_new = []
        # ersetze nun die Zeiten
        block_idx = 1
        z = 0
        t_last = 0
        cor_samples = (cor_samples - np.amin(cor_samples))/10
        print(f"the first 10 t_orgs")
        print(f"{t_org[0:10]}")
        print(f"cor_samples")
        print(f"{cor_samples[0:10]}")
        sample_idx = 0 # die Idx aus der correlierten Zufallsvariablen
        t_last = 0
        if chunk_length == 4:
            #while idx < len(t_org)-5
            for idx in range(len(t_org)):
                if block_idx!=b_org[idx]:
                    block_idx+=1
                    z = 0
                    t_last = 0
                else:
                    
                    if z ==0:   
                        tmp = t_last + np.random.uniform(np.amax(cor_samples), np.amax(cor_samples)+2.1)
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
                    t_last = 0
                    sample_idx+=1
                t_last = tmp
                t_new.append(tmp)
        # if chunk_length == 4:
        #     #while idx < len(t_org)-5
        #     for idx in range(len(t_org)):
        #         if block_idx!=b_org[idx]:
        #             block_idx+=1
        #             z = 0
        #         else:
                    
        #             if z ==0:   
        #                 tmp = t_org[idx]
        #             if z == 1:
        #                 tmp = t_last+ cor_samples[sample_idx,0]
        #             if z == 2:
        #                 tmp = t_last+ cor_samples[sample_idx,1]
        #             if z == 3:
        #                 tmp = t_last+ cor_samples[sample_idx,2]
        #             if z == 4:
        #                 tmp = t_last+ cor_samples[sample_idx,3]

        #         z+=1
        #         if z==5:
        #             z=0
        #             sample_idx+=1
        #         t_last = tmp
        #         t_new.append(tmp)

        for idx in range(df.shape[0]):
             # wir passen nur die Zeiten an 
            df.iloc[idx,2]= str(t_new[idx]).replace('.',',')

        print(df.head(12))
        df.to_csv(self.outputfile, sep=';', index=False)

    def create_SRTT(self):
        print(f"create SRTT file ..")
     
        # Correlation matrix
        # ES korrelieren der erste mit dem zweiten und der zweite mit dem drittn
        corr_mat= np.array([[1.0, 0.9, 0.1, 0.1, 0.1],
                            [0.9, 1.0, 0.9, 0.1, 0.1],
                            [0.1, 0.9, 1.0, 0.1, 0.1],
                            [0.1, 0.2, 0.4, 1.0, 0.1],
                            [0.1, 0.1, 0.1, 0.1, 1.0]
                            ])
        # 0-1 0.6
        # 0-2 0.3
        # 1-3 0.2
        # Compute the (upper) Cholesky decomposition matrix
        upper_chol = cholesky(corr_mat)

        # Generate 3 series of normally distributed (Gaussian) numbers
        rnd = np.random.normal(0.0, 1.0, size=(1000000, 4))

        # Finally, compute the inner product of upper_chol and rnd
        cor_samples = rnd @ upper_chol

        
        df = pd.read_csv(self.inputfile, sep = ';' )
        t_org = []
        b_org = []
       
        # wir passen nur die Zeiten an 
        for idx, row in df.iterrows():
            
            #t_org.append(float(row["Time Since Block start"]))
            t_org.append(int(row["Time Since Block start"]))
            b_org.append(int(row["BlockNumber"]))
        t_new = []
        # ersetze nun die Zeiten
        block_idx = 1
        z = 0
        t_last = 0
        cor_samples = (cor_samples - np.amin(cor_samples))/10
        print(f"the first 10 t_orgs")
        print(f"{t_org[0:10]}")
        print(f"cor_samples")
        print(f"{cor_samples[0:10]}")
        sample_idx = 0 # die Idx aus der correlierten Zufallsvariablen
        t_last = 0
        for idx in range(len(t_org)):
            if block_idx!=b_org[idx]:
                block_idx+=1
                z = 0
                #t_last = 0 # dont start at 0 for new block
            else:
                
                if z ==0:   
                    tmp = t_last + int(np.random.uniform(np.amax(cor_samples), np.amax(cor_samples)+2.1)*1000)
                if z == 1:
                    tmp = t_last+ int(cor_samples[sample_idx,0]*1000)
                if z == 2:
                    tmp = t_last+ int(cor_samples[sample_idx,1]*1000)
                if z == 3:
                    tmp = t_last+ int(cor_samples[sample_idx,2]*1000)
                if z == 4:
                    tmp = t_last+ int(cor_samples[sample_idx,3]*1000)
                if z == 5:
                    tmp = t_last+ int(cor_samples[sample_idx,4]*1000)

            z+=1
            if z==(chunk_length+1):
                z=0
                t_last = 0
                sample_idx+=1
            t_last = tmp
            t_new.append(tmp)

        for idx in range(df.shape[0]):
             # wir passen nur die Zeiten an 
            df.iloc[idx,2]= str(t_new[idx]).replace('.',',')

        print(df.head(12))
        df.to_csv(self.outputfile, sep=';', index=False)


    def create_SEQ(self, chunk_length = 3):
        
        print(f"create SEQ file")

        # Correlation matrix
        # ES korrelieren der erste mit dem zweiten und der zweite mit dem drittn
        # corr_mat= np.array([[1.0, 0.9, 0.1, 0.4, 0.1],
        #                     [0.9, 1.0, 0.9, 0.5, 0.1],
        #                     [0.1, 0.9, 1.0, 0.1, 0.4],
        #                     [0.4, 0.5, 0.1, 1.0, 0.7],
        #                     [0.1, 0.1, 0.4, 0.7, 1.0]
        #                     ])
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

        
        df = pd.read_csv(self.inputfile, sep = ';' )
        t_org = []
        b_org = []
       
        # wir passen nur die Zeiten an 
        for idx, row in df.iterrows():
            
            #t_org.append(float(row["Time Since Block start"]))
            t_org.append(float(row["Time Since Block start"].replace(',','.')))
            b_org.append(int(row["BlockNumber"]))
        t_new = []
        # ersetze nun die Zeiten
        block_idx = 1
        z = 0
        cor_samples = (cor_samples - np.amin(cor_samples))/10
        print(f"the first 10 t_orgs")
        print(f"{t_org[0:10]}")
        print(f"cor_samples")
        print(f"{cor_samples[0:10]}")
        sample_idx = 0 # die Idx aus der correlierten Zufallsvariablen
        t_last = 0
        for idx in range(len(t_org)):
            if block_idx!=b_org[idx]:
                block_idx+=1
                z = 0
                t_last = 0
        
            
            if z ==0:   
                tmp = t_last + np.random.uniform(np.amax(cor_samples), np.amax(cor_samples)+2.1)
            if z == 1:
                tmp = t_last+ cor_samples[sample_idx,0]
            if z == 2:
                tmp = t_last+ cor_samples[sample_idx,1]
            if z == 3:
                tmp = t_last+ cor_samples[sample_idx,2]
            if z == 4:
                tmp = t_last+ cor_samples[sample_idx,3]
            if z == 5:
                tmp = t_last+ cor_samples[sample_idx,4]

            z+=1
            if z==(chunk_length+1):
                z=0
                t_last = 0
                sample_idx+=1
            t_last = tmp
            t_new.append(tmp)

        for idx in range(df.shape[0]):
             # wir passen nur die Zeiten an 
            df.iloc[idx,2]= str(t_new[idx]).replace('.',',')

        print(df.head(12))
        df.to_csv(self.outputfile, sep=';', index=False)


    def create_SEQsimple(self, chunk_length = 3):
        
        print(f"create simple SEQ file")

        #use constant values for each sequence
        const_val = [0.7, 0.75, 2.65, 0.52, 0.5, 1.9, 0.4, 0.43 ]
        const_val = [2.7, 0.75, 0.65, 0.52, 0.5, 0.6, 0.4, 0.43 ]
        const_val = [[0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5],
                     [2.5, 3.5, 2.5, 3.5, 2.5, 3.5, 2.5, 3.5],
                     [0.5, 1.5, 0.5, 1.5, 0.5, 1.5, 0.5, 1.5]
                     ]
        const_val = [[0.5, 0.5, 0.5, 2.5, 0.5, 0.5, 0.5, 0.5],
                     [0.5, 0.5, 0.5, 0.5, 0.5, 2.5, 0.5, 0.5],
                     [0.5, 0.5, 2.5, 0.5, 0.5, 0.5, 2.5, 0.5]
                     ]
        const_val = [[2.5, 2.5, 2.5, 2.5, 0.5, 0.5, 0.5, 0.5],
                     [2.5, 2.5, 2.5, 2.5, 0.5, 0.5, 0.5, 0.5],
                     [2.5, 2.5, 2.5, 2.5, 0.5, 0.5, 0.5, 0.5]
                     ]
        const_val = [[0.7, 0.75, 2.65, 0.52, 0.5, 1.9, 0.4, 0.43],
                     [0.75, 2.65, 0.52, 0.5, 1.9, 0.4, 0.43, 2.7],
                     [2.65, 0.52, 0.5, 1.9, 0.4, 0.43, 2.7, 0.5]]
        const_val = [[0.7, 0.75, 2.65, 0.52, 0.5, 1.9, 0.4, 0.43],
                     [0.75, 2.65, 0.52, 0.5, 1.9, 0.4, 0.43, 0.7],
                     [2.65, 0.52, 0.5, 1.9, 0.4, 0.43, 0.7, 0.5],
                     [0.55, 0.52, 1.5, 1.9, 0.5, 0.53, 0.47, 0.52],
                     [0.65, 0.42, 0.5, 1.3, 0.45, 0.58, 0.77, 1.52]
                     ]
                     
        #const_val = [2.7, 0.75, 0.65, 0.52, 0.5, 0.6, 0.4, 0.43 ]
                        
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
#        for idx in range(len(t_org)):
        for idx in range(len(t_org)):
            if block_idx!=b_org[idx]:
                block_idx+=1
                z = 0
                t_last = 0
            const_sel = np.mod(idx,3)

            # if (const_sel==0 and (z==2 or z==5)) or (const_sel==0 and (z==1 or z==4 or z==7)) or (const_sel==0 and (z==0 or z==3 or z==6)):
            #     rnd = np.random.uniform(-0.2, 1.5)
            # else:
            #     rnd = np.random.uniform(0.1, 0.3)
            rnd = np.random.uniform(0.0, 1.7)
            const_val[const_sel] = [t *0.99 for t in const_val[const_sel]]
            t_last = t_last + const_val[const_sel][z] + rnd
            t_new.append(t_last)
            z += 1
            if z>=len(const_val[0]):
                z=0
        for idx in range(df.shape[0]):
             # wir passen nur die Zeiten an 
            df.iloc[idx,2]= str(t_new[idx]).replace('.',',')

        print(df.head(12))
        df.to_csv(self.outputfile, sep=';', index=False)


    def create_SEQdirect(self, chunk_length = 3):
        
        print(f"create SEQ file direct from handmade matrix")

        #use constant values for each sequence
        const_val = [[0.7, 0.75, 2.65, 0.52, 0.5, 1.9, 0.4, 0.43],
                     [0.75, 2.65, 0.52, 0.5, 1.9, 0.4, 0.43, 0.7],
                     [2.65, 0.52, 0.5, 1.9, 0.4, 0.43, 0.7, 0.5],
                     [0.55, 0.52, 1.5, 1.9, 0.5, 0.53, 0.47, 0.52],
                     [0.65, 0.42, 0.5, 1.3, 0.45, 0.58, 0.77, 1.52]
                     ]
                     
        #const_val = [2.7, 0.75, 0.65, 0.52, 0.5, 0.6, 0.4, 0.43 ]
                        
        df = pd.read_csv(self.inputfile, sep = ';' )
        t_org = []
        b_org = []
        for idx, row in df.iterrows():
            t_org.append(float(row["Time Since Block start"].replace(',','.')))
            b_org.append(int(row["BlockNumber"]))
        # ersetze nun die Zeiten
        block_idx = 1
        z = 0
        t_last = 0
        t_new = []
#        for idx in range(len(t_org)):
        for idx in range(len(const_val)*8):
            if block_idx!=b_org[idx]:
                block_idx+=1
                z = 0
                t_last = 0
            rnd = np.random.uniform(0.0, 1.7)
            t_last = t_last + const_val[block_idx-1][z] + rnd
            t_new.append(t_last)
            z+=1

        for idx in range(df.shape[0]):
             # wir passen nur die Zeiten an 
            df.iloc[idx,2]= str(t_new[idx]).replace('.',',')

        print(df.head(50))
        df.to_csv(self.outputfile, sep=';', index=False)



if __name__ == "__main__":
    # seed random number generator
    paradigm_name = 'SEQdirect'
    if paradigm_name == 'MST':
        inputfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\MST_Sim\\TemplateMST.csv"
        outputfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\MST_Sim\\16_PaulaHörnigREST2fertig.csv"
    if paradigm_name == 'SRTT':
        inputfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SRTT_Sim\\TemplateSRTT.csv"
        outputfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SRTT_Sim\\18_FritzGrudsinski199605261_SRTT1.csv"
    if paradigm_name == 'SEQ':
        inputfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SEQ_Sim\\TemplateSEQ.csv"
        outputfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SEQ_Sim\\34_NoraRichterFRA1fertig.csv"
    if paradigm_name == 'SEQsimple':
        inputfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SEQ_Sim\\TemplateSEQ.csv"
        outputfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SEQ_Sim\\34_SEQsimpleFRA1fertig.csv"
    if paradigm_name == 'SEQdirect':
        inputfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SEQ_Sim\\TemplateSEQ2.csv"
        outputfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SEQ_Sim\\34_SEQsimpleFRA1fertig.csv"
        
    mysim = SIM(paradigm_name, inputfile, outputfile)
    
