import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, rename
import os, logging, time
from os.path import isfile, join
from statistics import mean, stdev
import statistics
import networkx
from filehandler import FileHandler
from helper_functions import tolist_ck, create_standard_df
import helper_functions
from network import Network
#from experiment import Experiment
logger = logging.getLogger(__name__)

class SEQ():
    def __init__(self, fullfilename=".\\Data_Seq_8\\_Carsten_FRA1fertig.csv", sequence_length=8, path_output=".\\Data_python", _id="nox_id", show_images = False, target_color = 8):        
        """ die target color markiert die Zielfarbe welche als erstes in die Liste der paradigmen kommt ...
            als letztes sollte immer die RandomSequenz

            und fuer welches das outputfile erstellt wird
            die anderen Farben werden werden zwar auch analysiert, bekommen aber im dictionary namen die 
            anders heissen als die Namen beim MST , sonst koennen wir die ergebnisse nicht\
            mit den anderen paradigmen vergleichen und die Netzwerkklasse muesste auch umgeschrieben werde

            um eine bestmoegliche Vereinbarkeit von unterschiedlichen Paradigmen zu ermoeglichen sollte
            am ende nicht in dictionaries gespeichert werden sondern in Listen
            der erste eintrag ist dann die Zielfarbe bzw. im MST gibt es nur einen Listeneintrag
            im SRTT gaebe es dann 2 Listeneintraege

            # 01.05.2020 neue Idee ... um alles so einheitlich wie moeglich zu machen sollte diese Klasse nur ein
            #                          neues dataframe anlegen das dann allgemeingueltig fuer alle Experimente
            #                          identisch ist und das dann der Klasse Experiment zur Verfuegung gestellt 
            #                          wird. Diese Klasse berechnet dann alle notwendigen und moeglichen Parameter.

            INPUT-LOG-FILE
            BlockNumber;    EventNumber;    Time Since Block start; isHit;  target; pressed;    sequence
            1;              1;              4,211823;               0;      3;      2;          blue
            1;              2;              4,916992;               1;      4;      4;          blue
            1;              3;              5,841339;               0;      2;      3;          blue
            1;              4;              6,983551;               1;      1;      1;          blue
            1;              5;              8,57785;                1;      3;      3;          blue
            1;              6;              9,028168;               1;      2;      2;          blue
            1;              7;              9,610718;               1;      4;      4;          blue
            1;              8;              9,974152;               1;      1;      1;          blue
            2;              9;              4,085938;               1;      2;      2;          green
            2;              10              ;4,741425;              1;      1;      1;          green
            2;              11              ;5,252991;              1;      4;      4;          green
            2;              12              ;5,817474;              1;      1;      1;          green
            2;              13              ;6,494324;              1;      3;      3;          green
            2;              14              ;6,921967;              1;      2;      2;          green
            2;              15              ;7,720825;              1;      4;      4;          green
            2;              16              ;8,553619;              1;      3;      3;          green
            3;              17              ;4,288727;              1;      2;      2;          red
            3;              18              ;4,866821;              1;      3;      3;          red
            3;              19              ;5,340302;              1;      1;      1;          red


            # Anmerkung ... BlockNumber ist hier offensichtlich die Sequenznummer ... pffff 


            OUTPUT-PANDAS-FILE
            BlockNumber     SequenceNumber; EventNumber;    Time Since Block start; isHit;  target; pressed;    sequence
            1;              1;              1;              4,211823;               0;      3;      2;          1
            1;              1;              2;              4,916992;               1;      4;      4;          1
            1;              1;              3;              5,841339;               0;      2;      3;          1
            1;              1;              4;              6,983551;               1;      1;      1;          1
            1;              1;              5;              8,57785;                1;      3;      3;          1
            1;              1;              6;              9,028168;               1;      2;      2;          1
            1;              1;              7;              9,610718;               1;      4;      4;          1
            1;              1;              8;              9,974152;               1;      1;      1;          1
            1;              1;              9;              4,085938;               1;      2;      2;          2
            1;              2;              10;             4,741425;               1;      1;      1;          2
            1;              2;              11;             5,252991;               1;      4;      4;          2
            1;              2;              12;             5,817474;               1;      1;      1;          2
            1;              2;              13;             6,494324;               1;      3;      3;          2
            1;              2;              14;             6,921967;               1;      2;      2;          2
            1;              2;              15;             7,720825;               1;      4;      4;          2
            1;              2;              16;             8,553619;               1;      3;      3;          2
            1;              3;              17;             4,288727;               1;      2;      2;          0
            1;              3;              18;             4,866821;               1;      3;      3;          0
            1;              3;              19;             5,340302;               1;      1;      1;          0


            # Anmerkung ... BlockNumber ist schwierig da wenn moeglich die gleichen Anzahlen an Sequenzen pro paradigma pro block vorkommen sollte
        """


        logger.info("Initialising class SEQ ...")
        self.fullfilename = fullfilename
        base = os.path.basename(self.fullfilename)
        self.filename = os.path.splitext(base)[0]
        self.color_code_dict = self.get_color_code_dict()
        #print(f"filename = {self.filename}")
        self.path_output = path_output
        self._id = _id
        self.filehandler = FileHandler(path_output=self.path_output, filename=self.filename, time_identifier=_id)
        self.input_df = pd.read_csv(self.fullfilename, sep=';', engine='python')
        
        self.sequence_length = 8
        self.df = self.generate_standard_log_file_from_input_df(self.input_df)
        #!________________________
        #! 02.05.2020 ich habe die Namensgebung in unity veraendert ... hier ggf. Anpassung ... auch wenn man mehr als 
        #! einen einstelligen Traingingstage hat ... am besten mit string.split('_') dann arbeiten 
        #print(self.filename)
        try:
            self.day = int(self.filename.split('fertig')[0][-1])
        except:
            print(f"invalid file name for extracting the day with: {self.filename} ... error in SEQ.init")
            raise ValueError("invalid Filename")
        #!________________________
        try:
            self.vpn = int(self.filename.split('_')[0])
        except:
            print(f"invalid file name for extracting the VPN with: {self.filename} ... error in SEQ.init")
            raise ValueError("invalid Filename")
        #!_________________________
        self.experiment_name = "SEQ"
        #print(self.df.head())
        
        # self.ipi, self.hits, self.color = self.get_inter_key_intervals()
        # self.sequence_length = sequence_length
        # self.ipi_cor, self.color_cor = self.get_inter_key_intervals_only_cor2(self.sequence_length) # nur Korrekte Sequencen
        # self.target_col = target_color
        # self.color_dict = self.get_color_code_dict()
        # self.cor_seq_time_paradigmen,self.ipi_cor_paradigmen = self.estimate_color_dependent_dicts(self.ipi_cor)
        # self.paradigmen_slope = self.estimate_slope()

        
        #self.estimate_chunks() 
        if show_images:
            self.my_plot()

    def generate_standard_log_file_from_input_df(self, input_df):
        """ erstellt ein neues Dataframe welches dem allgemeinen Standard entspricht, damit es
            mittels der abstraktionsklasse "Experiment" verarbeitet werden kann
        """

        df = helper_functions.create_standard_df()
        df['SequenceNumber'] = input_df['BlockNumber'] # die BlockNumbers sind fals benannt in dieser Klasse
        df['EventNumber'] = input_df['EventNumber']

        
        df['Time Since Block start'] = pd.to_numeric(input_df['Time Since Block start'].str.replace(',','.'))*1000
        df['Time Since Block start'] = df['Time Since Block start'].astype(int) #round()
        
        df['isHit'] = input_df['isHit']
        df['target'] = input_df['target']
        df['pressed'] = input_df['pressed']
        df['sequence'] = input_df['sequence']
        # ersetzte die Sequenznamen durch Zahlen nach mit der wichtigsten beginnend 
        #! das replacen muss von Hand erfolgen 
        #! wenn das naechste mal ein Experiment designed wird und die Zahlen nach Wichtigkeit von 0
        #! beginnend eingetragen werden dann muss man gar nichts mehr per hand anpassen
        try:
            df = df.replace('green', 2)
            df = df.replace('blue', 1)
            df = df.replace('red', 0)
        except:
            print('color code did not work')
        # passe nun die BlockNumbers an 
        df = self.change_EventNumbers_to_inSequenceEventNumbers(df)
        df.rename({'Time Since Block start':'Time'}, axis = 'columns', inplace = True)
    
        df = self.subtract_200ms_initial_color_showing_time(df)
        df = self.generate_block_number2(df)
        df['BlockNumber'] = df['BlockNumber'].astype(int)

        return df

    def subtract_200ms_initial_color_showing_time(self, df):
        # es wird anfangs ein Farbbild gezeigt, das die kommende Sequence codiert
        # dieses wird fuer 2000 ms gezeigt, diese Zahl subtrahiere ich hier
        for idx in range(df.shape[0]):
            if df.loc[idx,'EventNumber']==1:
                df.loc[idx,'Time'] = df.loc[idx,'Time'] - 2000
        return df

    def change_EventNumbers_to_inSequenceEventNumbers(self, df):
        #seq_length = df['SequenceNumber'].value_counts().unique()[0]
        for idx in range(df.shape[0]):
            m = df.loc[idx,'EventNumber'] % self.sequence_length 
            if m==0:
                m=self.sequence_length
            df.loc[idx,'EventNumber'] = m
        df['EventNumber'] = df['EventNumber'].astype(int)
        return df


    def generate_block_number2(self, df):
        block_series = df['BlockNumber'] # nur als Platzhalter
        # es sollen 10 bloecke sein und in jedem Block soll
        # eine gleiche Anzahl an Sequenzen aller Paradigmata sein
        # die Blockzahl muss nicht zwingend aufsteigend sein um diese Bedingung zu erfuellen
        # diese Methode muss NICHT manuell angepasst werden wenn wir ein neues Experiment haben solange oben die Colorcodes gesetzt sind
        
        num_seq = df['sequence'].nunique()
        num_seq_occ = []
        for i in range(num_seq):
            # anzahl des Vorkommens einer jeden zeile
            num_seq_occ.append(int(round((df.sequence== i).sum())))
        # anzahl der Sequenzen die in einen Block sollen
        num_seq_in_block =[]
        num_seq_in_blocks =[]
        for i in range(num_seq):
            absolute = num_seq_occ[i]/self.sequence_length
            num_in_block, rest = divmod(absolute,10)
            num_seq_in_block = [int(num_in_block)] *10
            #print(f'rest = {rest}')
            rest = int(rest)
            for i in range(rest):
                num_seq_in_block[i] += 1
            num_seq_in_blocks.append(num_seq_in_block)
        # num_seq_in_block hat nun die folgende Struktur
        # [
        #   [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0],
        #   [5.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0],
        #   [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0],
        # ]
        # nun laufen wir die Sequenzen ab und ordnen die Bloecke zu den Sequenzen 
        # dies muessen entsprechend nicht aufsteigend sein
        #print(df)
        #print(num_seq_in_blocks)
        remaining_sequences_in_blocks = num_seq_in_blocks # dieser soll runter zaehlen
        block_number_list = [int(0),int(0),int(0)] # der angibt in welchem Block wir uns befinden
        for idx in range(0,df.shape[0],self.sequence_length):
            
            seq = df.loc[idx,'sequence']
            block_number = block_number_list[seq]
            remaining = remaining_sequences_in_blocks[seq][block_number]

            for i in range(self.sequence_length):
                df.loc[idx+i,'BlockNumber'] = block_number +1

            remaining_sequences_in_blocks[seq][block_number] -= 1
            if remaining_sequences_in_blocks[seq][block_number] == 0:
                # dann ruecke eins weiter
                block_number_list[seq] +=1
            
            # das die blockliste erschoepft ist muessen wir nicht abfragen
            # da diese nach unserer oberern berechnung genau aufgehen sollt
        return df  
 


    def my_plot(self):

        g1 = np.asarray(self.cor_seq_time_paradigmen[1], dtype=np.float32)
        g2 = np.asarray(self.cor_seq_time_paradigmen[6], dtype=np.float32)
        g3 = np.asarray(self.cor_seq_time_paradigmen[8], dtype=np.float32)
        g1 = ([x*2 for x in range(len(self.cor_seq_time_paradigmen[1]))],self.cor_seq_time_paradigmen[1])
        g2 = ([x*2.2 for x in range(len(self.cor_seq_time_paradigmen[6]))],self.cor_seq_time_paradigmen[6])
        g3 = (range(len(self.cor_seq_time_paradigmen[8])),self.cor_seq_time_paradigmen[8])

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
        # for seqence in self.color
        dict_list = []
        # mydict = {
        #     "SEQUENCES"           :       dict_list
        # }
        ipi_all = tolist_ck(self.ipi)
        hits_all = tolist_ck(self.hits)
        color_all = tolist_ck(self.color)
        ipi_cor_all = tolist_ck(self.ipi_cor)
        color_cor_all = tolist_ck(self.color_cor)
        ipi_cor = []
        ipi_cor_blue = []
        ipi_cor_green = []
        
        for idx, ipi in enumerate(ipi_cor_all):
            color_code = color_cor_all[idx]
            if color_code==self.target_col:
                ipi_cor.append(ipi)
            else:
                color_string = list(self.color_dict.keys())[color_code]
                if color_code == 1:
                    ipi_cor_blue.append(ipi)
                if color_code == 6:
                    ipi_cor_green.append(ipi)

        ipi = []
        ipi_blue = []
        ipi_green = []
        hits = []
        hits_blue = []
        hits_green = []
        color_list = list(self.color_dict.keys())
        
        for idx, ipix in enumerate(ipi_all):
            color_code = color_all[idx][0]
            
            if color_code==self.target_col:
                ipi.append(ipix)
                hits.append(hits_all[idx])
            else:
                
                color_string = color_list[color_code]
                if color_code == 1:
                    ipi_blue.append(ipix)
                    hits_blue.append(hits_all[idx])
                if color_code == 6:
                    ipi_green.append(ipix)
                    hits_green.append(hits_all[idx])
                    
        paradigmen_slope = tolist_ck(self.paradigmen_slope)
        uniquecolorlist = list(set(tolist_ck(self.color_cor)))
#        for c in uniquecolorlist:
        mydict = {
            'experiment'            :   'SEQ',
            'ipi_all'               :   tolist_ck(self.ipi),
            'hits_all'              :   tolist_ck(self.hits),
            'color_all'             :   tolist_ck(self.color),
            'ipi'                   :   ipi, # die ipis der Zielfarbe
            'hits'                  :   hits,
            'ipi_blue'              :   ipi_blue,
            'hits_blue'             :   hits_blue,
            'ipi_green'             :   ipi_green,
            'hits_green'            :   hits_green,
            'ipi_cor'               :   ipi_cor, # Zielfarbe
            'ipi_cor_blue'          :   ipi_cor_blue,
            'ipi_cor_green'         :   ipi_cor_green,
            'color_cor'             :   tolist_ck(self.color_cor),
            'sequence_length'       :   tolist_ck(self.sequence_length),
            'paradigmencorrsq_time' :   tolist_ck(self.cor_seq_time_paradigmen),
            #'paradigmen_cor_seq'    :   tolist_ck(self.ipi_cor_paradigmen), # die ipi_cor nach paradigmen (1...10)
            'cor_seq_per_block'     :   0, # aufteilung in 60 sek bloecke und zaehlen der Anzahl der korrekten Sequenzen pro block daraus slope
            'err_seq_per_block'            :   0, # aufteilung in 60 sek bloecke und zaehlen der Anzahl der korrekten Sequenzen pro block daraus slope
            'cor_seq_per_block_slope'            :   0, # aufteilung in 60 sek bloecke und zaehlen der Anzahl der korrekten Sequenzen pro block daraus slope
            'err_seq_per_block_slope'            :   0, # aufteilung in 60 sek bloecke und zaehlen der Anzahl der korrekten Sequenzen pro block daraus slope
            'cor_seq_per_block_slope_to_max'    :    0,
            'cor_seq_v_slope'            :   tolist_ck(paradigmen_slope[self.target_col][0]), # slope der Geschwindigkeit der Sequenzen
            'cor_seq_v_slope_blue'       :   tolist_ck(paradigmen_slope[1][0]),
            'cor_seq_v_slope_green'      :   tolist_ck(paradigmen_slope[6][0]),
            'cor_seq_v_slope_b'        :   tolist_ck(self.paradigmen_slope),
            'err_seq_abs'            :   len(tolist_ck(self.ipi))-len(tolist_ck(self.ipi_cor)),
            'cor_seq_abs'          :   len(tolist_ck(self.ipi_cor))
        }
  #      dict_list.append()
        # MST
        # mydict = {
        #     'experiment' :              'MST',
        #     'ipi' :                     tolist_ck(self.ipi),
        #     'hits':                     tolist_ck(self.hits),
        #     'ipi_cor' :                 tolist_ck(self.ipi_cor),
        #     'sequence_length' :         self.sequence_length,
        #     'corrsq' :                  tolist_ck(self.corrsq),
        #     'corrsq_slope' :            tolist_ck(self.corrsq_slope),
        #     'corrsq_slope_to_max' :     tolist_ck(self.corrsq_slope_to_max), # regressionsgerade nur bis zum Maximum berechnet
        #     'corrsq_slope_1_10' :       tolist_ck(self.corrsq_slope_1_10), # regressionsgerade nur 1-10
        #     'errors_per_block'      :   tolist_ck(self.errors_per_block),
        #     'abs_errors'            :   sum(tolist_ck(self.errors_per_block)),
        #     'abs_corr_seq' :            sum(tolist_ck(self.corrsq)),
        #     'pos_of_first_best_block' : corrsq.index(max(corrsq)),
        #     'pos_of_last_best_block' :  abs((reverse_corrsq.index(max(corrsq)))-12),
        #     'abs_corr_sequence'     :   sum(tolist_ck(self.corrsq))
        # }



        # ergaenze die Network Daten falls vorhanden
        if hasattr(self,'net'):
            net_dict = self.net.get_results_as_json()
            mydict.update(net_dict)
        return mydict






    def add_network_class(self, coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= True, is_estimate_Q= False, num_random_Q=0):
        #self.net = Network(self.ipi_cor, coupling_parameter = coupling_parameter,  resolution_parameter = resolution_parameter,is_estimate_clustering= is_estimate_clustering, is_estimate_Q= is_estimate_Q, num_random_Q=num_random_Q)
        self.net = Network(self.ipi_cor_paradigmen[self.target_col], coupling_parameter = coupling_parameter,  resolution_parameter = resolution_parameter,is_estimate_clustering= is_estimate_clustering, is_estimate_Q= is_estimate_Q, num_random_Q=num_random_Q)
        self.net.filename = self.fullfilename

    

    def get_inter_key_intervals_only_cor2(self, num_cor_press):
        """reduziert die ipi (inter Press Intervals) auf nur die korrekten Druecker
            dazu werden ausschliesslich korrekte Sequenzen herangezogen
            
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
                # es wurde eine Sequenz korrekt gedrueckt
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
            
    def estimate_color_dependent_dicts(self, ipi):
        # entsprechend der color werden Ergebnisse in diese Struktur geschrieben ... alternativ eine eigene Klasse
        # ipi kann hier alle ipis sein oder auch nur die correkten
        seq_time_paradigmen = self.initialize_num_dict()
        ipi_paradigmen = self.initialize_num_dict()
        for idx, ipi in enumerate(ipi):
            seq_time_paradigmen[self.color_cor[idx]].append(sum(ipi))
            ipi_paradigmen[self.color_cor[idx]].append(ipi)
        return (seq_time_paradigmen, ipi_paradigmen)

    def estimate_slope(self):
        if not hasattr(self,'cor_seq_time_paradigmen'):
            self.estimate_color_dependent_dicts()
        paradigmen_slope = self.initialize_num_dict()
        for k, v in self.cor_seq_time_paradigmen.items():

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

    filename= ".\\Data_Seq_8\\_Carsten_​FRA1fertig.csv"
    filename= ".\\Data_Rogens\\SEQ\\33_StevenHerrmannFRA2fertig.csv"

    seq = SEQ(fullfilename=filename, sequence_length=8, path_output=".\\Data_python", _id="nox_id")
    
    #seq.save()
    #seq = SEQ(fullfilename = ".\\Data MST\\3Tag1_.csv", sequence_length = 7, path_output = ".\\Data_python", _id = "no_id")
    #mst.save()
#    ipi_cor = mst.ipi_cor
#    ipi_norm = mst.ipi_norm
#    ipi_norm_arr = mst.ipi_norm_arr
    
    #w_norm = mst.w_norm
    #print(type(mst.ipi_cor))
    #print(len(mst.ipi_cor))

