import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, rename
from os.path import isfile, join
from mst import MST

class MST_Group():
    def __init__(self, mypath="./Data MST", filepattern="Tag1"):
        self.mypath = mypath
        self.filepattern = filepattern
        self.files = self.get_group_files()
        self.mst = []
        
    def get_group_files(self):
        file_list = []
        for file in os.listdir(self.mypath):
            if self.filepattern in file:
                file_list.append(os.path.join(self.mypth, file))
        return file_list

    def get_data(self):
        """ get data from every mst.csv file
        """            
        self.improvement = []
        self.corrsq = []
        for filename in onlyfiles:
            mst = MST(filename, mypath=mypath)
            mst.estimate_correct_seqences()
            mst.estimate_improvement()
            self.mst.append(mst)

            self.corrsq.append(mst.corrsq)
            self.improvement.append(mst.improvement)



        print(f"cor = {improvement}")
        print(f"improvement = {improvement}")
        print(f"mittelwert der improvement = {np.mean(improvement)}")
        print(f"Standardabweichung der lersteigung = {np.std(improvement)}")

if __name__ == '__main__':
    mst_group1 = MST_Group(mypath= "./Data_Rogens/MST", filepattern="REST1")
    mst_group2 = MST_Group(mypath= "./Data_Rogens/MST", filepattern="REST2")
    

