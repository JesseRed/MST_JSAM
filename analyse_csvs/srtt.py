import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, rename
from os.path import isfile, join
from statistics import mean, stdev
import statistics
import networkx
import time

class SRTT():
    def __init__(self, filename):
        self.df = pd.read_csv(filename, sep = '\t' )
        self.ipi_cor = self.get_ipi_from_correct_non_random_sequences()

        #self.ipi, self.hits = self.get_inter_key_intervals()
        #print(f"size = {len(self.ipi)}")
        #elf.ipi_cor = self.get_inter_key_intervals_only_cor(10) # nur Korrekte Sequencen

        #self.printlist3(self.ipi_cor)
        #print(self.ipi_cor)
        
        
        #self.corrsq = self.estimate_correct_seqences()
        #self.improvement = self.estimate_improvement()
        #self.estimate_chunks() 
    def get_ipi_from_correct_non_random_sequences(self):
       # loesche die random
        df = dfx.copy()
        df =df[df['type']=='fixed']
        cur_seq = 0
        ipi_cor = []
        rts_cor = []
        num_miss =1
        rts = []
        ipi = [] # temporaeres speichern einer Sequenz 
        print(df.columns)
        for idx,row in df.iterrows():
            rts.append(row['RT_1'])
            if row['sequ.']>1:
                ipi.append(row['time']-old_time)
            old_time = row['time']
            if row['trial']==12: # sequenz fertig
                if num_miss ==0: # wir speichern nur correcte Sequenzen
                    ipi_cor.append(ipi)
                    rts_cor.append(rts)
                rts = []
                ipi = []
                num_miss = 0
        return (rts_cor, ipi_cor)
        

    def estimate_correct_seqences(self):
        corrsq=[]
        tmpcount=0
        num_sq=[]
        blcktmp=-1
        num_blck_ev=0
        num_blck_tmp=0
        durchschnitt_blck=[]
        for index, row in self.df.iterrows():
            if row["BlockNumber"]!=blcktmp:
                if blcktmp>0:
                    pass
                    #print(f"In Block {blcktmp} ist Anzahl korrekter Sequenzen = {corrsq[-1]}/{num_sq[-1]}")
                corrsq.append(0)
                num_sq.append(0)
                blcktmp=row["BlockNumber"]
                num_blck_ev=row["EventNumber"]-num_blck_tmp
                num_blck_tmp=row["EventNumber"]
                durchschnitt_blck.append(num_blck_ev/30)
            # print(index)
            # print(row['pressed'], row['target'])
            if (row['pressed']== row['target']):
                tmpcount=tmpcount+1
            if ((index+1)%5)==0: # eine Serie komplett
                if tmpcount==5:
                    corrsq[-1]=corrsq[-1]+1
                tmpcount=0
                num_sq[-1]=num_sq[-1]+1
        #print(f"{corrsq}")   
        return corrsq

    def estimate_improvement(self):
        X = [1,2,3,4,5,6,7,8,9,10,11,12]
        if not hasattr(self,'corrsq'):
            self.estimate_correct_seqences()
        improvement,b = np.polyfit(X, self.corrsq, 1)
        return improvement
        

if __name__ == '__main__':
    filename = ".\\Data MST\\3Tag1_.csv"
    mst = MST(filename)
    ipi_cor = mst.ipi_cor
    ipi_norm = mst.ipi_norm
    ipi_norm_arr = mst.ipi_norm_arr
    
    #w_norm = mst.w_norm
    #print(type(mst.ipi_cor))
    #print(len(mst.ipi_cor))

