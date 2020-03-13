import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from os import listdir, rename
from os.path import isfile, join
from statistics import mean, stdev
import statistics
import networkx
import time
from matplotlib import pyplot as plt
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch
from filehandler import FileHandler
from network import Network
from helper_functions import tolist_ck

class SRTT():
    def __init__(self, fullfilename = ".\\Data MST\\3Tag1_.csv", path_output = ".\\Data_python", _id = "no_id"):
        self.fullfilename = fullfilename
        base=os.path.basename(self.fullfilename)
        self.filename = os.path.splitext(base)[0]
        self.path_output = path_output
        self._id = _id
        self.filehandler = FileHandler(path_output=self.path_output, filename = self.filename, time_identifier = _id)
        
        self.df = pd.read_csv(self.fullfilename, sep = '\t' )
        self.rts_nr, self.ipi_nr, self.but_nr = self.get_data_from_sequences(self.df,is_random=False)
        self.rts_ra, self.ipi_ra, self.but_ra = self.get_data_from_sequences(self.df, is_random=True)
        self.rts_cv_seq = self.get_rt_change_variable_sequence(self.rts_nr,self.rts_ra)# response time change variable
        self.rts_cv_but = self.get_rt_change_variable_button(self.rts_nr,self.rts_ra, self.but_nr, self.but_ra)# response time change variable
        

    def clustering(self,rts_cv):
        c = abs(np.corrcoef(rts_cv.T))
        # print(c.shape)
        # plt.figure(figsize=(10, 7))  
        # plt.title("Dendrograms")  
        # dendrogram = sch.dendrogram(sch.linkage(c, method='ward'))
        # plt.axhline(y=6, color='r', linestyle='--')
        # plt.show()

        model = AgglomerativeClustering(n_clusters=5, affinity='euclidean', linkage='ward')
        model.fit(c)
        labels = model.labels_
        # for i in range(c.shape[0]):
        #     c[i,i]=0
        # X=c

        # plt.scatter(X[labels==0, 0], X[labels==0, 1], s=50, marker='o', color='red')
        # plt.scatter(X[labels==1, 0], X[labels==1, 1], s=50, marker='o', color='blue')
        # plt.scatter(X[labels==2, 0], X[labels==2, 1], s=50, marker='o', color='green')
        # plt.scatter(X[labels==3, 0], X[labels==3, 1], s=50, marker='o', color='purple')
        # plt.scatter(X[labels==4, 0], X[labels==4, 1], s=50, marker='o', color='orange')

        # plt.show()
    def save(self):
        mydict = self.create_dict()
        self.filehandler.write(mydict)

    
    def create_dict(self):
        ''' generating a dictionary with all available information of this class
        '''
        mydict = {
            'experiment' :              'SRTT',
            'rts_cv_seq' :              tolist_ck(self.rts_cv_seq),
            'rts_cv_but':               tolist_ck(self.rts_cv_but)            
        }
        # ergaenze die Network Daten falls vorhanden
        if hasattr(self,'net'):
            net_dict = self.net.get_results_as_json()
            mydict.update(net_dict)
        return mydict 

    def add_network_class(self, coupling_parameter = 0.03,  resolution_parameter = 0.9,is_estimate_clustering= True, is_estimate_Q= False, num_random_Q=0):
        self.net = Network(self.rts_cv_but, coupling_parameter = coupling_parameter,  resolution_parameter = resolution_parameter,is_estimate_clustering= is_estimate_clustering, is_estimate_Q= is_estimate_Q, num_random_Q=num_random_Q)
        self.net.filename = self.fullfilename


    def get_rt_change_variable_sequence(self,rts_nr, rts_ra):
        ''' getting the response times (rts) and inter_key intervals (ipis)
        Boyed 2009 
            First, subtracting RTs of individual elements in random sequences from the elements
            in repeated sequences for each participant derived a change score
            variable. 
            ... es bleibt unklar ob ein "element" immer der gleiche Button ist
                oder die gleiche Position in der Sequenz
                ->ich mache erstmal die sequenzposition
        '''
        mean_ra = np.rint(np.mean(rts_ra, axis = 0)).astype(int)
        rts_cv = rts_nr-mean_ra
        # ich moechte nur positive WErte
        rts_cv = rts_cv + rts_cv.min()
        return rts_cv

    def get_rt_change_variable_button(self,rts_nr, rts_ra, but_nr, but_ra):
        ''' getting the response times (rts) and inter_key intervals (ipis)
        Boyed 2009 
            First, subtracting RTs of individual elements in random sequences from the elements
            in repeated sequences for each participant derived a change score
            variable. 
            ... es bleibt unklar ob ein "element" immer der gleiche Button ist
                oder die gleiche Position in der Sequenz
                ->ich mache erstmal die sequenzposition
        '''
        mean_ra_but_1 =  np.rint(np.mean(rts_ra[but_ra==1],axis=0)).astype(int)
        mean_ra_but_2 =  np.rint(np.mean(rts_ra[but_ra==2],axis=0)).astype(int)
        mean_ra_but_3 =  np.rint(np.mean(rts_ra[but_ra==3],axis=0)).astype(int)
        mean_ra_but_4 =  np.rint(np.mean(rts_ra[but_ra==4],axis=0)).astype(int)
        rts_cv = rts_nr
        rts_cv[but_nr==1]=rts_nr[but_nr==1]-mean_ra_but_1
        rts_cv[but_nr==2]=rts_nr[but_nr==2]-mean_ra_but_2
        rts_cv[but_nr==3]=rts_nr[but_nr==3]-mean_ra_but_3
        rts_cv[but_nr==4]=rts_nr[but_nr==4]-mean_ra_but_4
        # ich moechte nur positive Werte
        rts_cv = rts_cv + rts_cv.min()
        return rts_cv

    def get_data_from_sequences(self,df,is_random=False):
        ''' getting the response times (rts) and inter_key intervals (ipis)
        Boyed 2009 
            First, subtracting RTs of individual elements in random sequences from the elements
            in repeated sequences for each participant derived a change score
            variable. 
        '''
        selector = ('random' if is_random else 'fixed')
        # loesche die random
        df =df[df['type']==selector]
        ipi_cor = [] # correct sequences 
        rts_cor = []
        but_cor = []
        num_miss =1
        rts = []
        but = []
        buttons = []
        old_time = -1
        ipi = [] # temporaeres speichern einer Sequenz 
        for idx,row in df.iterrows():
            #print(f"idx= {idx}")
            rts.append(row['RT_1'])
            but.append(row['Button'])
            if old_time>0:
                #print(f"append with idx = {idx} and old_time= {old_time}")
                ipi.append(row['time']-old_time)
            old_time = row['time']
            
            if row['trial']%12==0: # sequenz fertig ... in den random steht bei sequenz immer 1 und trials werden hochgezaehlt
                
                if num_miss ==0: # wir speichern nur correcte Sequenzen
                    ipi_cor.append(ipi)
                    rts_cor.append(rts)
                    but_cor.append(but)
                old_time = -1
                rts = []
                ipi = []
                but = []
                num_miss = 0
        
        return (np.asarray(rts_cor), np.asarray(ipi_cor), np.asarray(but_cor))
        
    def estimate_improvement(self):
        X = [1,2,3,4,5,6,7,8,9,10,11,12]
        if not hasattr(self,'corrsq'):
            self.estimate_correct_seqences()
        improvement,b = np.polyfit(X, self.corrsq, 1)
        return improvement
        

if __name__ == '__main__':
    filename = ".\\Data MST\\3Tag1_.csv"
    filename = "H:\\Unity\MST_JSAM\\analyse_csvs\\Data_SRTT\\03_3_SRTT_2020-02-05_09-06-38.txt"
    filename = ".\\Data_SRTT\\03_3_SRTT_2020-02-05_09-06-38.txt"
    filename = ".\\Data_SRTT\\04_2_SRTT_2020-02-06_12-17-15.txt"
    df = pd.read_csv(filename, sep = '\t' )
    srtt = SRTT(filename)
    srtt.clustering(srtt.rts_cv_seq)
    srtt.clustering(srtt.rts_cv_but)
        
    
    '''
    To assess the chunking of elements, we first conducted an
    exploratory cluster analysis (Everitt, 1993), to identify groups of
    elements (i.e., chunks) within the sequence that were similar to
    one another based on the response time variable. First, subtracting
    RTs of individual elements in random sequences from the elements
    in repeated sequences for each participant derived a change score
    variable. Since we had no a priori estimate of the number of clusters 
    that would be present in each sequence (HC vs. ST), we employed a hierarchical approach to these analyses (Everitt, 1993).
    We applied a hierarchical agglomerative clustering algorithm to
    iteratively merge smaller clusters into larger clusters, based on a
    specified measure of proximity (Fukuoka, Lindgren, Rankin, Cooper, & Carroll, 2007). 
    As the element variable was the unit of analysis, variable clusters were identified using absolute values of the
    Pearson correlation coefficient as the measure of similarity. With
    12 elements in the sequence, the range of clusters was defined as
    a minimum of 2 to a maximum of 12 (i.e., one for each element).
    To combine clusters at each stage, we used Ward’s Method (Ward,
    1963), which first calculates the means for all variables and then
    generates and sums the squared Euclidean distance to the cluster
    means. At each stage, clusters with the smallest increase in
    summed distance are merged. This analysis yielded a number of
    potential variable cluster solutions, ranging from 12 to 2 groups
    of variables. Although one of the limitations of cluster analysis is
    the subjective selection of the optimal solution (Overall & Magee,
    1992), we used a combination of the distance between the values
    of coefficients in the agglomeration schedule (Mojena & Wishart,
    1980) and inspection of the icicle plot for the variable cluster that
    appeared to be the most consistent across all clustering stages, to
    identify the optimal solution for our analysis.
    To determine if these clusters represented significant groupings
    of elements (i.e., chunks), we next conducted paired t-tests to pinpoint 
    the locus of significant differences in individual elements for
    the two response types. Because random sequences cannot be
    chunked, significant differences between the two response types
    revealed elements of the repeated sequence that were grouped together. 
    Paired t-tests were performed between an average random
    measure for each element (Day 1 random + Day 2 random + Day 3
    random/3) and mean RTs from each of the 12 sequence elements
    from the first practice block and the retention block. To account
    for multiple t-tests in this procedure we employed a Bonferroni
    correction, resulting in a corrected critical p-value of p = .004.
    Once significant chunks were identified, we then sought to confirm that 
    the basal ganglia played an integral role in the process of
    chunking during motor sequence learning. As described above,
    previous work has shown that response times for the first element
    in a chunk may reflect the time to plan the entire response, while
    subsequent, faster, responses to elements in the sequence may represent 
    the time to execute the movement (Shea et al., 2006). Thus,
    we would expect that, if damage to the basal ganglia is associated
    with differences in the ability to chunk motor sequences, response
    times would differ for initial vs. final sequence elements in individuals 
    with stroke compared to healthy participants. Due to unequal
    variances, we conducted a Mann-Whitney test between the
    groups, to compare reaction times for the initial elements within
    each ‘‘chunk” and we conducted an independent samples t-test between groups, 
    examining reaction times for the final elements
    within each chunk. Importantly, only those individuals with confirmed basal 
    ganglia lesions (from Fig. 1) were included in these
    analyses.
    '''