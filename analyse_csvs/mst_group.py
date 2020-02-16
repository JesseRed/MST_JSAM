import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from os import listdir, rename
from os.path import isfile, join
from mst import MST
from scipy import stats 

class MST_Group():
    def __init__(self, mypath="./Data MST", filepattern="Tag1"):
        self.mypath = mypath
        self.filepattern = filepattern
        self.files = self.get_group_files()
        self.mst = []
        self.get_data()
        
    def get_group_files(self):
        file_list = []
        for file in os.listdir(self.mypath):
            if self.filepattern in file:
                file_list.append(os.path.join(self.mypath, file))
        return file_list

    def get_data(self):
        """ get data from every mst.csv file
        """            
        self.improvement = []
        self.corrsq = []
        for filename in self.files:
            mst = MST(filename)
            self.mst.append(mst)
            self.corrsq.append(mst.corrsq)
            self.improvement.append(mst.improvement)



        print(f"cor = {self.improvement}")
        print(f"improvement = {self.improvement}")
        print(f"mittelwert der improvement = {np.mean(self.improvement)}")
        print(f"Standardabweichung der lersteigung = {np.std(self.improvement)}")

if __name__ == '__main__':
    print(f"Gruppe 1")
    mst_group1 = MST_Group(mypath= "./Data MST", filepattern="Tag1")
    mst_group1.get_data()
    print(f"Gruppe 2")
    mst_group2 = MST_Group(mypath= "./Data MST", filepattern="Tag2")
    mst_group2.get_data()

    print(mst_group1.corrsq)

    statistic, pval = stats.ttest_ind(mst_group1.corrsq, mst_group2.corrsq)
    print(f"statistic = {statistic}")
    for i in pval:
        print(f"Block[i+1] - pval = {i:.4}")
