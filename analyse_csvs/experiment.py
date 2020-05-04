import numpy as np
import pandas as pd
import logging

##################################
### logging 
log_level = logging.INFO
data_base_log_level = logging.INFO

logging.basicConfig(level=log_level, filename='logfile.log', 
    format ='', #format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s',
    filemode='w')
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

    #! number:  z.B. sequence length
        8  # python integer
        
    #! list of numbers:  z.B. cor_seq_abs
        [20, 12, 8] # list python integers (mostly list across paradigms)        

    #! list of lists of numbers:  z.B. cor_seq_per_block
        [                                # list of ...  (mostly paradigms)
            [6 17 18 19 20 22 22 24 25] # Paradigma 1 | list number of correct sequences per block 
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
        p = block
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


    def __init__(self, experiment_name, vpn, day, df):
        self.experiment_name = experiment_name  # Name des Experiments (MST, SEQ, SRTT)
        self.vpn = vpn  # die Versuchspersonennummer
        self.day = day # DER Trainingstag
        self.df  = df # das Dataframe mit den standardisierten DAten eines Experimentes
        
        #! ein wesentlicher Unterschied ist noch, dass beim MST der erste ipi nicht geloescht wird
        self.is_delete_first = False if self.experiment_name=="MST" else True

        # initialisiere alle notwendigen Attribute
        # implemented by estimate_all_ipi_hits
        self.all_ipi_lsln = []          #estimate_all_ipi_hits_lglsln_lsln()
        self.all_hits_lsln = []         #estimate_all_ipi_hits_lglsln_lsln()

        self.all_ipi_lblsln = []        #estimate_all_ipi_hits_lglsln_lsln()
        self.all_hits_lblsln = []       #estimate_all_ipi_hits_lglsln_lsln()

        self.all_ipi_lplsln = []
        self.cor_ipi_lplsln = [] 
        self.err_ipi_lplsln = []
            
        self.all_ipi_lplblsln = []
        self.cor_ipi_lplblsln = [] 
        self.err_ipi_lplblsln = []

        #___________________________
        # implemented by estimate_seqsum()
        self.all_seqsum_lpn = []  # anzahl der vollstaendigen Sequenzen pro paradigma 
        self.cor_seqsum_lpn = []  # Anzahl der vollstaendigen korrekten Sequenzen pro Paradigma
        self.err_seqsum_lpn = []

        self.all_seqsum_lplbn = []  # anzahl der vollstaendigen Sequenzen pro block pro paradigma 
        self.cor_seqsum_lplbn = []  
        self.err_seqsum_lplbn = []

        self.all_seqtimesum_lplsn = []  # n = gesamtdauer pro Sequenz als liste
        self.cor_seqtimesum_lplsn = [] 
        self.err_seqtimesum_lplsn = []

        self.all_seqtimesum_lplblsn = []  # n = gesamtdauer pro Sequenz als liste
        self.cor_seqtimesum_lplblsn = [] 
        self.err_seqtimesum_lplblsn = []

       #__________________________
       # 
               
        self.all_seqtimesum_slope_lpn = []  # n = Anstieg der REgressionsgeraden ueber die gesamtdauer pro Sequenz 
        self.cor_seqtimesum_slope_lpn = [] 
        self.err_seqtimesum_slope_lpn = []
        
        self.all_seqtimesum_per_block_slope_lpn = []  # n = Statt ueber alle Sequenzen wird ueber die mittlere Dauer der Sequenzen pro block die regression gemacht
        self.cor_seqtimesum_per_block_slope_lpn = [] 
        self.err_seqtimesum_per_block_slope_lpn = []
        
        self.all_seqtimesum_to_max_slope_lpn = []  # n = Anstieg der REgressionsgeraden ueber die gesamtdauer pro Sequenz aber nur bis zur maximalen Geschwindigkeit (sliding window ueber 3 hintereinander erfolgte sequenzen)
        self.cor_seqtimesum_to_max_slope_lpn = [] 
        self.err_seqtimesum_to_max_slope_lpn = []
        
        self.all_seqtimesum_per_block_to_max_slope_lpn = []  # n = Statt ueber alle Sequenzen wird ueber die mittlere Dauer der Sequenzen pro block die regression gemacht aber nur bis zum schnellsten block
        self.cor_seqtimesum_per_block_to_max_slope_lpn = [] 
        self.err_seqtimesum_per_block_to_max_slope_lpn = []
        
        self.all_seqnum_per_block_slope_lpn = []  # n = Anstieg der REgressionsgeraden ueber die Anzahl der Sequenzen die in einem Block geschafft wurden ... n
        self.cor_seqnum_per_block_slope_lpn = []  #  ... das ist fuer SEQ kein sinnvolles Mass da die Bloecke ueber die Anzahl der Sequenzen definiert wurden
        self.err_seqnum_per_block_slope_lpn = []

        self.paradigmen = []        # description of the paradigms as list of strings
        self.sequence_length = self.df['SequenceNumber'].value_counts().unique()[0]   

        # netzwerkparameter fehlen hier noch

        self.df.to_csv('.\\tmp.csv', index = False, sep = '\t')

        
        print('before initialize')
        self.initialize()
        
        self.df_debug = df.copy() # only for debug reasons
        self.add_parameter_to_df_debug(self.all_ipi_lsln, "all_ipi_lsn")
        #print(self.all_seqnum_per_block_slope_lpn)

    def initialize(self):
        """ initialize alle lists
        """
        df = self.df

        self.estimate_all_ipi_hits()
        self.all_seqsum_lpn, self.all_seqsum_lplbn, self.all_seqtimesum_lplsn, self.all_seqtimesum_lplblsn = self.estimate_seqsum(self.all_ipi_lplblsln)
        self.cor_seqsum_lpn, self.cor_seqsum_lplbn, self.cor_seqtimesum_lplsn, self.cor_seqtimesum_lplblsn = self.estimate_seqsum(self.cor_ipi_lplblsln)
        self.err_seqsum_lpn, self.err_seqsum_lplbn, self.err_seqtimesum_lplsn, self.err_seqtimesum_lplblsn = self.estimate_seqsum(self.err_ipi_lplblsln)
        self.estimate_slopes()


    def add_parameter_to_df_debug(self, all_ipi_lsln, string):
        self.df_debug = self.add_lsln(self.df_debug, all_ipi_lsln, string)

    def add_lsln(self, df, lsln, col_name):
        flat_list = [item for sublist in lsln for item in sublist]
        print(len(flat_list))
        print(self.df_debug.shape)
        df[col_name] = flat_list

        return df

    def estimate_slopes(self):
        self.all_seqtimesum_slope_lpn, all_seqtimesum_to_max_slope_lpn = self.estimate_seqtimesum_slope_lpn(self.all_seqtimesum_lplsn)
        self.cor_seqtimesum_slope_lpn, cor_seqtimesum_to_max_slope_lpn = self.estimate_seqtimesum_slope_lpn(self.cor_seqtimesum_lplsn)
        self.err_seqtimesum_slope_lpn, err_seqtimesum_to_max_slope_lpn = self.estimate_seqtimesum_slope_lpn(self.err_seqtimesum_lplsn)

        self.all_seqtimesum_per_block_slope_lpn, self.all_seqtimesum_per_block_to_max_slope_lpn = self.estimate_seqtimesum_slope_lplbn(self.all_seqtimesum_lplblsn)
        self.cor_seqtimesum_per_block_slope_lpn, self.cor_seqtimesum_per_block_to_max_slope_lpn = self.estimate_seqtimesum_slope_lplbn(self.cor_seqtimesum_lplblsn)
        self.err_seqtimesum_per_block_slope_lpn, self.err_seqtimesum_per_block_to_max_slope_lpn = self.estimate_seqtimesum_slope_lplbn(self.err_seqtimesum_lplblsn)

        self.all_seqnum_per_block_slope_lpn = self.estimate_seqnum_per_block_slope(self.all_seqtimesum_lplblsn)
        self.cor_seqnum_per_block_slope_lpn = self.estimate_seqnum_per_block_slope(self.cor_seqtimesum_lplblsn)
        self.err_seqnum_per_block_slope_lpn = self.estimate_seqnum_per_block_slope(self.err_seqtimesum_lplblsn)

    def estimate_seqnum_per_block_slope(self, lplblsn):
        seqtimesum_slope_lpn = []
        for lblsn in lplblsn: 
            abs_seq_num_per_block = []
            for lsn in lblsn:  
                abs_seq_num_per_block.append(len(lsn))
            seqtimesum_slope_lpn.append(self.estimate_slope(abs_seq_num_per_block))

        return seqtimesum_slope_lpn



    def estimate_seqtimesum_slope_lpn(self, lplsn):
        seqtimesum_slope_lpn = []
        seqtimesum_to_max_slope_lpn = []
        for lsn in lplsn:
            if not lsn: # empty
                seqtimesum_slope_lpn.append(self.estimate_slope(lsn))
                seqtimesum_to_max_slope_lpn.append(self.estimate_slope(lsn))
            else:
                seqtimesum_slope_lpn.append(self.estimate_slope(lsn))
                min_pos = lsn.index(min(lsn))
                if min_pos>10:
                    seqtimesum_to_max_slope_lpn.append(self.estimate_slope(lsn[:min_pos]))
                else:
                    seqtimesum_to_max_slope_lpn.append(self.estimate_slope(lsn))

        return (seqtimesum_slope_lpn, seqtimesum_to_max_slope_lpn)



    def estimate_seqtimesum_slope_lplbn(self, lplblsn):
        seqtimesum_slope_lpn = []
        seqtimesum_to_max_slope_lpn = []
        for lblsn in lplblsn: 
            average_seq_time_per_block = []
            for lsn in lblsn:  
                if len(lsn) == 0:
                    average_seq_time_per_block.append(sum(lsn))
                else:
                    average_seq_time_per_block.append(sum(lsn)/len(lsn))            
            seqtimesum_slope_lpn.append(self.estimate_slope(average_seq_time_per_block))
            max_pos = average_seq_time_per_block.index(min(average_seq_time_per_block))
            if max_pos>3:
                seqtimesum_to_max_slope_lpn.append(self.estimate_slope(average_seq_time_per_block[:max_pos]))
            else:
                seqtimesum_to_max_slope_lpn.append(self.estimate_slope(average_seq_time_per_block))

        return (seqtimesum_slope_lpn, seqtimesum_to_max_slope_lpn)


    def estimate_slope(self, y):
        if len(y)<2:
            slope, b = None, None
        else:
            x = np.arange(len(y))
            slope,b = np.polyfit(x, y, 1)
        return (slope, b)

        # # slope 1 to 10
        # slope_1_10,b = np.polyfit(x[:10], self.corrsq[:10], 1)

        # # slope to max
        # pos_max = self.corrsq.index(max(self.corrsq))
        # x = np.arange(pos_max+1) # 1 because pos_max starts by 0 and range is not including
        # slope_to_max,b = np.polyfit(x, self.corrsq[:pos_max+1], 1)

        # return (slope, slope_to_max, slope_1_10)


    def estimate_seqsum(self, ipi_lplblsln):
        """ estimates parameter:
            input is    self.all_ipi_lplblsln oder
                        self.cor_ipi_lplblsln oder
                        self.err_ipi_lplblsln
            output entsprechend

            self.all_seqsum_lpn = []  # anzahl der vollstaendigen Sequenzen pro paradigma 
            self.all_seqsum_lplbn = []  # anzahl der vollstaendigen Sequenzen pro block pro paradigma 
            self.all_seqtimesum_lplsn = []  # n = gesamtdauer pro Sequenz als liste
            self.all_seqtimesum_lplblsn = []  # n = gesamtdauer pro Sequenz als liste
            
            oder 

            self.cor_seqsum_lpn = []  # Anzahl der vollstaendigen korrekten Sequenzen pro Paradigma
            self.cor_seqsum_lplbn = []  
            self.cor_seqtimesum_lplsn = [] 
            self.cor_seqtimesum_lplblsn = [] 
            
            oder 

            self.err_seqsum_lpn = []
            self.err_seqsum_lplbn = []
            self.err_seqtimesum_lplsn = []
            self.err_seqtimesum_lplblsn = []
        """
        seq_sum_lpn = []
        seq_sum_lplbn = []
        seqtimesum_lplsn = []
        seqtimesum_lplblsn = []

        for paradigma in ipi_lplblsln:
            sum_in_paradigma = 0
            seq_sum_lbn = []
            seqtimesum_lblsn = []
            seqtimesum_lsn = []
            for block in paradigma:
                sum_one_block = 0
                seqtimesum_lsn_single = []
                for seq in block:
                    sum_one_block += 1
                    sum_in_paradigma += 1 
                    seqtimesum_lsn.append(sum(seq))
                    seqtimesum_lsn_single.append(sum(seq))
                    
                seqtimesum_lblsn.append(seqtimesum_lsn_single)
                seq_sum_lbn.append(sum_one_block)
            
            seq_sum_lplbn.append(seq_sum_lbn)
            seq_sum_lpn.append(sum_in_paradigma)
            seqtimesum_lplsn.append(seqtimesum_lsn)
            seqtimesum_lplblsn.append(seqtimesum_lblsn)


        return (seq_sum_lpn, seq_sum_lplbn, seqtimesum_lplsn, seqtimesum_lplblsn)

    def estimate_all_ipi_hits(self):
        """ estimate the interpress intervalls for correct as errors 
            as list of sequences of list of numbers
        """
        """ in einem numpy Array werden die inter Key intervalls gespeichert
            die Zeit zum ersten key press entfaellt 
            Liste von Arrays
            # estimates self.ipi_lblsln, self.hits_lblsln, self.ipi_lsln, self.hits_lsln
        """ 
        df = self.df 
        all_ipi_lplsln = []
        cor_ipi_lplsln = []
        err_ipi_lplsln = []
        all_ipi_lplblsln = []
        cor_ipi_lplblsln = []
        err_ipi_lplblsln = []

        hits_lsln = []
        hits_lblsln = []
        ipi_lsln = []
        cor_ipi_lsln = []
        err_ipi_lsln = []
        ipi_lblsln = []
        cor_ipi_lblsln = []
        err_ipi_lblsln = []

        for current_paradigma in range(df['sequence'].min(), df['sequence'].max()+1):
            df_paradigma = df[df['sequence']==current_paradigma]
            for current_block in range(df_paradigma['BlockNumber'].min() ,df_paradigma['BlockNumber'].max()+1):
                df_block = df_paradigma[df_paradigma['BlockNumber']==current_block]
                
                ipi_lsln_one_block = []
                cor_ipi_lsln_one_block = []
                err_ipi_lsln_one_block = []
                hits_lsln_one_block = []
                
                # ueber alle Sequenzen in einem Block
                if not df_block.empty: # z.B. Block 7 in srtt ist empty
                    for current_seq in range(df_block['SequenceNumber'].min(), df_block['SequenceNumber'].max()+1):
                        df_sequence = df_block[df_block['SequenceNumber']==current_seq]
                        seq_tmp_time = 0
                        ipi_ln = []
                        hits_ln = []
                    
                        # ueber die rows einer Sequenz
                        for idx, row in df_sequence.iterrows():
                            ipi_ln.append(row['Time']-seq_tmp_time)
                            seq_tmp_time = row['Time']
                            hits_ln.append(row['isHit'])
                        
                                
                        ipi_lsln_one_block.append(ipi_ln)
                        ipi_lsln.append(ipi_ln)
                        hits_lsln_one_block.append(hits_ln)
                        hits_lsln.append(hits_ln)

                        if sum(hits_ln)==self.sequence_length:
                            cor_ipi_lsln_one_block.append(ipi_ln)
                            cor_ipi_lsln.append(ipi_ln)
                        else:
                            err_ipi_lsln_one_block.append(ipi_ln)
                            err_ipi_lsln.append(ipi_ln)

                    ipi_lblsln.append(ipi_lsln_one_block)
                    cor_ipi_lblsln.append(cor_ipi_lsln_one_block)
                    err_ipi_lblsln.append(err_ipi_lsln_one_block)
                    hits_lblsln.append(hits_lsln_one_block)
            all_ipi_lplsln.append(ipi_lsln)
            all_ipi_lplblsln.append(ipi_lblsln)    
            cor_ipi_lplsln.append(cor_ipi_lsln)
            cor_ipi_lplblsln.append(cor_ipi_lblsln)    
            err_ipi_lplsln.append(err_ipi_lsln)
            err_ipi_lplblsln.append(err_ipi_lblsln)  





        self.all_ipi_lsln = ipi_lsln         #estimate_all_ipi_hits_lglsln_lsln()
        self.all_hits_lsln = hits_lsln         #estimate_all_ipi_hits_lglsln_lsln()

        self.all_ipi_lblsln = ipi_lblsln       #estimate_all_ipi_hits_lglsln_lsln()
        self.all_hits_lblsln = hits_lblsln       #estimate_all_ipi_hits_lglsln_lsln()

        self.all_ipi_lplsln = all_ipi_lplsln
        self.cor_ipi_lplsln = cor_ipi_lplsln 
        self.err_ipi_lplsln = err_ipi_lplsln
            
        self.all_ipi_lplblsln = all_ipi_lplblsln
        self.cor_ipi_lplblsln = cor_ipi_lplblsln
        self.err_ipi_lplblsln = err_ipi_lplblsln

        return 


    @property
    def all_ipi_lblsln(self):
        return self.__ipi_all_no_paradigm

    @all_ipi_lblsln.setter
    def all_ipi_lblsln(self, val):
        self.__all_ipi_lblsln = self.check_list_of_lists_of_lists_of_numbers(val) #lxln









    def check_list_of_list_of_lists_of_lists_of_numbers(self, val):
        """
        [ 
            [                               # lists
            [                           # list of ... 
                [1.1, 1.2, 0.9, 0.8]    # interpres intervalls
                [1.1, 1.2, 0.9, 0.8]    # interpres intervalls
            ],
            [                           # list of ... 
                [1.1, 1.2, 0.9, 0.8]    # interpres intervalls
                [1.1, 1.2, 0.9, 0.8]    # interpres intervalls
            ]
            ]
        ]
        """
        if not isinstance(val,list):
            print("ipi_all have to be a list of lists with inter_press_interval_times")
            raise Exception("ipi_all have to be a list of lists with inter_press_interval_times")
            return
        new_liste = []
        for any in val:
            liste = self.check_list_of_lists_of_lists_of_numbers(any)
            new_liste.append(liste)
        return new_liste


    def check_list_of_lists_of_lists_of_numbers(self, val):
        """
        [                               # lists
            [                           # list of ... 
                [1.1, 1.2, 0.9, 0.8]    # interpres intervalls
                [1.1, 1.2, 0.9, 0.8]    # interpres intervalls
            ],
            [                           # list of ... 
                [1.1, 1.2, 0.9, 0.8]    # interpres intervalls
                [1.1, 1.2, 0.9, 0.8]    # interpres intervalls
            ]
            
        ]
        """
        if not isinstance(val,list):
            print("ipi_all have to be a list of lists with inter_press_interval_times")
            raise Exception("ipi_all have to be a list of lists with inter_press_interval_times")
            return
        new_liste = []
        for any in val:
            liste = self.check_list_of_lists_of_numbers(any)
            new_liste.append(liste)
        return new_liste

    def check_list_of_lists_of_numbers(self, val):
        """  [                   # list of ... 
            [1.1, 1.2, 0.9, 0.8] # interpres intervalls
            [1.1, 1.2, 0.9, 0.8]
        ]
        """
        if not isinstance(val,list):
            print("ipi_all have to be a list of lists with inter_press_interval_times")
            raise Exception("ipi_all have to be a list of lists with inter_press_interval_times")
            return
        new_liste = []
        for any in val:
            liste = self.check_list_of_numbers(any)    
            new_liste.append(liste)
        return new_liste

    def check_list_of_numbers(self, liste):
        if not isinstance(liste, list):
            print("liste has to be a list ")
            raise Exception("ipi_all have to be a list of lists with inter_press_interval_times")
            return None
        new_liste = []
        for any in liste:
            num = self.check_of_number(any)
            new_liste.append(num)
        
        return new_liste

    def check_of_number(self, num):

        if isinstance(num, float):
            print("int expected but float received")
            raise Exception("int expected but float received")
#            new_num = int(num*1000)
        try:
            if hasattr(num,'dtype'):
                new_num = int(num.item())
            else:
                new_num = int(num)
        except:
            
            raise Exception("cannot convert to integer")
        return None


    # def check_list_of_lists_of_numbers(self, val):
    #     """  [                   # list of ... 
    #         [1.1, 1.2, 0.9, 0.8] # interpres intervalls
    #         [1.1, 1.2, 0.9, 0.8]
    #     ]
    #     """
    #     if not isinstance(val,list):
    #         print("ipi_all have to be a list of lists with inter_press_interval_times")
    #         raise Exception("ipi_all have to be a list of lists with inter_press_interval_times")
    #         return
    #     ipi_all = []

    #     for seq_list in val:
    #         if not isinstance(seq_list, list):
    #             print("ipi_all have to be a list of lists with inter_press_interval_times")
    #             raise Exception("ipi_all have to be a list of lists with inter_press_interval_times")
    #         new_seq_list = []
    #         for num in seq_list:
    #             if isinstance(num, float):
    #                 new_num = int(num*1000)
    #             elif num.is_integer():
    #                 new_num = num
    #             else:
    #                 print("numbers are not float or integers")
    #                 raise Exception("numbers are not float or integers")
    #             new_seq_list.append(new_num)

    #         ipi_all.append(new_seq_list)
    #     return ipi_all

    def __str__(self):
        string = "Experiment Name: " + self.experiment_name 
        string = string + "; VPN = " + str(self.vpn)
        string = string + "; Day = " + str(self.day)
        pd.set_option('display.max_rows', 2000)
        pd.set_option('display.max_columns', 2000)
        self.df_debug.to_csv("log_df_debug.log",sep='\t')
        for idx, row in self.df_debug.iterrows():
            logger.info(row)
        #logger.info(self.df_debug)
        print(self.all_ipi_lsln)
        return string

    __repr__ = __str__