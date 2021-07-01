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
from helper_functions import tolist_ck, create_standard_df
from network import Network
import logging
import helper_functions
#from experiment import Experiment
from uuid import getnode as get_mac
import socket
logger = logging.getLogger(__name__)


class MST():
    def __init__(self, fullfilename = ".\\Data MST\\3Tag1_.csv", sequence_length = 5, path_output = ".\\Data_python", _id = "nox_id"):
        print(f"init of MST with: fillfilename = {fullfilename}, sequence_length = {sequence_length}, path_output = {path_output}, _id = {_id}")
        self.fullfilename = fullfilename
        base=os.path.basename(self.fullfilename)
        self.filename = os.path.splitext(base)[0]
        #logger.info(f"filename = {self.filename}")
        self.path_output = path_output
        self._id = _id
        self.filehandler = FileHandler(path_output=self.path_output, filename = self.filename, time_identifier = _id)
        self.input_df = pd.read_csv(self.fullfilename, sep = ';', engine = "python")
        self.sequence_length = sequence_length
        self.df = self.generate_standard_log_file_from_input_df(self.input_df)
        #!________________________
        #! 02.05.2020 ich habe die Namensgebung in unity veraendert ... hier ggf. Anpassung ... auch wenn man mehr als 
        #! einen einstelligen Traingingstage hat ... am besten mit string.split('_') dann arbeiten 
        self.vpn, self.day, self.paradigma = self.get_infos_from_filename(self.filename)

        #!_________________________
        self.experiment_name = "MST"
        #self.experiment = Experiment(self.experiment_name, self.vpn, self.day, self.sequence_length, self.df)

    def get_infos_from_filename(self, filename):
        # 50_Lena​Mers​MOLE3fertig
        # 50_Lena​Mers​MOLE11fertig
        # 50_Lena​Mers​MOLE21fertig ... drei gruppen
        # 50_Lena​Mers​MOLE22fertig ... drei gruppen
        # 50_Lena​Mers​MOLE23fertig ... drei gruppen
        coding_numbers = filename.split('fertig')[0][-3:]
        real_nums = []
        for num in coding_numbers:
            try:
                real_nums.append(int(num))
            except:
                pass

        day = real_nums[0]
        paradigma = 0
        if len(real_nums) > 1:
            paradigma = real_nums[1]
        #!________________________
        vpn = int(filename.split('_')[0])
        return (vpn, day, paradigma)
            
        # testing
        #self.df = self.input_df
        #self.ipi, self.hits = self.get_inter_key_intervals(self.input_df)
        #print(type(self.ipi))
        # print(type(self.ipi[0]))
        #print(self.ipi)
        #helper_functions.write_to_df_log(experiment.all_ipi_lsln, self.ipi)
        # self.sequence_length = sequence_length
        # self.ipi_cor, self.errors_per_block = self.get_inter_key_intervals_only_cor2(self.sequence_length) # nur Korrekte Sequencen
        # self.corrsq = self.estimate_correct_seqences()
        # self.corrsq_slope, self.corrsq_slope_to_max, self.corrsq_slope_1_10 = self.estimate_slope()
        

    def generate_standard_log_file_from_input_df(self, input_df):
        """ erstellt ein neues Dataframe welches dem allgemeinen Standard entspricht, damit es
            mittels der abstraktionsklasse "Experiment" verarbeitet werden kann
        """

        df = helper_functions.create_standard_df()
        df['BlockNumber'] = input_df['BlockNumber']
        df['EventNumber'] = input_df['EventNumber'] 
#        df['Time Since Block start'] = input_df['Time Since Block start']
        df['Time Since Block start'] = pd.to_numeric(input_df['Time Since Block start'].str.replace(',','.'))*1000
        df['Time Since Block start'] = df['Time Since Block start'].astype(int) #round()

        df['isHit'] = input_df['isHit']
        df['target'] = input_df['target']
        df['pressed'] = input_df['pressed']
        # the sequence column is not present in older versions
        try:
            df['sequence'] = input_df['sequence']
        except:
            df['sequence'] = 0 

        # ersetzte die Sequenznamen durch Zahlen nach mit der wichtigsten beginnend 
        #! das replacen muss von Hand erfolgen 
        #! wenn das naechste mal ein Experiment designed wird und die Zahlen nach Wichtigkeit von 1
        #! beginnend eingetragen werden dann muss man gar nichts mehr per hand anpassen
        try:
            df = df.replace('clear', 0)
        except:
            print('color code did not work')
        # passe nun die BlockNumbers an 
        df = self.generate_sequence_number(df)
        #df = self.generate_sequence_number_and_delete_incomplete_sequences(df)
        df = self.change_EventNumbers_to_inSequenceEventNumbers(df)
        df.rename({'Time Since Block start':'Time'}, axis = 'columns', inplace = True)
        df = self.adapt_Time_from_within_Block_to_within_Sequence(df)
        df.to_csv("tmp2.csv", sep = "\t")
        df = self.delete_incomplet_sequences(df)
        df = df.reset_index(drop=True)
        return df

    def delete_incomplet_sequences(self, df):
        # loesche alle unvollstaendigen Sequenzen und passe die Sequenznummer an
        s = df['SequenceNumber'].value_counts()<5
        sequences_to_delete = s[s==True].index.tolist()
        sequences_to_delete = sorted(sequences_to_delete)
        #print(sequences_to_delete)
        for num in sequences_to_delete:
            df = df[df['SequenceNumber']!= num]
        additional_subtractor = 0
        for num in sequences_to_delete:
            target = num - additional_subtractor
            df['SequenceNumber'] = df['SequenceNumber'].apply(lambda x: x if x<target else x-1)
            additional_subtractor += 1
        return df

    def adapt_Time_from_within_Block_to_within_Sequence(self, df):
        current_block = df.loc[1,'BlockNumber']
        sequence_start_time = 0
        for idx in range(df.shape[0]):
            if not df.loc[idx,'BlockNumber'] == current_block:
                current_block = df.loc[idx,'BlockNumber']
                sequence_start_time = 0
            current_time = df.loc[idx,'Time']
            df.loc[idx,'Time'] = current_time - sequence_start_time
            if df.loc[idx,'EventNumber']==self.sequence_length:
                sequence_start_time = current_time
                
        return df

    def change_EventNumbers_to_inSequenceEventNumbers(self, df):
        seq_length = self.sequence_length
        current_sequence = 1
        current_block = 1
        eventNum = 0
        for idx in range(df.shape[0]):
            if df.loc[idx,'SequenceNumber']!=current_sequence:
                # neue Sequence
                eventNum = 0
                current_sequence = df.loc[idx,'SequenceNumber']
            if df.loc[idx,'BlockNumber']!=current_block:
                # neue Sequence
                eventNum = 0
                current_block = df.loc[idx,'BlockNumber']
            if eventNum>seq_length:
                eventNum = 0
            eventNum += 1

            df.loc[idx,'EventNumber'] = eventNum
        df['EventNumber'] = df['EventNumber'].astype(int)
        return df

    def generate_sequence_number(self, df):
        # im MST File sind keine Sequence Numbers enthalten
        # da bei Fehlern die Sequenz nicht unterbrochen wird kann einfach hochgezaehlt werden
        #seq_length = df['SequenceNumber'].value_counts().unique()[0] 
        
        sequence_number = 1
        current_block = df.loc[0,'BlockNumber']
        current_sequence_element = 0
        for idx in range(df.shape[0]):
            if not df.loc[idx,'BlockNumber'] == current_block:
                new_block = True
                current_block = df.loc[idx,'BlockNumber']
                sequence_number +=1
                current_sequence_element = 0
            else:
                new_block = False

            current_sequence_element+=1

            if current_sequence_element > self.sequence_length:
                current_sequence_element = 1
                sequence_number += 1

            df.loc[idx,'SequenceNumber'] = sequence_number

        df['SequenceNumber'] = df['SequenceNumber'].astype(int)
        return df





##########################################
# from here the old code starts initially as implementation of MST allone
# now only used to test the validity of our experiment class


    def save(self):
        mydict = self.create_dict()
        self.filehandler.write(mydict)

    def create_dict(self):
        ''' generating a dictionary with all available information of this class
        '''
        corrsq = tolist_ck(self.corrsq)
        reverse_corrsq = corrsq.copy()
        reverse_corrsq.reverse()
        mydict = {
            'experiment' :              'MST',
            'ipi' :                     tolist_ck(self.ipi),
            'hits':                     tolist_ck(self.hits),
            'ipi_cor' :                 tolist_ck(self.ipi_cor),
            'sequence_length' :         self.sequence_length,
            'corrsq' :                  tolist_ck(self.corrsq),
            'corrsq_slope' :            tolist_ck(self.corrsq_slope),
            'corrsq_slope_to_max' :     tolist_ck(self.corrsq_slope_to_max), # regressionsgerade nur bis zum Maximum berechnet
            'corrsq_slope_1_10' :       tolist_ck(self.corrsq_slope_1_10), # regressionsgerade nur 1-10
            'errors_per_block'      :   tolist_ck(self.errors_per_block),
            'abs_errors'            :   sum(tolist_ck(self.errors_per_block)),
            'abs_corr_seq' :            sum(tolist_ck(self.corrsq)),
            'pos_of_first_best_block' : corrsq.index(max(corrsq)),
            'pos_of_last_best_block' :  abs((reverse_corrsq.index(max(corrsq)))-12),
            'abs_corr_sequence'     :   sum(tolist_ck(self.corrsq))
        }
        # ergaenze die Network Daten falls vorhanden
        if hasattr(self,'net'):
            net_dict = self.net.get_results_as_json()
            mydict.update(net_dict)
        return mydict

    def add_network_class(self, coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= True, is_estimate_Q= False, num_random_Q=0):
        self.net = Network(self.ipi_cor, coupling_parameter = coupling_parameter,  resolution_parameter = resolution_parameter,is_estimate_clustering= is_estimate_clustering, is_estimate_Q= is_estimate_Q, num_random_Q=num_random_Q)
        self.net.filename = self.fullfilename

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
            # logger.info(f'block number: {idx} mit blocklaenge von: {i.shape}')
            # am Anfang des blockes gibt es kein ipi fuer den ersten Tastendruck
            # hier fuege ich einen dummy des durchschnitts der Tastendruecke ein           
            ipi = np.array(np.mean(i))
            ipi = np.append(ipi, i)
            logger.info(f"idx = {idx}")
            #h = self.hits[idx]
            #logger.info(h.shape)
            #logger.info(ipi.shape)
            ipi_corr_block = []
            ipi_corr_seq = []
            # Schleife ueber das Array eines Blocks
            seq_idx = 0
            arr_idx = 0
            while arr_idx <ipi.shape[0]:
                #logger.info(f"arr_idx = {arr_idx}")
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
        error_per_block = []
        
        for idx, i in enumerate(self.ipi):
            # logger.info(f'block number: {idx} mit blocklaenge von: {i.shape}')
            # am Anfang des blockes gibt es kein ipi fuer den ersten Tastendruck
            # hier fuege ich einen dummy des durchschnitts der Tastendruecke ein           
            #ipi = np.array(np.mean(i))
            #ipi = np.append(ipi, i)


            ipi = np.asarray(i)
            h = self.hits[idx]
            ipi_corr_block = []
            errors_in_current_block = 0
            ipi_corr_seq = []
            # Schleife ueber das Array eines Blocks
            seq_idx = 0
            arr_idx = 0
            while arr_idx <ipi.shape[0]:
                #logger.info(f"arr_idx = {arr_idx}")
                if h[arr_idx]==0:
                    # abbruch der Sequenz bei einem Fehler nun neubegin
                    # setze arr_idx auf den begin der naechsten Sequenz 
                    # ggf. vor oder zurueck
                    if seq_idx < 5:
                        arr_idx = arr_idx + 5 -seq_idx
                    if seq_idx > 5:
                        arr_idx = arr_idx - (seq_idx-5)
                    errors_in_current_block +=1
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
            error_per_block.append(errors_in_current_block)
        
        return (ipi_cor, error_per_block)

    def get_inter_key_intervals(self, df):
        """ in einem numpy Array werden die inter Key intervalls gespeichert
            die Zeit zum ersten key press entfaellt 
            Liste von Arrays
        """ 
        
        blcktmp = 0
        ipi = []
        hits = []
        key_press_time = 0
        for index, row in df.iterrows():
            if row["BlockNumber"]!=blcktmp:
                if blcktmp > 0:
                    ipi.append(ipi_block_list_tmp)
                    hits.append(block_hits)
                    key_press_time = 0
                 
                # ein neuer Block
                blcktmp +=1
                ipi_block_list_tmp = []
                block_hits = []
                #block_h..its.append(row['isHit'])
                #continue # der erste in jedem Block wird nicht gespeichert
            cur_time = row["Time"]
            new_time = cur_time-key_press_time
            #logger.info(f"append index={index} {new_time}  current time = {cur_time}... old time = {key_press_time}")
            ipi_block_list_tmp.append(new_time)
            key_press_time = cur_time
            block_hits.append(row['isHit'])
        ipi.append(ipi_block_list_tmp)
        hits.append(block_hits)
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
                    #logger.info(f"In Block {blcktmp} ist Anzahl korrekter Sequenzen = {corrsq[-1]}/{num_sq[-1]}")
                corrsq.append(0)
                num_sq.append(0)
                blcktmp=row["BlockNumber"]
                num_blck_ev=row["EventNumber"]-num_blck_tmp
                num_blck_tmp=row["EventNumber"]
                durchschnitt_blck.append(num_blck_ev/30)
            # logger.info(index)
            # logger.info(row['pressed'], row['target'])
            if (row['pressed']== row['target']):
                tmpcount=tmpcount+1
            if ((index+1)%5)==0: # eine Serie komplett
                if tmpcount==5:
                    corrsq[-1]=corrsq[-1]+1
                tmpcount=0
                num_sq[-1]=num_sq[-1]+1
        #logger.info(f"{corrsq}")   
        return corrsq

    

    def estimate_slope(self):
        # slope gesamt
        if not hasattr(self,'corrsq'):
            self.estimate_correct_seqences()
        x = np.arange(len(self.corrsq))
        slope,b = np.polyfit(x, self.corrsq, 1)

        # slope 1 to 10
        slope_1_10,b = np.polyfit(x[:10], self.corrsq[:10], 1)

        # slope to max
        pos_max = self.corrsq.index(max(self.corrsq))
        x = np.arange(pos_max+1) # 1 because pos_max starts by 0 and range is not including
        slope_to_max,b = np.polyfit(x, self.corrsq[:pos_max+1], 1)

        return (slope, slope_to_max, slope_1_10)

    

if __name__ == '__main__':
    #filename = ".\\Data MST\\3Tag1_.csv"
    #filename = ".\\Data_MST_Simulation\\3Tag1_.csv"
    #mst = MST(filename)
    mac = get_mac()
    computername = socket.gethostname()
    if computername == "BigBang":
        mstfile = "G:\\Unity\\MST_JSAM\\analyse_csvs\\Data_Rogens\\MST\\17_TimQueißertREST1fertig.csv"
    if computername == "XenonBang":
        mstfile = "H:\\Unity\\MST_JSAM\\analyse_csvs\\Data_Rogens\\MST\\17_TimQueißertREST1fertig.csv"
    if computername == "Laptop-LittleBang":
        mstfile = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_MST_Grischeck\\Jung\\3_Elena​Buettner​MOLE21fertig.csv"
        outpath = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_MST_Grischeck\\tmp\\"
    mst = MST(fullfilename = mstfile, sequence_length = 5, path_output = outpath, _id = "no_id")

#    mst.save()
#    ipi_cor = mst.ipi_cor
#    ipi_norm = mst.ipi_norm
#    ipi_norm_arr = mst.ipi_norm_arr
    
    #w_norm = mst.w_norm
    #logger.info(type(mst.ipi_cor))
    #logger.info(len(mst.ipi_cor))

