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

class MST():
    def __init__(self, fullfilename = ".\\Data MST\\3Tag1_.csv", sequence_length = 7, path_output = ".\\Data_python", _id = "nox_id"):
        self.fullfilename = fullfilename
        base=os.path.basename(self.fullfilename)
        self.filename = os.path.splitext(base)[0]
        #print(f"filename = {self.filename}")
        self.path_output = path_output
        self._id = _id
        self.filehandler = FileHandler(path_output=self.path_output, filename = self.filename, time_identifier = _id)
        self.df = pd.read_csv(self.fullfilename, sep = ';' )
        self.ipi, self.hits = self.get_inter_key_intervals()
        #print(f"size = {len(self.ipi)}")
        self.sequence_length = sequence_length
        self.ipi_cor = self.get_inter_key_intervals_only_cor2(self.sequence_length) # nur Korrekte Sequencen
        #print(f'starting MST with filename : {self.filename}')
        #self.printlist3(self.ipi_cor)
        #print(self.ipi_cor)
        
        
        self.corrsq = self.estimate_correct_seqences()
        self.improvement = self.estimate_improvement()
        #self.estimate_chunks() 

    def save(self):
        mydict = self.create_dict()
        self.filehandler.write(mydict)

    def create_dict(self):
        ''' generating a dictionary with all available information of this class
        '''
        mydict = {
            'ipi' :                     tolist_ck(self.ipi),
            'hits':                     tolist_ck(self.hits),
            'ipi_cor' :                 tolist_ck(self.ipi_cor),
            'sequence_length' :         self.sequence_length,
            'corrsq' :                  tolist_ck(self.corrsq),
            'corrsq_slope' :            tolist_ck(self.improvement)
        }
        return mydict

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
            print(f"idx = {idx}")
            h = self.hits[idx]
            print(h.shape)
            print(ipi.shape)
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


    def get_inter_key_intervals_only_cor2(self, num_cor_press):
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
            #ipi = np.array(np.mean(i))
            #ipi = np.append(ipi, i)


            ipi = np.asarray(i)
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
                    key_press_time = 0
                 
                # ein neuer Block
                blcktmp +=1
                ipi_block_list_tmp = []
                block_hits = []
                #block_h..its.append(row['isHit'])
                #continue # der erste in jedem Block wird nicht gespeichert
            cur_time = float(str(row["Time Since Block start"]).replace(',','.'))
            new_time = cur_time-key_press_time
            #print(f"append index={index} {new_time}  current time = {cur_time}... old time = {key_press_time}")
            ipi_block_list_tmp.append(new_time)
            key_press_time = cur_time
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
        if not hasattr(self,'corrsq'):
            self.estimate_correct_seqences()
        x = np.arange(len(self.corrsq))
        improvement,b = np.polyfit(x, self.corrsq, 1)
        return improvement

    

if __name__ == '__main__':
    #filename = ".\\Data MST\\3Tag1_.csv"
    #filename = ".\\Data_MST_Simulation\\3Tag1_.csv"
    #mst = MST(filename)
    mst = MST(fullfilename = ".\\Data MST\\3Tag1_.csv", sequence_length = 7, path_output = ".\\Data_python", _id = "no_id")
    mst.save()
#    ipi_cor = mst.ipi_cor
#    ipi_norm = mst.ipi_norm
#    ipi_norm_arr = mst.ipi_norm_arr
    
    #w_norm = mst.w_norm
    #print(type(mst.ipi_cor))
    #print(len(mst.ipi_cor))

