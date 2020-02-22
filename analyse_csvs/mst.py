import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, rename
from os.path import isfile, join
from statistics import mean, stdev
import statistics

class MST():
    def __init__(self, filename):
        self.df = pd.read_csv(filename, sep = ';' )
        self.ipi, self.hits = self.get_inter_key_intervals()
        #print(f"size = {len(self.ipi)}")
        self.ipi_cor = self.get_inter_key_intervals_only_cor(10) # nur Korrekte Sequencen

        #self.printlist3(self.ipi_cor)
        print(self.ipi_cor)
        self.estimate_chunks()
        
        self.corrsq = self.estimate_correct_seqences()
        self.improvement = self.estimate_improvement()
        #self.estimate_chunks()


    def estimate_chunks(self):
        ipi = self.ipi_cor
        self.ipi_arr = self.convert_to_array2D(self.ipi)
        m, std = self.get_ipi_mean_arr(self.ipi_arr)

        self.ipi_norm = self.get_normalized_ipi(ipi, m, std)
        self.ipi_norm_arr = self.convert_to_array2D(self.ipi_norm)
        self.w = self.get_simple_weights(self.ipi_norm_arr)
        #self.w_norm = self.get_normalized_weigths(self.ipi_norm)
            
    def convert_to_array2D(self, list3):
        y = []
        for block in x:
             for sequence in block:
                 y.append(sequence)
        y_mat = np.stack(y)
        return y_mat # array der dimension N x M   (N anzahl der korrekten Sequenzen, M Anzahl der Elemente pro sequenz)
        
    def get_simple_weights(ipi_arr):
        # estimates similarities in IKIs 
        w = []
        for i in range(ipi_arr.shape[0]):
            d = np.zeros((10,10))
            m = max(ipi_arr[i,:])
            for j in range(ipi_arr.shape[1]-1):
                d[j,j]=0.03
                d[j,j+1]=(m-abs(ipi_arr[i,j]-ipi_arr[i,j+1]))/m
            w.append(d)
    
    def get_normalized_weigths(self, ipi):
        w = []
        wm = [] #np.zeros(10,10)
        w2 = []
        for block in ipi:
            w_block = []
            for sequence in block:
                w_seq = []
                w_mat = np.zeros((10,10))
                for k in range(1,len(sequence)):
                    w_seq.append(abs(sequence[k]-sequence[k-1]))
                    
                maximum = max(w_seq)
                w_seq = [(maximum-i)/maximum for i in w_seq]
                for index,i in enumerate(w_seq):
                    w_mat[index,index+1] = (maximum-w_seq[i])/maximum
                
                w_block.append(w_seq)
            w.append(w_block)

        for x in wm[:-1]:
            for idx in range(x.shape[0]):
                x[idx,idx]=x[idx,idx+1]


        return w

    def get_ipi_mean_arr(self, ipi):
        mean_arr = ipi.mean(axis=0)
        std_arr = ipi.std(axis=0)

        return (mean_arr, std_arr)        
    
    def get_mean_list3(self, ipi):
        mean_list = []
        for block in ipi:
            for sequence in block:
                mean_list.append(sum(sequence) / len(sequence))
        m = sum(mean_list) / len(mean_list)
        std = stdev(mean_list)
        return (m, std)        

    def get_normalized_ipi(self, ipi, m, std):

        ipi_new = []
        for block in ipi:
            block_new = []
            for sequence in block:
                keep = True
                for idx, p in enumerate(sequence):
                    if p>m[idx]+std[idx]*3 or p<m[idx]-std[idx]*3 :
                        keep = False
                if keep:
                    block_new.append(sequence)
            ipi_new.append(block_new)
        return ipi_new

    def printlist3(self, list3):
        for idx, x in enumerate(list3):
            print(f"Block nummer: {idx+1}")
            for y in x:
                print(y)
 #               print(type(y[0]))


    def get_inter_key_intervals_only_cor(self, num_cor_press):
        """reduziert die ipi (inter Press Intervals) auf nur die korrekten Druecker
            dazu werden ausschliesslich korrekte Sequenzen herangezogen
            Wir behaupten, dass man nicht mehr als 10 druecker chunkt
            Daher ketten wir maximal 2 aneinander
            Nachher die anhehaengte wird gedoppelt
            hier muessen wir nacher darauf achten, dass wir keine Sequenzen nehmen die nur in der 2. 
            Sequenz stattfinden da sie dann doppelte gezaehlt waeren
            num_cor_press definiert wie viele korrekte vorhanden sein muessen um eine komplette "Sequenz" zu definieren
        """        
        ipi_cor = []

        
        for idx, i in enumerate(self.ipi):
            # print(f'block number: {idx} mit blocklaenge von: {i.shape}')
            # am Anfang des blockes gibt es kein ipi fuer den ersten Tastendruck
            # hier fuege ich einen dummy des durchschnitts der Tastendruecke ein           
            ipi = np.array(np.mean(i))
            ipi = np.append(ipi, i)

            h = self.hits[idx]
            ipi_corr_block = []
            ipi_corr_seq = []
            # Schleife ueber das Array eines Blocks
            seq_idx = 0
            arr_idx = 0
            while arr_idx <ipi.shape[0]:
                #print(f"arr_idx = {arr_idx}")
                if h[arr_idx]==0:
                    # abbruch der Sequenz bei einem Fehler nun neubegin
                    # setze arr_idx auf den begin der naechsten Sequenz 
                    # ggf. vor oder zurueck
                    if seq_idx < 5:
                        arr_idx = arr_idx + 5 -seq_idx
                    if seq_idx > 5:
                        arr_idx = arr_idx - (seq_idx-5)
                    # loesche den aktuellen Sequenzblock
                    ipi_corr_seq = []
                    # setze den aktuellen Sequenzmarker zureck
                    seq_idx = 0
                else:
                    # es wurde korrekt gedrueckt
                    ipi_corr_seq.append(ipi[arr_idx])
                    seq_idx+= 1
                    arr_idx+= 1

                if seq_idx==num_cor_press:
                    # wenn diese Stelle erreicht wird dann war die Sequenz bis hierher erfolgreich
                    # und wir speichern die Sequenz ab
                    ipi_corr_block.append(ipi_corr_seq)
                    ipi_corr_seq = []
                    seq_idx = 0
            ipi_cor.append(ipi_corr_block) # liste einer liste einer Liste
        return ipi_cor

    def get_inter_key_intervals(self):
        """ in einem numpy Array werden die inter Key intervalls gespeichert
            die Zeit zum ersten key press entfaellt 
            Liste von Arrays
        """ 
        blcktmp = 0
        ipi = []
        hits = []
        key_press_time = 0
        for index, row in self.df.iterrows():
            if row["BlockNumber"]!=blcktmp:
                if blcktmp > 0:
                    ipi.append(np.asarray(ipi_block_list_tmp, dtype = np.float32))
                    hits.append(np.asarray(block_hits, dtype = np.int8))
                # ein neuer Block
                blcktmp +=1
                ipi_block_list_tmp = []
                key_press_time = float(row["Time Since Block start"].replace(',','.')) # dummy 
                block_hits = []
                block_hits.append(row['isHit'])
                continue # der erste in jedem Block wird nicht gespeichert
                
            ipi_block_list_tmp.append(float(row["Time Since Block start"].replace(',','.'))-key_press_time)
            key_press_time = float(row["Time Since Block start"].replace(',','.'))
            block_hits.append(row['isHit'])
        ipi.append(np.asarray(ipi_block_list_tmp, dtype = np.float32))
        hits.append(np.asarray(block_hits, dtype = np.int8))
        return (ipi, hits)
            

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

