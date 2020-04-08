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
from network import Network

class SEQ():
    def __init__(self, fullfilename=".\\Data_Seq_8\\_Carsten_FRA1fertig.csv", sequence_length=8, path_output=".\\Data_python", _id="nox_id"):
        self.fullfilename = fullfilename
        base = os.path.basename(self.fullfilename)
        self.filename = os.path.splitext(base)[0]
        self.color_code_dict = self.get_color_code_dict()
        #print(f"filename = {self.filename}")
        self.path_output = path_output
        self._id = _id
        self.filehandler = FileHandler(path_output=self.path_output, filename=self.filename, time_identifier=_id)
        self.df = pd.read_csv(self.fullfilename, sep=';', engine='python')
        self.ipi, self.hits, self.color = self.get_inter_key_intervals()
        #print(f"size = {len(self.ipi)}")
        self.sequence_length = sequence_length
        self.ipi_cor, self.color_cor = self.get_inter_key_intervals_only_cor2(self.sequence_length) # nur Korrekte Sequencen
        # print(self.ipi_cor)
        # print(type(self.ipi_cor))
        # print(f"after get_inter_key_interals_only_cor2 with len(ipi_cor) = {len(self.ipi_cor)}")
        #print(f'starting MST with filename : {self.filename}')
        #self.printlist3(self.ipi_cor)
        #print(self.ipi_cor)
        
        #print('now estimate_correct_sequences')
        self.paradigmen_time,self.ipi_cor_paradigmen = self.estimate_correct_seqences()
        self.paradigmen_slope = self.estimate_slope()
        #self.estimate_chunks() 
        self.my_plot()


    def my_plot(self):

        g1 = np.asarray(self.paradigmen_time[1], dtype=np.float32)
        g2 = np.asarray(self.paradigmen_time[6], dtype=np.float32)
        g3 = np.asarray(self.paradigmen_time[8], dtype=np.float32)
        g1 = ([x*2 for x in range(len(self.paradigmen_time[1]))],self.paradigmen_time[1])
        g2 = ([x*2.2 for x in range(len(self.paradigmen_time[6]))],self.paradigmen_time[6])
        g3 = (range(len(self.paradigmen_time[8])),self.paradigmen_time[8])

        data = (g1, g2, g3)
        colors = ("blue", "green", "red")
        groups = ("blue", "green", "red")

        # Create plot
        #fig = plt.figure()
        #ax = fig.add_subplot(1, 1, 1)
        fig, ax = plt.subplots()

        for data, color, group in zip(data, colors, groups):
            x, y = data
            ax.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        plt.title('Matplot scatter plot')
        plt.legend(loc=2)
        plt.show()

    def save(self):
        mydict = self.create_dict()
        self.filehandler.write(mydict)

    def create_dict(self):
        ''' generating a dictionary with all available information of this class
        '''
        mydict = {
            'experiment' :              'SEQ',
            'ipi' :                     tolist_ck(self.ipi),
            'hits':                     tolist_ck(self.hits),
            'color':                    tolist_ck(self.color),
            'ipi_cor' :                 tolist_ck(self.ipi_cor),
            'color_cor':                tolist_ck(self.color_cor),
            'sequence_length' :         self.sequence_length,
            'paradigmencorrsq' :        self.paradigmen_time,
            'corrsq_slope_b' :          tolist_ck(self.paradigmen_slope)
        }
        # ergaenze die Network Daten falls vorhanden
        if hasattr(self,'net'):
            net_dict = self.net.get_results_as_json()
            mydict.update(net_dict)
        return mydict

    def add_network_class(self, coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= True, is_estimate_Q= False, num_random_Q=0):
        #self.net = Network(self.ipi_cor, coupling_parameter = coupling_parameter,  resolution_parameter = resolution_parameter,is_estimate_clustering= is_estimate_clustering, is_estimate_Q= is_estimate_Q, num_random_Q=num_random_Q)
        self.net = Network(self.ipi_cor_paradigmen[8], coupling_parameter = coupling_parameter,  resolution_parameter = resolution_parameter,is_estimate_clustering= is_estimate_clustering, is_estimate_Q= is_estimate_Q, num_random_Q=num_random_Q)
        self.net.filename = self.fullfilename

    

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
        color_cor = []

        
        for idx, i in enumerate(self.ipi):
            # print(f'block number: {idx} mit blocklaenge von: {i.shape}')
            # am Anfang des blockes gibt es kein ipi fuer den ersten Tastendruck
            # hier fuege ich einen dummy des durchschnitts der Tastendruecke ein           
            ipi = np.asarray(i)
            h = self.hits[idx]
            color = self.color[idx]
            if sum(h) == self.sequence_length:
                # es wurde korrekt gedrueckt
                ipi_cor.append(ipi[1:])
                #print(f"get_inter_key_intervals_only_cor2 with append ipi.shape = {ipi.shape}")
                color_cor.append(color[1])
                #print(f"get_inter_key_intervals_only_cor2 with append color.shape = {color.shape}")
            else:
                pass

        return (ipi_cor, color_cor)

    def get_inter_key_intervals(self):
        """ in einem numpy Array werden die inter Key intervalls gespeichert
            die Zeit zum ersten key press entfaellt
            Liste von Arrays
        """
        blcktmp = 0
        ipi = []
        hits = []
        color = []
        key_press_time = 0

        for index, row in self.df.iterrows():
            if row["BlockNumber"] != blcktmp:
                if blcktmp > 0:
                    ipi.append(np.asarray(ipi_block_list_tmp, dtype = np.float32))
                    hits.append(np.asarray(block_hits, dtype = np.int8))
                    color.append(np.asarray(block_color, dtype = np.int8))
                    key_press_time = 0
                 
                # ein neuer Block
                blcktmp +=1
                ipi_block_list_tmp = []
                block_hits = []
                block_color = []
                #block_h..its.append(row['isHit'])
                #continue # der erste in jedem Block wird nicht gespeichert
            cur_time = float(str(row["Time Since Block start"]).replace(',','.'))
            new_time = cur_time-key_press_time
            #print(f"append index={index} {new_time}  current time = {cur_time}... old time = {key_press_time}")
            ipi_block_list_tmp.append(new_time)
            key_press_time = cur_time
            block_hits.append(row['isHit'])
            block_color.append(self.color_code_dict[row['sequence']])
            #print(f"row[sequence] = {row['sequence']}")
            #print(f"self.color_code_dict[row['sequence']]) = {self.color_code_dict[row['sequence']]}")
        ipi.append(np.asarray(ipi_block_list_tmp, dtype = np.float32))
        hits.append(np.asarray(block_hits, dtype = np.int8))
        color.append(np.asarray(block_color, dtype = np.int8))
        return (ipi, hits, color)
            
    def estimate_correct_seqences(self):
        # entsprechend der color werden Ergebnisse in diese Struktur geschrieben ... alternativ eine eigene Klasse
        paradigmen_time = self.initialize_num_dict()
        ipi_cor_paradigmen = self.initialize_num_dict()
        for idx, ipi in enumerate(self.ipi_cor):
            paradigmen_time[self.color_cor[idx]].append(sum(ipi))
            ipi_cor_paradigmen[self.color_cor[idx]].append(ipi)
        return (paradigmen_time, ipi_cor_paradigmen)

    def estimate_slope(self):
        if not hasattr(self,'paradigmen_time'):
            self.estimate_correct_seqences()
        paradigmen_slope = self.initialize_num_dict()
        for k, v in self.paradigmen_time.items():

            x = np.arange(len(v))
            if len(v) > 0:
                slope, b = np.polyfit(x, v, 1)
            else:
                slope = -999
                b = -999
            paradigmen_slope[k].append(slope)
            paradigmen_slope[k].append(b)

        return paradigmen_slope

    def get_color_code_dict(self):
        color_dict = {
            "clear":    0,
            "blue":     1,
            "black":    2,
            "cyan":     3,
            "gray":     4,
            "grey":     5,
            "green":    6,
            "magenta":  7,
            "red":      8,
            "white":    9,
            "yellow":   10
        }
        return color_dict

    def initialize_num_dict(self):
        num_dict = {
            0 :    [],
            1 :    [],
            2 :    [],
            3 :    [],
            4 :    [],
            5 :    [],
            6 :    [],
            7 :    [],
            8 :    [],
            9 :    [],
            10 :    []
        }
        return num_dict


if __name__ == '__main__':
    #filename = ".\\Data MST\\3Tag1_.csv"
    #filename = ".\\Data_MST_Simulation\\3Tag1_.csv"
    #mst = MST(filename)
    seq = SEQ(fullfilename=".\\Data_Seq_8\\_Carsten_​FRA1fertig.csv", sequence_length=8, path_output=".\\Data_python", _id="nox_id")
    seq.save()
    #seq = SEQ(fullfilename = ".\\Data MST\\3Tag1_.csv", sequence_length = 7, path_output = ".\\Data_python", _id = "no_id")
    #mst.save()
#    ipi_cor = mst.ipi_cor
#    ipi_norm = mst.ipi_norm
#    ipi_norm_arr = mst.ipi_norm_arr
    
    #w_norm = mst.w_norm
    #print(type(mst.ipi_cor))
    #print(len(mst.ipi_cor))

