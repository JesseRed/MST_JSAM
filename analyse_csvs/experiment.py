import numpy as np
import pandas as pd
import logging, os, json
from network import Network
import matplotlib.pyplot as plt
import socket
from mst import MST
from seq import SEQ
from srtt import SRTT
import pickle
#from debug import Debug
import exp_est # hier sind alle Funktionen die etwas berechnenen fuer die ExperimentKlasse
##################################
### logging 
# log_level = logging.INFO
# data_base_log_level = logging.INFO

# logging.basicConfig(level=log_level, filename='logfile.log', 
#     format ='', #format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s',
#     filemode='w')
logger = logging.getLogger(__name__)
#db_logger = logging.getLogger('sqlalchemy')
#db_logger.addHandler(logger)
#db_logger.setLevel(data_base_log_level)
##################################

class Experiment:
    """alles sind listen 
    # wenn nicht explizit erwaehnt dann immer am ende als Liste der Sequenz
    # 1. Listenebene Paradigma (z.B. random vs. non random)
    # 2. Listenebene Sequenz []
    # 3. Ebene dann die eigentliche Zahl

    #! number: n z.B. sequence length
        8  # python integer
        
    #! list of numbers: ln  z.B. cor_seq_abs
        [20, 12, 8] # list python integers (mostly list across paradigms)        

    #! list of lists of numbers: lln  z.B. cor_seq_per_block
        [                               # list of ...  (mostly paradigms)
            [6 17 18 19 20 22 22 24 25],# Paradigma 1 | list number of correct sequences per block 
            [9 10 12 13 20 20 22 24 27] # Paradigma 2 | list number of correct sequences per block 
        ]

    #! list of lists of lists of numbers:  z.B. ipi_cor
        [                               # list of lists of lists of numbers ...   (mostly paradigms at the first level)
            [                           # list of lists of numbers
                [1.1, 1.2, 0.9, 0.8],   #  Paradigma 1  | list of numbers (z.B. interpres intervalls)
                [1.1, 1.2, 0.9, 0.8]    #  Paradigma 1  | list of numbers (z.B. interpres intervalls)
            ],                          
            [
                [1.1, 1.2, 0.9, 0.8],   #  Paradigma 2  | list of numbers (z.B. interpres intervalls)
                [1.1, 1.2, 0.9, 0.8]    #  Paradigma 2  | list of numbers (z.B. interpres intervalls)
            ]

        ]


        hinter jeder variablen steht die codierung 
        l = liste 
        n = number
        p = paradigma
        s = sequenz
        b = block
        Bsp.: lplsln  ... liste der paradimgen mit listen der seqenzen mit listen von numbers
        Bsp.: lplblsln waere eine liste ueber paradigmen liste ueber bloecke liste uever sequenzen liste von numbers 
        Bsp.: lplbn ... liste von paradigmen von liste von bloecken mit einer nummer pro block (liste von listen von nummern)

        variablenbenennung 
        1. correct, error oder all
        2. was wir speichern (ipi, hits, time, velocity)
        3. optionaler parameter der eine zusatzberechnung kennzeichnet z.B. slope
        z.B. cor_ipi_lplsln         ... correcte inter-press-intervalle als liste ueber die paradigmen liste ueber die sequenzen liste der numbers
        z.B. err_ipi_seqsum_lpln      ... fehlerhafte ipis als summe ueber Sequencen als liste von gesamtzeiten jeder Sequenz fuer jedes Paradigma
        
        #?____________________________________________________________________________________________________________________________________
        #? INPUT DAtaframe
        #! alle Nummerierungen beginnen mit ausser die sequence die mit 0 als wichtigste beginnt
        BlockNumber ....Kodierung der Bloecke ... beim MST durch Pausen unterbrochen, beim Seq keine Pausen
                            daher nachtraegliche Aufteilung in 10 Bloecke mit gleich Verteilung der unterschiedlichen Paradigmen 
                            (unterschiedlichen Sequenzen die gelernt werden sollen) daher #!BlockNumbers nicht zuwingend aufsteigend
        SequenceNumber. Aufsteigende Kodierung der Sequenzen, jedes Element der Sequenz hat die gleiche Nummer
                            Sobald eine neue Sequenz beginnt erheoht sich die Zahl um eins
                            #! unvollstaendige Sequenzen muessen vorher entfernt werden, die Sequenznummerierung muss dennoch aufsteigend
                            #! kontinuierlich sein und der Index muss resetet sein (siehe mst.py file)
        EventNumber ... Numerierung der Elemente in einer Sequenz, bei einer neuen Sequenz beginnt die EventNummer wieder bei 1
        Time        ...     die Zeit gibt den Abstand vom Start der Sequenz an. Eine neue Sequenz reseted die Time
                            der erste Wert ist daher nur im Kontext des spezifischen Experimentes zu interpretieren
                            im Sequenzexperiment sollte nicht der Abstand vom vergangenen bei der Berechnung des ersten verwendet werden
                            da noch 2000 ms der Hinweis ueber das nun folgende Paradigma eingeblendet wird, diese sollten abgezogen werden
                            so dass dem Wesen nach die erste Zeitangabe moeglichst die Zeit vom Start der aktuellen Sequenz wiedergibt
        isHit       ... Ob der Button korrket gedrueckt wurde (redundant und sollte sich aus pressed und target ergeben)
        target      ... Der Zielknopf der gedrueckt werden sollte
        pressed     ... Der Button der tatsaechlich gedrueckt wurde
        sequence    ... Die Sequence die gerad durchgefuehrt wird. Wenn mehrere Sequenzen in dem Experiment vorhanden sind dann 
                            sollten diese der Wichtigkeit nach geordnet sein. z.B. im SRTT sollte das fixed mit einer 1 kodiert sein
                            das random mit 2. Im Seq die haeufigste Hauptsequenz als 1 und die selteneren Vergleichssequenzen mit 2 und 3

        BlockNumber	SequenceNumber	EventNumber	    Time      isHit	    target	pressed	 sequence
            1	        1	            1	        1831	    1	       4	    4	    0
            1	        1	            2	        2552	    1	       1	    1	    0
            1	        1	            3	        4483	    1	       3	    3	    0
            1	        1	            4	        5219	    1	       2	    2	    0
            1	        1	            5	        6081	    1	       4	    4	    0
            1	        2	            1	        2219	    1	       4	    4	    0
            1	        2	            2	        2785	    1	       1	    1	    0
            1	        2	            3	        3545	    1	       3	    3	    0
            1	        2	            4	        4118	    1	       2	    2	    0
            1	        2	            5	        4727	    1	       4	    4	    0
            1	        3	            1	        756	        1	       4	    4       0
            1	        3	            2	        1535	    1	       1	    1	    0
            1	        3	            3	        2354	    1	       3	    3	    0
            1	        3	            4	        2936	    1	       2	    2	    0
            1	        3	            5	        4535	    1	       4	    4	    0
            2	        4	            1	        902	        1	       4	    4	    0
            2	        4	            2	        1556	    1	       1	    1	    0
            2	        4	            3	        2748	    1	       3	    3	    0
            2	        4	            4	        3330	    1	       2	    2	    0
            2	        4	            5	        4485	    1	       4	    4	    0
            2	        5	            1	        800	        1	       4	    4	    1
            2	        5	            2	        1351	    1	       1	    1	    1
            2	        5	            3	        2150	    1	       3	    3	    1
            2	        5	            4	        2898	    1	       2	    2	    1
            2	        5	            5	        4153	    1	       4	    4	    1
            
        """


    def __init__(self, experiment_name, vpn, day, sequence_length, root_dir, is_load=False, df="leer", sep='\t', paradigma = 0):
        """ idee an der init ist, dass nur ein Experimentname, ein vpn, ein Tag und sequenzlaenge uebergeben werden muesse
            wenn es hier bereits ein abgespeichertes experiment gibt dann wird das geladen
            es kann aber auch neu berechnet werden
            damit koennte man dann durch eine Liste iterieren und sich jeweils die experiment Klasse die bereits schon
            mal ausgerechnet wurde uebergeben lassen
        """
        self.experiment_name = experiment_name  # Name des Experiments (MST, SEQ, SRTT)
        self.vpn = vpn  # die Versuchspersonennummer
        self.day = day  # DER Trainingstag
        self.paradigma = paradigma  # falls an einem Tag unterschiedliche Interventionen erfolgten (MST_21 vs. MST_22 vs. MST_23) 
        self.sequence_length = sequence_length
        self.filename = str(self.vpn) + '_' + self.experiment_name + '_' +  str(self.day) + '_' + str(self.paradigma) + '_' + str(self.sequence_length)

        # the root dir is the dir where the estimations are rooted, 
        # in this dir there will an Experiment_data dir created
        # in this Experiment_data dir all the experiment files will be saved and loaded
        self.root_dir = root_dir
        self.data_dir =  os.path.join(self.root_dir, 'Experiment_data')       
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # das Dataframe mit den standardisierten DAten eines Experimentes
        if is_load:
            pass 
        else:
            if isinstance(df, str):
                if df=='leer':
                    print('if is_load = False then there has to be a dataframe or a filename to a csv file')
                    try:
                        self.df = pd.read_csv(df, sep=sep, engine='python')
                    except:
                        print("cannt load the inputfile that was given as string")
                        raise ValueError('pandas value error')
            else:
                self.df  = df #? getestet

            self.estimate_experiment_attributes()



    def estimate_experiment_attributes(self):
        #  df_ipi hat in der Time Column interpress intervalle anstatt von Sequencet9imeings ansonsten identisch zu self.df
        self.df_ipi = exp_est.generate_df_ipi(self.df)  #? getestet

        
        #! Sequencelength Berechnung klappt nur wenn alle Sequenzen tatsaechlich gleich lang sind
        #self.sequence_length = self.df['SequenceNumber'].value_counts().unique()[0]  

        # speichere zum weiteren testen
        self.df.to_csv('.\\experiment_input.csv', index = False, sep = '\t')
        self.df_ipi.to_csv('.\\experiment_input_ipi.csv', index = False, sep = '\t')

        self.paradigmen = []        # description of the paradigms as list of strings
    
        #! ein wesentlicher Unterschied ist noch, dass beim MST der erste ipi nicht geloescht wird
        self.is_delete_first = False if self.experiment_name=="MST" else True

        # initialisiere alle notwendigen Attribute
        # implemented by estimate_all_ipi_hits
        a, b, c, d  = exp_est.estimate_all_ipi_hits_lsln(self.df_ipi)
        self.all_ipi_lsln = a
        self.cor_ipi_lsln = b
        self.err_ipi_lsln = c
        self.all_hits_lsln = d
#       pd.set_option('display.max_rows', 2000)
#       print(dfshow.head(180))
        
        a,b,c,d = exp_est.estimate_ipi_hits_lblsln(self.df_ipi)
        self.all_ipi_lblsln = a        #estimate_all_ipi_hits_lglsln_lsln()
        self.cor_ipi_lblsln = b       #estimate_all_ipi_hits_lglsln_lsln()
        self.err_ipi_lblsln = c       #estimate_all_ipi_hits_lglsln_lsln()
        self.all_hits_lblsln = d       #estimate_all_ipi_hits_lglsln_lsln()
        
        a, b, c, d = exp_est.estimate_ipi_hits_lplsln(self.df_ipi)
        self.all_ipi_lplsln = a
        self.cor_ipi_lplsln = b 
        self.err_ipi_lplsln = c
        self.all_hits_lplsln = d

        a,b, c, d = exp_est.estimate_ipi_hits_lplblsln(self.df_ipi)
        #print(self.df_ipi.tail())
        self.all_ipi_lplblsln = a
        self.cor_ipi_lplblsln = b 
        self.err_ipi_lplblsln = c
        self.all_hits_lplblsln = d

        #___________________________
        # implemented by estimate_seqsum()
        
        a, b, c, d = exp_est.estimate_seqsum(self.all_ipi_lplblsln)
        self.all_seqsum_lpn = a #?check error check # Anzahl der vollstaendigen (all) Sequenzen pro paradigma  
        self.all_seqsum_lplbn = b  #?check error check # Anzahl der vollstaendigen korrekten Sequenzen pro Paradigma pro block
        self.all_seqtimesum_lplsn = c #? check # Summe der Zeiten einer Sequenz als Liste ueber die Paradigma ueber die Sequenzen
        self.all_seqtimesum_lplblsn = d #? check
        
        a, b, c, d = exp_est.estimate_seqsum(self.cor_ipi_lplblsln)
             
        self.cor_seqsum_lpn = a
        self.cor_seqsum_lplbn = b
        self.cor_seqtimesum_lplsn = c
        self.cor_seqtimesum_lplblsn = d

        a, b, c, d = exp_est.estimate_seqsum(self.err_ipi_lplblsln)
        self.err_seqsum_lpn = a 
        self.err_seqsum_lplbn = b
        self.err_seqtimesum_lplsn = c
        self.err_seqtimesum_lplblsn = d 
       #__________________________
       # 

        # Anstieg der Regressionsgeraden ueber die mittlere Dauer der Sequenzen (nicht gemittelt ueber die Bloecke) (aktuell noch kein sliding window)                   
        self.all_seqtimesum_slope_lpn, self.all_seqtimesum_to_max_slope_lpn = exp_est.estimate_seqtimesum_slope_lpn(self.all_seqtimesum_lplsn)
        self.cor_seqtimesum_slope_lpn, self.cor_seqtimesum_to_max_slope_lpn = exp_est.estimate_seqtimesum_slope_lpn(self.cor_seqtimesum_lplsn)
        self.err_seqtimesum_slope_lpn, self.err_seqtimesum_to_max_slope_lpn = exp_est.estimate_seqtimesum_slope_lpn(self.err_seqtimesum_lplsn)
        
        # Anstieg der REgressionsgeraden ueber die mittlere Dauer der Sequenzen pro Block (bis zum Ende oder mis zum Minimum)
        self.all_seqtimesum_per_block_slope_lpn, self.all_seqtimesum_per_block_to_max_slope_lpn = exp_est.estimate_seqtimesum_slope_lplbn(self.all_seqtimesum_lplblsn)
        self.cor_seqtimesum_per_block_slope_lpn, self.cor_seqtimesum_per_block_to_max_slope_lpn = exp_est.estimate_seqtimesum_slope_lplbn(self.cor_seqtimesum_lplblsn)
        self.err_seqtimesum_per_block_slope_lpn, self.err_seqtimesum_per_block_to_max_slope_lpn = exp_est.estimate_seqtimesum_slope_lplbn(self.err_seqtimesum_lplblsn)


        # Anstieg der REgressionsgeraden ueber die Anzahl der Sequenzen die in einem Block geschafft wurden
        self.all_seqnum_per_block_slope_lpn = exp_est.estimate_seqnum_per_block_slope(self.all_seqtimesum_lplblsn) # n = Anstieg der REgressionsgeraden ueber die Anzahl der Sequenzen die in einem Block geschafft wurden ... n
        self.cor_seqnum_per_block_slope_lpn = exp_est.estimate_seqnum_per_block_slope(self.cor_seqtimesum_lplblsn)  #  ... das ist fuer SEQ kein sinnvolles Mass da die Bloecke ueber die Anzahl der Sequenzen definiert wurden
        self.err_seqnum_per_block_slope_lpn = exp_est.estimate_seqnum_per_block_slope(self.err_seqtimesum_lplblsn)    

        # netzwerkparameter fehlen hier noch
        
        #debug = Debug(self)


    def add_network_class(self, coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= True, is_estimate_Q= False, num_random_Q=0, parad = 0):
        # CK 08.09.2020
        #ipi_cor = exp_est.make2dlist_to_2darray(self.cor_ipi_lsln)
        # CK 08.09.2020
        #ipi_cor = exp_est.make2dlist_to_2darray(self.cor_ipi_lplsln[parad,:,:])
        # CK 10.09.2020
        ipi_cor = exp_est.make2dlist_to_2darray(self.cor_ipi_lplsln[parad][:][:])
        self.net = Network(ipi_cor, coupling_parameter = coupling_parameter,  resolution_parameter = resolution_parameter,is_estimate_clustering= is_estimate_clustering, is_estimate_Q= is_estimate_Q, num_random_Q=num_random_Q)
        #self.net.filename = self.filename

    def save(self):
        """ how to save the experiment class?
        """
        #dirname = os.path.join(os.path.dirname(__file__),'Experiment_data')
        #dirname = os.path.join(self.root_dir,'Experiment_data')
        # logging.debug(f"in Experiment.save with data_dir = {self.data_dir}, filename = {self.filename}")
        # print("in Experiment.save()")
        with open(os.path.join(self.data_dir, self.filename),'wb') as fp:
            pickle.dump(self, fp)

    # def save_as_json(self):
    #     results = {
    #         'experiment_name'                           : self.experiment_name,               # Name des Experiments (MST, SEQ, SRTT)
    #         'vpn'                                       : self.vpn,                                        # die Versuchspersonennummer
    #         'day'                                       : self.day,                                       # DER Trainingstag
    #         'paradigma'                                 : self.paradigma,            # falls an einem Tag unterschiedliche Interventionen erfolgten (MST_21 vs. MST_22 vs. MST_23) 
    #         'sequence_length'                           : self.sequence_length,
    #         'filename'                                  : self.filename,
    #         'root_dir'                                  : self.root_dir,
    #         'data_dir'                                  : self.data_dir,
    #         'is_delete_first'                           : self.is_delete_first,  #! ein wesentlicher Unterschied ist noch, dass beim MST der erste ipi nicht geloescht wird      
    #         'all_ipi_lsln'                              : self.all_ipi_lsln, 
    #         'cor_ipi_lsln'                              : self.cor_ipi_lsln, 
    #         'err_ipi_lsln'                              : self.err_ipi_lsln, 
    #         'all_hits_lsln'                             : self.all_hits_lsln, 
    #         'all_ipi_lblsln'                            : self.all_ipi_lblsln, 
    #         'cor_ipi_lblsln'                            : self.cor_ipi_lblsln, 
    #         'err_ipi_lblsln'                            : self.err_ipi_lblsln , 
    #         'all_hits_lblsln'                           : self.all_hits_lblsln, 
    #         'all_ipi_lplsln'                            : self.all_ipi_lplsln, 
    #         'cor_ipi_lplsln'                            : self.cor_ipi_lplsln, 
    #         'err_ipi_lplsln'                            : self.err_ipi_lplsln, 
    #         'all_hits_lplsln'                           : self.all_hits_lplsln, 
    #         'all_ipi_lplblsln'                          : self.all_ipi_lplblsln, 
    #         'cor_ipi_lplblsln'                          : self.cor_ipi_lplblsln, 
    #         'err_ipi_lplblsln'                          : self.err_ipi_lplblsln, 
    #         'all_hits_lplblsln'                         : self.all_hits_lplblsln, 
    #         'all_seqsum_lpn'                            : self.all_seqsum_lpn, 
    #         'all_seqsum_lplbn'                          : self.all_seqsum_lplbn, 
    #         'all_seqtimesum_lplsn'                      : self.all_seqtimesum_lplsn, 
    #         'all_seqtimesum_lplblsn'                    : self.all_seqtimesum_lplblsn, 
    #         'cor_seqsum_lpn'                            : self.cor_seqsum_lpn, 
    #         'cor_seqsum_lplbn'                          : self.cor_seqsum_lplbn, 
    #         'cor_seqtimesum_lplsn'                      : self.cor_seqtimesum_lplsn, 
    #         'cor_seqtimesum_lplblsn'                    : self.cor_seqtimesum_lplblsn, 
    #         'err_seqsum_lpn'                            : self.err_seqsum_lpn, 
    #         'err_seqsum_lplbn'                          : self.err_seqsum_lplbn, 
    #         'err_seqtimesum_lplsn'                      : self.err_seqtimesum_lplsn, 
    #         'err_seqtimesum_lplblsn'                    : self.err_seqtimesum_lplblsn,     
    #         'all_seqtimesum_slope_lpn'                  : self.all_seqtimesum_slope_lpn, 
    #         'all_seqtimesum_to_max_slope_lpn'           : self.all_seqtimesum_to_max_slope_lpn, 
    #         'cor_seqtimesum_slope_lpn'                  : self.cor_seqtimesum_slope_lpn, 
    #         'cor_seqtimesum_to_max_slope_lpn'           : self.cor_seqtimesum_to_max_slope_lpn, 
    #         'err_seqtimesum_slope_lpn'                  : self.err_seqtimesum_slope_lpn, 
    #         'err_seqtimesum_to_max_slope_lpn'           : self.err_seqtimesum_to_max_slope_lpn, 
    #         'all_seqtimesum_per_block_slope_lpn'        : self.all_seqtimesum_per_block_slope_lpn, 
    #         'all_seqtimesum_per_block_to_max_slope_lpn' : self.all_seqtimesum_per_block_to_max_slope_lpn,  
    #         'cor_seqtimesum_per_block_slope_lpn'        : self.cor_seqtimesum_per_block_slope_lpn, 
    #         'cor_seqtimesum_per_block_to_max_slope_lpn' : self.cor_seqtimesum_per_block_to_max_slope_lpn, 
    #         'err_seqtimesum_per_block_slope_lpn'        : self.err_seqtimesum_per_block_slope_lpn, 
    #         'err_seqtimesum_per_block_to_max_slope_lpn' : self.err_seqtimesum_per_block_to_max_slope_lpn, 
    #         'all_seqnum_per_block_slope_lpn'            : self.all_seqnum_per_block_slope_lpn, 
    #         'cor_seqnum_per_block_slope_lpn'            : self.cor_seqnum_per_block_slope_lpn, 
    #         'err_seqnum_per_block_slope_lpn'            : self.err_seqnum_per_block_slope_lpn, 
    #         'net_A'                                     : self.net.A,
    #         'net_C'                                     : self.net.C,
    #         'net_c'                                     : self.net.c,
    #         'net_ipi'                                   : self.net.ipi,
    #         'net_is_estimate_clustering'                : self.net.is_estimate_clustering,
    #         'net_k'                                     : self.net.k,
    #         'net_kappa'                                 : self.net.kappa,
    #         'net_m'                                     : self.net.m,
    #         'net_my2'                                   : self.net.my2,
    #         'net_phi'                                   : self.net.phi,
    #         'net_phi_real'                              : self.net.phi_real,
    #         'net_phi_fake_list'                         : self.net.phi_fake_list,
    #         'net_q_real'                                : self.net.q_real,
    #         'net_q_real_t'                              : self.net.q_real_t,
    #         'net_q_real_p'                              : self.net.q_real_p,
    #         'net_q_fake_list'                           : self.net.q_fake_list,
    #         'net_g_real'                                : self.net.g_real,
    #         'net_g_fake_list'                           : self.net.g_fake_list,
    #         'net_is_adapt_communities_across_trials'    : self.net.is_adapt_communities_across_trials,
    #         'net_is_estimate_Q'                         : self.net.is_estimate_Q,
    #         'net_num_random_Q'                          : self.net.num_random_Q,
    #         'net_resolution_parameter'                  : self.net.resolution_parameter,
    #     }
    #     json_data_dir = self.data_dir + "json"
    #     if not os.path.exists(json_data_dir):
    #         os.makedirs(json_data_dir)
    #     with open(os.path.join(json_data_dir, self.filename + '.json'),'w') as fp:
    #         json.dump(results, fp)


    def load(self):
        #dirname = os.path.join(os.path.dirname(__file__),'Experiment_data')
        with open(os.path.join(self.data_dir, self.filename),'rb') as fp:
            return pickle.load(fp)

    def __str__(self):
        string = "Experiment Name: " + self.experiment_name 
        string = string + "; VPN = " + str(self.vpn)
        string = string + "; Day = " + str(self.day)
        string = string + "; Paradigma = " + str(self.paradigma)
        string = string + str(self.cor_seqsum_lpn)
        pd.set_option('display.max_rows', 2000)
        pd.set_option('display.max_columns', 2000)
        #self.df_debug.to_csv("log_df_debug.log",sep='\t')
        #for idx, row in self.df_debug.iterrows():
        #    logger.info(row)
        #logger.info(self.df_debug)
        #print(self.all_ipi_lsln)
        #print(self.all_hits_lsln)
        return string

    __repr__ = __str__


if __name__ == "__main__":
    print('start experiment main')
    computername = socket.gethostname()
    if computername == "BigBang":
        mstfile = "G:\\Unity\\MST_JSAM\\analyse_csvs\\Data_Rogens\\MST\\17_TimQueißertREST1fertig.csv"
    if computername == "XenonBang":
        mstfile = "H:\\Unity\\MST_JSAM\\analyse_csvs\\Data_Rogens\\MST\\17_TimQueißertREST1fertig.csv"
    if computername == "Laptop-LittleBang":
        #mstfile = "D:\Programming\MST_JSAM\analyse_csvs\Data_Rogens\Results\Experiment_data\\17_TimQueißertREST1fertig.csv"
        #subj_exp = Experiment("MST", 15, 1, 8, is_load = True)
        estimate = True

        paradigma = "MST"

        paradigma = 'SEQ'
        paradigma = 'SEQsimple'
        simulation = True
        
        if not estimate:
            file = 'D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\Results\\Experiment_data\\15_MST_1_5'
            file = 'D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\Results\\Experiment_data\\23_SEQ_1_8' #22
            file = 'D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\Results\\Experiment_SEQ\\23_SEQ_1_0_8' #22
            with open(file,'rb') as fp:
                subj_exp = pickle.load(fp)
        # print(vars(subj_exp.net))
        # attributes = [attr for attr in dir(subj_exp.net) if (not attr.startswith('__'))]
        # print("attributes........................")
        # print(attributes)
        if estimate:
            if paradigma=="SEQ":
                file = os.path.join("D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SEQ", "20_JulianKlosFRA1fertig.csv")
                file = os.path.join("D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SEQ", "23_Isabell BernhardFRA1fertig.csv")
                if simulation:
                    file = os.path.join("D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SEQ_Sim", "34_NoraRichterFRA1fertig.csv")
            if paradigma=="SEQsimple":
                if simulation:
                    file = os.path.join("D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SEQ_Sim", "34_SEQsimpleFRA1fertig.csv")
            if paradigma=="MST":
                file = os.path.join("D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\MST_Sim", "16_PaulaHörnigREST2fertig.csv")
                file = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_MST_Grischeck\\Jung\\3_Elena​Buettner​MOLE21fertig.csv"
            if paradigma == "SRTT":
                file = os.path.join("D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\SRTT", "28_Dorothea Staub199811211_SRTT1.csv")
            
            
            
            
        # subj_class = MST(fullfilename = mstfile, sequence_length = 5) #, path_output = ".\\Data_python", _id = "no_id")
        #subj_class = SEQ(fullfilename = srttfile, sequence_length = 10) #, path_output = ".\\Data_python", _id = "no_id")
            root_dir = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_Rogens\\tmp"
            root_dir = "D:\\Programming\\MST_JSAM\\analyse_csvs\\Data_MST_Grischeck\\tmp"
            #subj_class = SEQ(fullfilename = orgseqfile, sequence_length = 8, path_output = root_dir, _id = "no_id")
            if paradigma == 'MST':
                subj_class = MST(fullfilename = file, sequence_length = 5, path_output = root_dir, _id = "no_id")
            if paradigma == 'SEQ':
                subj_class = SEQ(fullfilename = file, sequence_length = 8, path_output = root_dir, _id = "no_id")
            if paradigma == 'SEQsimple':
                subj_class = SEQ(fullfilename = file, sequence_length = 8, path_output = root_dir, _id = "no_id")
        # print("MST ready")
            subj_exp = Experiment(subj_class.experiment_name, subj_class.vpn, subj_class.day, subj_class.sequence_length, root_dir,is_load=False, df = subj_class.df, paradigma=0)
        #print(subj_exp.cor_seqtimesum_lplblsn)
        #print(subj_exp.all_seqtimesum_lplblsn)


            subj_exp.add_network_class(coupling_parameter = 0.913,  resolution_parameter = 0.9, is_estimate_clustering= False, is_estimate_Q= True, num_random_Q=3)
            print(subj_exp.net.print_Q_parts())
            #subj_exp.add_network_class(coupling_parameter = 0.01,  resolution_parameter = 0.9, is_estimate_clustering= False, is_estimate_Q= True, num_random_Q=3)
            #subj_exp.save_as_json()
        # print("all_seqtimesum_per_block_slope_lpn")
        # print(subj_exp.all_seqtimesum_per_block_slope_lpn)
        # print("subj_exp.err_seqsum_lplbn")
        # print(subj_exp.err_seqsum_lplbn)
        # print("err_ipi_lplblsln")
        # for idx, p in enumerate(subj_exp.err_ipi_lplblsln):
        #     print(f"paradigma {idx}")
        #     for idx2,b in enumerate(p):
        #         print(f"block {idx2}")
        #         print(b)
        # print("Q_REAL")
        # print(subj_exp.net.q_real)
        # print("Q_FAKE")
        # print(subj_exp.net.q_fake_list)
        # print(subj_exp.net.phi)
        
        #print(vars(subj_exp.net))
        #attributes = [attr for attr in dir(subj_exp.net) if (not attr.startswith('__'))]
        #print("attributes........................")
        #print(attributes)
        

    # print(f"in main now subj_exp.add_network_class")
    # subj_exp.add_network_class(coupling_parameter = 0.03,  resolution_parameter = 0.9, is_estimate_clustering= False, is_estimate_Q= True, num_random_Q=3)
    # # with open('testpickle','rb') as fp:
    # #     subj_exp = pickle.load(fp)
    # print('now save')
    # subj_exp.save()

    # #subj_exp = Experiment( "name", 1, 1, 5, "x")
    # #subj_exp.load()
    # print(subj_exp.err_seqsum_lpn)    

