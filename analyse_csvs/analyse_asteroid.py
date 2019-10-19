import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns

df = pd.read_csv("./analyse_csvs/test_asteroid_01.csv", sep = ';')

print(df.head())

# print(df.iloc[[1],[1]]) # indexing by position

# print(df.loc[[1],['time']]) # indexing by name 

# print(df.ix[2]) # indexing by row-number

df['XDist'] = abs(df.xPos - df.xPosAsteroid)

#print(df.head())

#plt.figure()

df.plot( x = 'time', y = 'XDist' )
plt.show()

#for index, row in df.iterrows():
    #print(row['xPos'], row['yPos'])
 #   pass

