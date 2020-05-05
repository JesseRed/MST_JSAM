import numpy as np
import pandas as pd
def tolist_ck(A):
    ''' Funktion wandelt in ein json serializeable format um
        d.h. arrays werden zu listen
        einfaches np.array kann einfach mit a.tolist() umgewandelt werden
        bei in listen verschachtelten Arrays funktioniert das nicht
        dieser Fall wird durch diese Funktio abgedeckt. 
    '''
    if isinstance(A, np.ndarray):
        return A.tolist()        
    elif isinstance(A,list):
        B = []
        for e in A:
            B.append(tolist_ck(e))
            # if isinstance(e, np.ndarray):
            #     B.append(e.tolist())
        return B
    elif isinstance(A, np.float32):
        return np.float(A)
    elif isinstance(A, np.int8):
         return np.int(A)
    else:
        return A


def create_standard_df():
    df = pd.DataFrame(columns=['BlockNumber',  'SequenceNumber', 'EventNumber', 'Time Since Block start', 'isHit',
        'target', 'pressed', 'sequence'])
    return df

# def write_to_df_log(logfile, exp, ipi):
#     current_element = 0
#     with open(logfile, 'w') as fp:
#         idx  = 0
#         for l1 in exp:
#             for l2 in l1:
#                 idx += 1
#                 s +=1
#                 if s>
#                 fp.write(f"{l2} - {ipi[z,s]}")