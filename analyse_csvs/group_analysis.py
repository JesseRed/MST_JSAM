import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from os import listdir, rename
from os.path import isfile, join
from mst import MST
from group import Group
from scipy import stats 
from myplots import my_violinplot, set_axis_style
from my_statistics import cohend

class Group_analysis():
    def __init__(self, group1_path= "./Data MST", group1_filepattern="Tag1", group2_path= "./Data MST", group2_filepattern="Tag2" ):
        self.group1_path = group1_path
        self.group1_filepattern = group1_filepattern
        self.group2_path = group2_path
        self.group2_filepattern = group2_filepattern
        self.mst_g1 = MST_Group(mypath= self.group1_path, filepattern=self.group1_filepattern)
        self.mst_g2 = MST_Group(mypath= self.group2_path, filepattern=self.group2_filepattern)

    def add_group(self):
        print("adding additional groups for the analysis")

    def perform_statistics(self):
        self.statistic, self.pval = stats.ttest_ind(self.mst_g1.corrsq, self.mst_g2.corrsq)
        #print(f"statistic = {self.statistic}")
        for index, p in enumerate(self.pval):
            print(f"Block[{index+1}] - pval = {p:.4}")

        cd = cohend(np.asarray(self.mst_g1.corrsq[0]), np.asarray(self.mst_g2.corrsq[0]))
        print(f"CohensD={cd:.3f}")
        

    def plot(self):
        # https://matplotlib.org/gallery/statistics/violinplot.html#sphx-glr-gallery-statistics-violinplot-py
        print(f"about to make beautiful violin plots")
        #print(self.mst_g1.corrsq) # list of lists of Probanden [correcte SEqenzen pro block] N x Bloecke
        #print(self.mst_g2.corrsq)
        my_violinplot(self.mst_g1.corrsq, self.mst_g2.corrsq)
        my_forestplot(self.mst_g1.corrsq, self.mst_g2.corrsq)
        

        
if __name__ == '__main__':
    experiment = Group_analysis(group1_path= "./Data MST", group1_filepattern="Tag1", 
                        group2_path= "./Data MST", group2_filepattern="Tag2")
    experiment.perform_statistics()
    #experiment.plot()
    

    