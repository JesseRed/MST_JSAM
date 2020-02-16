import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from os import listdir, rename
from os.path import isfile, join
from mst import MST
from mst_group import MST_Group
from scipy import stats 

class MST_Exp():
    def __init__(self, group1_path= "./Data MST", group1_filepattern="Tag1", group2_path= "./Data MST", group2_filepattern="Tag2" ):
        self.group1_path = group1_path
        self.group1_filepattern = group1_filepattern
        self.group2_path = group2_path
        self.group2_filepattern = group2_filepattern
        self.mst_g1 = MST_Group(mypath= self.group1_path, filepattern=self.group1_filepattern)
        self.mst_g2 = MST_Group(mypath= self.group2_path, filepattern=self.group2_filepattern)

    def perform_statistics(self):
        self.statistic, self.pval = stats.ttest_ind(self.mst_g1.corrsq, self.mst_g2.corrsq)
        print(f"statistic = {self.statistic}")
        for index, p in enumerate(self.pval):
            print(f"Block[{index+1}] - pval = {p:.4}")

    def plot(self):
        # https://matplotlib.org/gallery/statistics/violinplot.html#sphx-glr-gallery-statistics-violinplot-py

if __name__ == '__main__':
    experiment = MST_Exp(group1_path= "./Data MST", group1_filepattern="Tag1", group2_path= "./Data MST", group2_filepattern="Tag2")
    experiment.perform_statistics()
    experiment.plot()
    

    