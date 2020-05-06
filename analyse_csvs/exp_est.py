import numpy as np
import pandas as pd

""" hier sind der uebersichtlichkeit halber alle Berechnungsfunktionen der Klasse "Experiment" untergebracht
"""

def make2dlist_to_2darray(list):
    arr = np.array(list, dtype = np.int32)
    return arr

def estimate_seqnum_per_block_slope(lplblsn):
    seqtimesum_slope_lpn = []
    for lblsn in lplblsn: 
        abs_seq_num_per_block = []
        for lsn in lblsn:  
            abs_seq_num_per_block.append(len(lsn))
        seqtimesum_slope_lpn.append(estimate_slope(abs_seq_num_per_block))

    return seqtimesum_slope_lpn



def estimate_seqtimesum_slope_lpn(lplsn):
    seqtimesum_slope_lpn = []
    seqtimesum_to_max_slope_lpn = []
    for lsn in lplsn:
        if not lsn: # empty
            seqtimesum_slope_lpn.append(estimate_slope(lsn))
            seqtimesum_to_max_slope_lpn.append(estimate_slope(lsn))
        else:
            seqtimesum_slope_lpn.append(estimate_slope(lsn))
            min_pos = lsn.index(min(lsn))
            if min_pos>10:
                seqtimesum_to_max_slope_lpn.append(estimate_slope(lsn[:min_pos]))
                
            else:
                seqtimesum_to_max_slope_lpn.append(estimate_slope(lsn))

    return (seqtimesum_slope_lpn, seqtimesum_to_max_slope_lpn)



def estimate_seqtimesum_slope_lplbn(lplblsn):
    seqtimesum_slope_lpn = []
    seqtimesum_to_max_slope_lpn = []
    for p in lplblsn:
        average_seq_time_per_block = []
        for lsn in p:   # z.B. [6081, 4727, 4535, 4485, 4153, 3412]
            
            if len(lsn) == 0:
                average_seq_time_per_block.append(sum(lsn))
            else:
                average_seq_time_per_block.append(sum(lsn)/len(lsn))            
        seqtimesum_slope_lpn.append(estimate_slope(average_seq_time_per_block))
        min_pos = average_seq_time_per_block.index(min(average_seq_time_per_block))
        if min_pos>3:
            seqtimesum_to_max_slope_lpn.append(estimate_slope(average_seq_time_per_block[:min_pos]))
        else:
            seqtimesum_to_max_slope_lpn.append(estimate_slope(average_seq_time_per_block))

    return (seqtimesum_slope_lpn, seqtimesum_to_max_slope_lpn)




def estimate_slope(y):
    if len(y)<2:
        slope, b = None, None
    else:
        x = np.arange(len(y))
        slope,b = np.polyfit(x, y, 1)
    return (slope, b)


def estimate_seqsum(ipi_lplblsln):
    """ estimates parameter:
        input is    all_ipi_lplblsln oder
                    cor_ipi_lplblsln oder
                    err_ipi_lplblsln
        output entsprechend

        all_seqsum_lpn = []  # anzahl der vollstaendigen Sequenzen pro paradigma 
        all_seqsum_lplbn = []  # anzahl der vollstaendigen Sequenzen pro block pro paradigma 
        all_seqtimesum_lplsn = []  # n = gesamtdauer pro Sequenz als liste
        all_seqtimesum_lplblsn = []  # n = gesamtdauer pro Sequenz als liste
        
        oder 

        cor_seqsum_lpn = []  # Anzahl der vollstaendigen korrekten Sequenzen pro Paradigma
        cor_seqsum_lplbn = []  
        cor_seqtimesum_lplsn = [] 
        cor_seqtimesum_lplblsn = [] 
        
        oder 

        err_seqsum_lpn = []
        err_seqsum_lplbn = []
        err_seqtimesum_lplsn = []
        err_seqtimesum_lplblsn = []
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
            seqtimesum_lsn_single = []
            for seq in block:
                sum_in_paradigma += 1 
                seqtimesum_lsn.append(sum(seq))
                seqtimesum_lsn_single.append(sum(seq))
                
            seqtimesum_lblsn.append(seqtimesum_lsn_single)
            seq_sum_lbn.append(len(block))
        
        seq_sum_lplbn.append(seq_sum_lbn)
        seq_sum_lpn.append(sum_in_paradigma)
        seqtimesum_lplsn.append(seqtimesum_lsn)
        seqtimesum_lplblsn.append(seqtimesum_lblsn)


    return (seq_sum_lpn, seq_sum_lplbn, seqtimesum_lplsn, seqtimesum_lplblsn)


def generate_df_ipi(input_df):
    """ mache die Spalte Time von in Sequence Time zu einer ipi Zeit
        d.h. es wird immer nur die Zeit von einem Event zum naechsten angegeben
    """
    df = input_df.copy()

    elem_num_old = -1
    old_time = 0
    current_sequence = []
    for idx in range(df.shape[0]):
        elem_num = df.loc[idx,'EventNumber']
        row_time = df.loc[idx, 'Time']

        if elem_num<=elem_num_old:
            # neue Sequenz
            old_time = 0
        df.loc[idx, 'Time'] = row_time -old_time
        old_time = row_time
        elem_num_old = elem_num
            
    return df

def estimate_all_ipi_hits_lsln(df_input):
    """ estimate the interpress intervalls for correct as errors 
        as list of sequences of list of numbers ... the sequence stays constant

    
    BlockNumber	SequenceNumber	EventNumber	    Time      isHit	    target	pressed	 sequence
        1	        1	            1	        1831	    1	       4	    4	    0
        1	        1	            2	        2552	    1	       1	    1	    0
        1	        1	            3	        4483	    1	       3	    3	    0
        1	        1	            4	        5219	    1	       2	    2	    0
    """ 

    df = df_input.reset_index(drop = True) 
    all_ipi_lsln = []          #estimate_all_ipi_hits_lsln_lsln()
    cor_ipi_lsln = []
    err_ipi_lsln = []
    all_hits_lsln = []         #estimate_all_ipi_hits_lsln_lsln()

    elem_num_old = -1
    current_sequence = []
    current_sequence_hits = []
    
    for idx in range(df.shape[0]):
        elem_num = df.loc[idx,'EventNumber']
        if elem_num<=elem_num_old:
            #neue Sequenz
            #print(f"neue sequenc mit elem_num = {elem_num}, elem_num_old = {elem_num_old} current sequence = {current_sequence}")
            if current_sequence:
                all_ipi_lsln.append(current_sequence)
            if current_sequence_hits:
                all_hits_lsln.append(current_sequence_hits)
            # teste ob correct
            if sum(current_sequence_hits)==elem_num_old:
                if current_sequence:
                    cor_ipi_lsln.append(current_sequence)
            else:
                if current_sequence:
                    err_ipi_lsln.append(current_sequence)

            current_sequence = []
            current_sequence_hits = []
        current_sequence.append(df.loc[idx, 'Time'])
        current_sequence_hits.append(df.loc[idx, 'isHit'])
        elem_num_old = elem_num
    if current_sequence:
        all_ipi_lsln.append(current_sequence)
    if current_sequence_hits:
        all_hits_lsln.append(current_sequence_hits)
    # auch die letzte Sequence muss noch nach falsch und richtig geteilt werden
    if sum(current_sequence_hits)==elem_num_old:
        if current_sequence:
            cor_ipi_lsln.append(current_sequence)
    else:
        if current_sequence:
            err_ipi_lsln.append(current_sequence)
            
    return (all_ipi_lsln, cor_ipi_lsln, err_ipi_lsln, all_hits_lsln)         


def estimate_ipi_hits_lplblsln(df_ipi):
    df = df_ipi
    all_ipi_lplblsln = []        #estimate_all_ipi_hits_lglsln_lsln()
    cor_ipi_lplblsln = []
    err_ipi_lplblsln = []
    all_hits_lplblsln = []       #estimate_all_ipi_hits_lglsln_lsln()
    for current_paradigma in range(df['sequence'].min() ,df['sequence'].max()+1):
        df_paradigma = df[df['sequence']==current_paradigma]
        all_ipi_lblsln, cor_ipi_lblsln, err_ipi_lblsln, all_hits_lblsln = estimate_ipi_hits_lblsln(df_paradigma)
        if all_ipi_lblsln: 
            all_ipi_lplblsln.append(all_ipi_lblsln)
        if cor_ipi_lblsln:
            cor_ipi_lplblsln.append(cor_ipi_lblsln)
        if err_ipi_lblsln:
            err_ipi_lplblsln.append(err_ipi_lblsln)
        if all_hits_lblsln:
            all_hits_lplblsln.append(all_hits_lblsln)
    return (all_ipi_lplblsln, cor_ipi_lplblsln, err_ipi_lplblsln, all_hits_lplblsln)



def estimate_ipi_hits_lplsln(df_ipi):
    df = df_ipi
    all_ipi_lplsln = []        #estimate_all_ipi_hits_lglsln_lsln()
    cor_ipi_lplsln = []
    err_ipi_lplsln = []
    all_hits_lplsln = []       #estimate_all_ipi_hits_lglsln_lsln()
    for current_paradigma in range(df['sequence'].min() ,df['sequence'].max()+1):
        df_paradigma = df[df['sequence']==current_paradigma]
        all_ipi_lsln, cor_ipi_lsln, err_ipi_lsln, all_hits_lsln = estimate_all_ipi_hits_lsln(df_paradigma)
        if all_ipi_lsln:
            all_ipi_lplsln.append(all_ipi_lsln)
        if cor_ipi_lsln:
            cor_ipi_lplsln.append(cor_ipi_lsln)
        if err_ipi_lsln:
            err_ipi_lplsln.append(err_ipi_lsln)
        if all_hits_lsln:
            all_hits_lplsln.append(all_hits_lsln)
    return (all_ipi_lplsln, cor_ipi_lplsln, err_ipi_lplsln, all_hits_lplsln)

def estimate_ipi_hits_lblsln(df_ipi):
    df = df_ipi
    all_ipi_lblsln = []        #estimate_all_ipi_hits_lglsln_lsln()
    cor_ipi_lblsln = []
    err_ipi_lblsln = []
    all_hits_lblsln = []       #estimate_all_ipi_hits_lglsln_lsln()
    for current_block in range(df['BlockNumber'].min() ,df['BlockNumber'].max()+1):
        df_block = df[df['BlockNumber']==current_block]
        all_ipi_lsln, cor_ipi_lsln, err_ipi_lsln, all_hits_lsln = estimate_all_ipi_hits_lsln(df_block)
        if all_ipi_lsln:
            all_ipi_lblsln.append(all_ipi_lsln)
        if cor_ipi_lsln:
            cor_ipi_lblsln.append(cor_ipi_lsln)
        if err_ipi_lsln:
            err_ipi_lblsln.append(err_ipi_lsln)
        if all_hits_lsln:
            all_hits_lblsln.append(all_hits_lsln)
    return (all_ipi_lblsln, cor_ipi_lblsln, err_ipi_lblsln, all_hits_lblsln)

# def estimate_all_ipi_hits(self):
#     """ estimate the interpress intervalls for correct as errors 
#         as list of sequences of list of numbers
#     """
#     """ in einem numpy Array werden die inter Key intervalls gespeichert
#         die Zeit zum ersten key press entfaellt 
#         Liste von Arrays
#         # estimates ipi_lblsln, hits_lblsln, ipi_lsln, hits_lsln
#     """ 
#     df = df 
#     all_ipi_lplsln = []
#     cor_ipi_lplsln = []
#     err_ipi_lplsln = []
#     all_ipi_lplblsln = []
#     cor_ipi_lplblsln = []
#     err_ipi_lplblsln = []

#     hits_lsln = []
#     hits_lblsln = []
#     ipi_lsln = []
#     cor_ipi_lsln = []
#     err_ipi_lsln = []
#     ipi_lblsln = []
#     cor_ipi_lblsln = []
#     err_ipi_lblsln = []

#     for current_paradigma in range(df['sequence'].min(), df['sequence'].max()+1):
#         df_paradigma = df[df['sequence']==current_paradigma]
#         for current_block in range(df_paradigma['BlockNumber'].min() ,df_paradigma['BlockNumber'].max()+1):
#             df_block = df_paradigma[df_paradigma['BlockNumber']==current_block]
            
#             ipi_lsln_one_block = []
#             cor_ipi_lsln_one_block = []
#             err_ipi_lsln_one_block = []
#             hits_lsln_one_block = []
            
#             # ueber alle Sequenzen in einem Block
#             if not df_block.empty: # z.B. Block 7 in srtt ist empty
#                 for current_seq in range(df_block['SequenceNumber'].min(), df_block['SequenceNumber'].max()+1):
#                     df_sequence = df_block[df_block['SequenceNumber']==current_seq]
#                     seq_tmp_time = 0
#                     ipi_ln = []
#                     hits_ln = []
                
#                     # ueber die rows einer Sequenz
#                     for idx, row in df_sequence.iterrows():
#                         ipi_ln.append(row['Time']-seq_tmp_time)
#                         seq_tmp_time = row['Time']
#                         hits_ln.append(row['isHit'])
                    
                            
#                     ipi_lsln_one_block.append(ipi_ln)
#                     ipi_lsln.append(ipi_ln)
#                     hits_lsln_one_block.append(hits_ln)
#                     hits_lsln.append(hits_ln)

#                     if sum(hits_ln)==sequence_length:
#                         cor_ipi_lsln_one_block.append(ipi_ln)
#                         cor_ipi_lsln.append(ipi_ln)
#                     else:
#                         err_ipi_lsln_one_block.append(ipi_ln)
#                         err_ipi_lsln.append(ipi_ln)

#                 ipi_lblsln.append(ipi_lsln_one_block)
#                 cor_ipi_lblsln.append(cor_ipi_lsln_one_block)
#                 err_ipi_lblsln.append(err_ipi_lsln_one_block)
#                 hits_lblsln.append(hits_lsln_one_block)
#         all_ipi_lplsln.append(ipi_lsln)
#         all_ipi_lplblsln.append(ipi_lblsln)    
#         cor_ipi_lplsln.append(cor_ipi_lsln)
#         cor_ipi_lplblsln.append(cor_ipi_lblsln)    
#         err_ipi_lplsln.append(err_ipi_lsln)
#         err_ipi_lplblsln.append(err_ipi_lblsln)  





#     all_ipi_lsln = ipi_lsln         #estimate_all_ipi_hits_lglsln_lsln()
#     all_hits_lsln = hits_lsln         #estimate_all_ipi_hits_lglsln_lsln()

#     all_ipi_lblsln = ipi_lblsln       #estimate_all_ipi_hits_lglsln_lsln()
#     all_hits_lblsln = hits_lblsln       #estimate_all_ipi_hits_lglsln_lsln()

#     all_ipi_lplsln = all_ipi_lplsln
#     cor_ipi_lplsln = cor_ipi_lplsln 
#     err_ipi_lplsln = err_ipi_lplsln
        
#     all_ipi_lplblsln = all_ipi_lplblsln
#     cor_ipi_lplblsln = cor_ipi_lplblsln
#     err_ipi_lplblsln = err_ipi_lplblsln

#     return 


# # @property
# # def all_ipi_lblsln(self):
# #     return __all_ipi_lblsln

# # @all_ipi_lblsln.setter
# # def all_ipi_lblsln val):
# #     __all_ipi_lblsln = check_list_of_lists_of_lists_of_numbers(val) #lxln









def check_list_of_list_of_lists_of_lists_of_numbers(val):
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
        liste = check_list_of_lists_of_lists_of_numbers(any)
        new_liste.append(liste)
    return new_liste


def check_list_of_lists_of_lists_of_numbers(val):
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
        liste = check_list_of_lists_of_numbers(any)
        new_liste.append(liste)
    return new_liste

def check_list_of_lists_of_numbers( val):
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
        liste = check_list_of_numbers(any)    
        new_liste.append(liste)
    return new_liste

def check_list_of_numbers( liste):
    if not isinstance(liste, list):
        print("liste has to be a list ")
        raise Exception("ipi_all have to be a list of lists with inter_press_interval_times")
        return None
    new_liste = []
    for any in liste:
        num = check_of_number(any)
        new_liste.append(num)
    
    return new_liste

def check_of_number( num):

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
