
class Results:
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
        """

    self.all_ipi_lsln = [] 
    self.all_hits_lsln = []     

    self.all_ipi_lblsln = [] 
    self.all_hits_lblsln = []

    self.all_ipi_lplsln = []
    self.cor_ipi_lplsln = [] 
    self.err_ipi_lplsln = []
           
    self.all_ipi_lplblsln = []
    self.cor_ipi_lplblsln = [] 
    self.err_ipi_lplblsln = []

    self.all_seqsum_lpn = []  # anzahl der vollstaendigen Sequenzen pro paradigma 
    self.cor_seqsum_lpn = []  # Anzahl der vollstaendigen korrekten Sequenzen pro Paradigma
    self.err_seqsum_lpn = []

    self.all_seqsum_per_block_lplbn = []  # anzahl der vollstaendigen Sequenzen pro block pro paradigma 
    self.cor_seqsum_per_block_lplbn = []  
    self.err_seqsum_per_block_lplbn = []

    self.all_seqtimesum_lplsn = []  # n = gesamtdauer pro Sequenz als liste
    self.cor_seqtimesum_lplsn = [] 
    self.err_seqtimesum_lplsn = []
    
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
    
    self.all_seqnum_per_block_slope_lpn = []  # n = Anstieg der REgressionsgeraden ueber die gesamtdauer pro Sequenz 
    self.cor_seqnum_per_block_slope_lpn = [] 
    self.err_seqnum_per_block_slope_lpn = []

    self.paradigmen = []        # description of the paradigms as list of strings
    self.sequence_length = []   # description of the paradigms as list of strings

    # netzwerkparameter fehlen hier noch


    def __init__(self, experiment, name, vorname, geb_datum, vpn, day):
        self.experiment = experiment
        self.name = name
        self.vorname = vorname
        self.geb_datum = geb_datum
        self.vpn = vpn
        self.day = day



    @property
    def all_ipi_lblsln(self):
        return self.__ipi_all_no_paradigm

    @all_ipi_lblsln.setter
    def all_ipi_lblsln(self, val):
        self.__all_ipi_lblsln = self.check_list_of_lists_of_numbers(val) #lxln







    def check_list_of_lists_of_numbers(self, val)
        """  [                   # list of ... 
            [1.1, 1.2, 0.9, 0.8] # interpres intervalls
            [1.1, 1.2, 0.9, 0.8]
        ]
        """
        if not isinstance(val,list):
            print("ipi_all have to be a list of lists with inter_press_interval_times")
            raise Exception("ipi_all have to be a list of lists with inter_press_interval_times")
            return
        ipi_all = []

        for seq_list in val:
            if not isinstance(seq_list, list):
                print("ipi_all have to be a list of lists with inter_press_interval_times")
                raise Exception("ipi_all have to be a list of lists with inter_press_interval_times")
            new_seq_list = []
            for num in seq_list:
                if isinstance(num, float):
                    new_num = int(num*1000)
                elif num.is_integer():
                    new_num = num
                else:
                    print("numbers are not float or integers")
                    raise Exception("numbers are not float or integers")
                new_seq_list.append(new_num)

            ipi_all.append(new_seq_list)
        return ipi_all

        