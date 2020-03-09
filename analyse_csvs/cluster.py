import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import seaborn as sns
from os import listdir, rename
import os
from os.path import isfile, join
from statistics import mean, stdev
import statistics
import scipy
from mst import MST
from srtt import SRTT
from sim import SIM
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch


class Cluster():
    def __init__(self, ipi, dir_to_save = ".\\Data_python\\Data_Clustering",
                    is_save_to_file = True, is_show_images = False):
        # ipi ist die einzige wichtige Information
        # InterPressIntervalle shape = (Sequencelaenge x Sequenzanzahl)
        self.c = self.clustering()

    def clustering(self):
        ipi = self.ipi
    

        c = abs(np.corrcoef(ipi.T))
        c = np.nan_to_num(c)
        # c2 = np.zeros((ipi.shape[1],ipi.shape[1]))
        # for i in range(ipi.shape[1]):
        #     for j in range(ipi.shape[1]):
        #         c2[i,j], _ = pearsonr(ipi[:,i],ipi[:,j])
        # sns.heatmap(c2, annot = True)


                


        plt.figure(figsize=(10, 7))  
        plt.title("Dendrograms")  
        #print(c)
        dendrogram = sch.dendrogram(sch.linkage(c, method='ward'))
        plt.axhline(y=6, color='r', linestyle='--')
        plt.show()

        model = AgglomerativeClustering(n_clusters=5, affinity='euclidean', linkage='ward')
        model.fit(c)
        labels = model.labels_
        for i in range(c.shape[0]):
            c[i,i]=0
        if self.is_show_images:

            X=c
            sns.heatmap(c)
            print(f"c..... ")
            print(f"{np.array2string(c, precision=2, separator = ' ')}")
            print(f"--------------")

            plt.scatter(X[labels==0, 0], X[labels==0, 1], s=50, marker='o', color='red')
            plt.scatter(X[labels==1, 0], X[labels==1, 1], s=50, marker='o', color='blue')
            plt.scatter(X[labels==2, 0], X[labels==2, 1], s=50, marker='o', color='green')
            plt.scatter(X[labels==3, 0], X[labels==3, 1], s=50, marker='o', color='purple')
            plt.scatter(X[labels==4, 0], X[labels==4, 1], s=50, marker='o', color='orange')

            plt.show()
    