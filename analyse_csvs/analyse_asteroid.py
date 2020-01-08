import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, rename
from os.path import isfile, join


X = [1,2,3,4,5,6,7,8,9,10,11,12]
#df = pd.read_csv("./analyse_csvs/test_asteroid_01.csv", sep = ';')
mypath = "./Data MST"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
lernsteigung = []
for filename in onlyfiles:
    df = pd.read_csv(join(mypath,filename), sep = ';' )
    #print(df.head())
    corrsq=[]
    tmpcount=0
    num_sq=[]
    blcktmp=-1
    num_blck_ev=0
    num_blck_tmp=0
    durchschnitt_blck=[]
    for index, row in df.iterrows():
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
        if ((index+1)%5)==0:
            if tmpcount==5:
                corrsq[-1]=corrsq[-1]+1
            tmpcount=0
            num_sq[-1]=num_sq[-1]+1
    print(f"{corrsq}")   
    m,b = np.polyfit(X, corrsq, 1)
    lernsteigung.append(m)
    print(m)
    #print(f"In Block {blcktmp} ist Anzahl korrekter Sequenzen = {corrsq[-1]}/{num_sq[-1]}")
    #for idx, val in enumerate(durchschnitt_blck):
    #    print(f"Pro Block {idx+1} ist die Durschschnittszeit pro Anschlag = {val}")    
print(f"{lernsteigung}")
print(np.mean(lernsteigung))
print(np.std(lernsteigung))
# lockNumber;EventNumber;Time Since Block start;isHit;target;pressed
# print(df.iloc[[1],[1]]) # indexing by position

# print(df.loc[[1],['time']]) # indexing by name 

# print(df.ix[2]) # indexing by row-number

# df['XDist'] = abs(df.xPos - df.xPosAsteroid)

#print(df.head())

#plt.figure()

# df.plot( x = 'time', y = 'XDist' )
# plt.show()

#for index, row in df.iterrows():
    #print(row['xPos'], row['yPos'])
 #   pass

