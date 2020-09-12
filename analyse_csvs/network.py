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
import networkx
import time, copy
from sim import SIM
import random
import pickle
import json
from datetime import datetime
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as sch
from helper_functions import tolist_ck
import logging

logger = logging.getLogger(__name__)

class Network():
    def __init__(self, ipi, coupling_parameter = 0.03,  resolution_parameter = 0.9, is_estimate_clustering= True, is_estimate_Q= False, num_random_Q=0 ):
        # whether in the adaptation process it will be tried to set the
        # node in the next trial to the same node of the previous
        print('starting Network init')
        self.is_adapt_communities_across_trials = False 
        self.is_estimate_clustering = is_estimate_clustering
        self.is_estimate_Q = is_estimate_Q
        self.num_random_Q = num_random_Q
        
        self.coupling_parameter = coupling_parameter
        self.resolution_parameter = resolution_parameter
        #logger.info(f"dimension in network get_normalized_2D_array {self.ipi}") 
        self.ipi = self.get_normalized_2D_array(ipi)
        # self.ipi now 2D np.array trials x sequence_elements (key presses per trial)
        
        #! all relevant Values are saved in lists .... starting with the variable namen and than list
        # IMPORTANT is that the real value of all estimations is the first one than the 
        # shuffeld ones following
#        self.ipi = self.convert_to_array2D(self.ipi_norm)
        self.A = self.get_adjacency_matrix(self.ipi) 
        self.A_list = []
        self.C = self.get_inter_slice_coupling(self.ipi, self.coupling_parameter)
        self.C_list = []
        self.delta_intra_slice = self.get_delta_intra_slice(self.A)
        self.delta_intra_slice_list = []
        self.delta_inter_slice = self.get_delta_inter_slice(self.C)
        self.delta_inter_slice_list = []

        self.c = np.sum(self.C, axis=2)  # checked 08.09.2020
        self.c_list = []
        self.k = np.sum(self.A, axis=0)  # checked 08.09.2020
        self.k_list = []
        self.kappa = self.k + self.c     # checked 08.09.2020
        self.kappa_list = []
        self.my2 = sum(sum(self.kappa))  # checked 08.09.2020
        self.my2_list = []
        self.m = np.sum(self.k, axis=0)  # checked 08.09.2020
        self.m_list = []
        self.gamma = np.zeros((self.A.shape[2]))+self.resolution_parameter  # checked 08.09.2020
        self.gamma_list = []
        self.ipi_list = []
        self.phi_list = []
        self.g_list = []
        self.Q_list = []
        

        if self.is_estimate_clustering:
            self.clustering()
        
        if self.estimate_Q:
            self.estimate_Q()
        
    def estimate_Q(self):
        # it is important that the estimation with real values comes first !!!!
        # the real values are the first entry in the list ... than the fake values following
        # self.estimate_chunks(is_random = False)
        # self.estimate_chunk_magnitudes(self.g_list[-1])
        # only after estimation of real Q than the estimation of fals Q is performed
        for i in range(self.num_random_Q):
            self.estimate_chunks(is_random=True)
            self.estimate_chunk_magnitudes(self.g_list[-1])
        # muss hier wieder weg nur zum testen
        self.estimate_chunks(is_random = False)
        self.estimate_chunk_magnitudes(self.g_list[-1])

        self.q_real_t, self.q_real_p = scipy.stats.ttest_1samp(self.Q_list[1:],self.Q_list[0])
        self.print_results(print_shuffled_results = (self.num_random_Q>0))


    def get_normalized_2D_array(self, ipi):
        ''' checking and preparing of input data
                check whether ipi is a 3D list (mst) or a 2D array (SRTT)
            if list than changing into 2D array
            then normalizing as suggested by Wymbs 2013 (deleting trails with std>3)
        '''
        # umwandlung in np.ndarray fals als liste uebergeben
        ipi_arr = (ipi if isinstance(ipi, np.ndarray) else self.convert_to_array2D(ipi))
        
        # logger.info(self.ipi_arr.shape)
        m, std = self.get_ipi_mean_arr(ipi_arr)
        # self.ipi_norm = self.get_normalized_ipi(ipi, m, std)
        ipi_norm_arr = self.get_normalized_ipi_arr(ipi_arr, m, std)
        return ipi_norm_arr

    # checked CK 07.09.2020
    def shuffle(self, ipi_org):
        ipi = copy.deepcopy(ipi_org) 
        for i in range(ipi.shape[0]):
            random.shuffle(ipi[i,:])
        return ipi

    # checked CK 07.09.2020
    def shuffle2D(self, ipi):
        for i in range(ipi.shape[0]):
            random.shuffle(ipi[i,:])
        for j in range(ipi.shape[1]):
            random.shuffle(ipi[:,j])
            
        return ipi
        
    def estimate_chunk_magnitudes(self, g):
        '''
        To determine the modularity of each trial separately (Qsingle–trial) we computed the modularity
        function Q given in Equation (1) using the partition assigned to that trial by Qmulti–trial.
        
        Chunk magnitude (ϕ) is defined as 1/Qsingle–trial. Low values of ϕ correspond to trials with
        greater segmentation, which are computationally easier to split into chunks and high values
        of ϕ correspond to trials with greater chunk concatenation, which contain chunks that are
        more difficult to computationally isolate. We normalized the values of ϕ across correct trials
        for each frequent sequence: (Wymbs et al. 2013)
        
        '''
        logger.info("estimating chunk magnitudes")
        #logger.info(g.T)
        # erzeuge Zufallskonfiguration fuer P ... Null model
        ipi_shuffled = self.shuffle(self.ipi)
#        P = self.get_adjacency_matrix(ipi_shuffled)
        phi = []
        for slice in range(g.shape[1]):
            Q_st = self.estimate_Q_st(g[:,slice],self.A[:,:,slice], self.get_null_model_P(self.A[:,:,slice]))
            # Berechnung von P entsprechend von paper Newman and Girvan 2004
            # wenn es keine Chunks in einem Layer gibt kann Q_st auch null sein
            phi.append(1/Q_st)
        #normalization
        phi_arr = np.asarray(phi)
        phi_arr[np.isinf(phi_arr)]=np.NaN
        m = np.nanmean(phi_arr)
        logger.info(f"chunk magnitude m = {m}")
        for i in range(phi_arr.shape[0]):
            phi_arr[i]=(phi_arr[i]-m)/m

        self.phi = phi_arr.tolist()
        self.phi_list.append(self.phi)
        return


    def estimate_Q_st(self, trial, W, P):
        # Berechnung nach Porter 2009 
        summe = 0
        for i in range(W.shape[0]):
            for j in range(W.shape[1]):
                summe = summe +(W[i,j]-P[i,j])*self.get_delta_2d(trial[i],trial[j])

        summe = summe / sum(sum(W))
        return summe
    
    def get_delta_2d(self,gi,gj):
        ret = (1 if gi==gj else 0)
        return ret

    def get_null_model_P(self, A):
        ''' Berechnung von P entsprechend von paper Newman and Girvan 2004
        '''
        P = np.zeros((A.shape[0],A.shape[1]))
        w = sum(sum(A))/2
        for i in range(A.shape[0]):
            ki = sum(A[i,:])
            for j in range(A.shape[1]):
                kj = sum(A[:,j])
                P[i,j] = (ki * kj) / 2*w
        return P


    def initialize_variables_for_new_Q_estimation(self, is_random):
        if is_random:
            current_ipi = self.shuffle(self.ipi)
        else:
            current_ipi = self.ipi
    
        self.ipi_list.append(current_ipi)
        self.A = self.get_adjacency_matrix(current_ipi)
        
        self.C = self.get_inter_slice_coupling(current_ipi, self.coupling_parameter)
        self.delta_intra_slice = self.get_delta_intra_slice(self.A)
        self.delta_inter_slice = self.get_delta_inter_slice(self.C)
        self.c = np.sum(self.C, axis=2)  # checked 08.09.2020
        self.k = np.sum(self.A, axis=0)  # checked 08.09.2020
        self.kappa = self.k + self.c     # checked 08.09.2020
        self.my2 = sum(sum(self.kappa))  # checked 08.09.2020
        self.m = np.sum(self.k, axis=0)  # checked 08.09.2020
        self.gamma = np.zeros((self.A.shape[2]))+self.resolution_parameter  # checked 08.09.2020
        self.g = self.initialize_g() # jedes node ist seine eigene community

    def estimate_chunks(self, is_random=False):
        ''' A ist die Adjacency matrix anhand der die Berechnung der chunks
            erfolgt. Diese kann dann auch durch die Random Adjacency matrix 
            ersetzt werden.
        '''
        self.initialize_variables_for_new_Q_estimation(is_random)

        start = time.time()
        Qms_old = self.get_Qms_opt(self.g, self.A)
        logger.info(f"Qms execution time = {time.time()-start:.3} s")
        idx = 0
        while True:
            idx +=1
            start = time.time()
            self.g = self.adapt_communities(self.g, self.A)
            Qms = self.get_Qms_opt(self.g, self.A)
            if Qms<=Qms_old:
                break
            else:
                Qms_old=Qms
#            logger.info(g.T)
            logger.info(f"------------------------------------------")
            logger.info(f"----------Durchlauf = {idx} --------------")
            logger.info(f"postadapt ... unique elements in g: {np.unique(self.g).shape[0]}")
            logger.info(f"adapt_communities execution time = {time.time()-start:.3} s")                    
            logger.info(f"durchlauf={idx} mit Qms = {Qms}")
        Qms = self.get_Qms_opt(self.g, self.A)
        logger.info(f"Final Qms = {Qms}")
        self.Qms = Qms
        """ save the estimated Valued for possible further analysis"""
        self.save_Variables()
        
    
    def save_Variables(self):
        self.A_list.append(self.A)
        self.C_list.append(self.C)
        self.delta_intra_slice_list.append(self.delta_intra_slice)
        self.delta_inter_slice_list.append(self.delta_inter_slice)
        self.c_list.append(self.c)
        self.k_list.append(self.k)
        self.kappa_list.append(self.kappa)
        self.my2_list.append(self.my2)
        self.m_list.append(self.m)
        self.gamma_list.append(self.gamma)
        self.g_list.append(self.g)
        self.Q_list.append(self.Qms)
            
        
    def adapt_communities(self,g, A):
        # Anpassung von g entsprechend dem Algorithmus von Blondel 2008
        # initialisiert wir mit jeder Node als eigene Community
        # g wird durchgegangen und g[i,s] wird in seiner community
        # ersetzt durch g[i-1,s] und g[i+1,s]
        # wenn sich eine Verbesserung einstellt dann wird die neue
        # Zuordnung beibehalten

#        logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
 
        index = 0
        for s in range(g.shape[1]):
            for i in range(g.shape[0]):
                index+=1
                #logger.info(f"{i} ... unique elements in g: {np.unique(g).shape[0]}")
                #logger.info(f"{g[:,0]}")
                #logger.info(f"g[i,s]= {g[i,s]}")
                community_org = g[i,s]
                community_links = -1
                community_rechts = -1
                community_unten = -1
                q_org = self.get_Qms_opt(g,A)
                q_links = -999
                q_rechts = -999
                q_unten = -999
                #logger.info(f"original Q0 = {q_org}")
                if i>0:
                    if not g[i,s]==g[i-1,s]:
                        g[i,s] = g[i-1,s]
                        q_links = self.get_Qms_opt(g,A)

                        community_links = g[i,s]

                if i<g.shape[0]-1:
                    if not g[i,s]==g[i+1,s]:
                        g[i,s] = g[i+1,s]
                        q_rechts = self.get_Qms_opt(g,A)
                        community_rechts = g[i,s]

                #! nach unten oder nach oben?
                if self.is_adapt_communities_across_trials: 
                    if s<g.shape[1]-1:
                        if not g[i,s]==g[i,s+1]:
                            g[i,s] = g[i,s+1]
                            q_unten = self.get_Qms_opt(g,A)
                            community_unten = g[i,s]

                results = [q_org, q_links, q_rechts, q_unten]
                #logger.info(f"adapt communites results = {results}")
                g_communities = [community_org, community_links, community_rechts, community_unten]
                # ist Q wirklich immer positiv wenn es besser wird????
                g[i,s] = g_communities[results.index(max(results))] # die community zuordnung des maximums
   
                #self.g = g

        


        return g
        #logger.info(f"postadapt ... unique elements in g: {np.unique(g).shape[0]}")
                
                

    def initialize_g(self):
        # initialization with every node is a community
        g = np.arange(self.A.shape[0]*self.A.shape[2]).reshape(self.A.shape[0],self.A.shape[2])
        #g = self.shuffle(g)
        #g = np.ones((self.A.shape[0],self.A.shape[2]),dtype=int)
        return g
    
    def get_Qms_opt(self, g, A):



        summe =  0
        #start= time.time()
        for i in range(A.shape[0]):
            j_start = (i-1 if i>0 else i)
            j_stop = (i+2 if i<A.shape[0]-1 else i+1)
            for j in range(j_start,j_stop):
                for s in range(A.shape[2]):
                    r_start = (s-1 if s>0 else s)
                    r_stop = (s+2 if s<A.shape[2]-1 else s+1)
                    for r in range(r_start,r_stop):
                        x = A[i,j,s] - ((self.gamma[s]*self.k[i,s]*self.k[j,s])/(2*self.m[s]))
                        x = x * self.delta_inter_slice[s,r]
                        x = x + self.delta_intra_slice[i,j] * self.C[j,s,r]
                        x = x * self.get_delta_community(g[i,s],g[j,r])
                        summe = summe + x 
                        #if self.get_delta_community(g[i,s],g[j,r])>0:
                            #logger.info(self.get_delta_community(g[i,s],g[j,r]))
                        #if i==0:
                        #    logger.info(f"[i,j,s,r] = [{i},{j},{s},{r}]")
#                        if i==0 and j==1 and s==0 and r==0:
#                            logger.info(f"A[{i},{j},{s}]={A[i,j,s]}")
#                            xxx = ((gamma[s]*k[i,s]*k[j,s])/(2*m[s]))
#                            logger.info(f"gamma[s]*k[i,s]*k[j,s])/(2*m[s]) = {xxx}")
#                            logger.info(f"delta_inter_slice[{s},{r}]={delta_inter_slice[s,r]}")
#                            logger.info(f"delta_intra_slice[{i},{j}]={delta_intra_slice[i,j]}")
#                            logger.info(f"C[{j},{s},{r}]={C[j,s,r]}]")
#                            logger.info(f"self.get_delta_community(g[{i},{s}],g[{j},{r}]) = {self.get_delta_community(g[i,s],g[j,r])}")
#        
        Qms = 1/self.my2 * summe
        
        #logger.info(f"estimation time = {time.time()-start} s")
        return Qms
    
    def get_Qms_optx(self, g, i, s):
        A = self.A
        C = self.C
        logger.info(f"----------------------")
        logger.info(f"start estimate Qms")
        logger.info(f"{g[:,0]}")
        logger.info(f"{g[:,1]}")
        #logger.info(f"C.shape = {C.shape}")
        #logger.info("C")
        #logger.info(C)
        c = np.sum(C,axis=2)
        #logger.info("c")
        #logger.info(c)
        k = np.sum(A,axis=0)
        #logger.info("k")
        #logger.info(k)
        kappa = k + c
        #logger.info("kappa")
        #logger.info(kappa)
        my2 = sum(sum(kappa))
#        logger.info("my2")
#        logger.info(my2)
        m = np.sum(k, axis=0)
#        logger.info("m")
#        logger.info(m)
        gamma = np.zeros((A.shape[2]))+self.resolution_parameter
        delta_intra_slice = self.get_delta_intra_slice(A)
        delta_inter_slice = self.get_delta_inter_slice(C)
        
        summe =  0
        delta = 0
        start= time.time()
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                for s in range(A.shape[2]):
                    for r in range(C.shape[2]):
                        x = A[i,j,s] - ((gamma[s]*k[i,s]*k[j,s])/(2*m[s]))
                        x = x * delta_inter_slice[s,r]
                        x = x + delta_intra_slice[i,j] * C[j,s,r]
                        x = x * self.get_delta_community(g[i,s],g[j,r])
                        summe = summe + x 
                        #if self.get_delta_community(g[i,s],g[j,r])>0:
                            #logger.info(self.get_delta_community(g[i,s],g[j,r]))
                        if i==0 and j==1 and s==0 and r==0:
                            logger.info(f"A[{i},{j},{s}]={A[i,j,s]}")
                            xxx = ((gamma[s]*k[i,s]*k[j,s])/(2*m[s]))
                            logger.info(f"gamma[s]*k[i,s]*k[j,s])/(2*m[s]) = {xxx}")
                            logger.info(f"delta_inter_slice[{s},{r}]={delta_inter_slice[s,r]}")
                            logger.info(f"delta_intra_slice[{i},{j}]={delta_intra_slice[i,j]}")
                            logger.info(f"C[{j},{s},{r}={C[j,s,r]}]")
                            logger.info(f"self.get_delta_community(g[{i},{s}],g[{j},{r}]) = {self.get_delta_community(g[i,s],g[j,r])}")
        logger.info("summe")
        logger.info(summe)
        

        Qms = 1/my2 * summe
        logger.info(f"Qms = {Qms}")
        logger.info(f"estimation time = {time.time()-start} s")
        return Qms
    
    def get_delta_community(self, g1,g2):
        ''' g1 and g2 are two entries from the community numeration
            if g1==g2 then 1 else 0
        '''
        d = 0
        if g1==g2:
            d = 1
        return d
    
    def get_delta_intra_slice(self, A):
        delta_intra_slice = np.zeros((A.shape[0],A.shape[1]))
        for i in range(delta_intra_slice.shape[0]-1):
            delta_intra_slice[i,i+1]=1
            delta_intra_slice[i+1,i]=1
        return delta_intra_slice

    def get_delta_inter_slice(self, C):
        delta_inter_slice = np.zeros((C.shape[1],C.shape[2]))
        for s in range(delta_inter_slice.shape[0]-1):
            delta_inter_slice[s,s]=1
            delta_inter_slice[s+1,s+1]=1
            delta_inter_slice[s,s+1]=1
            delta_inter_slice[s+1,s]=1
        return delta_inter_slice

    def get_inter_slice_coupling(self, ipi, coupling_parameter):
        C = np.zeros((ipi.shape[1],ipi.shape[0],ipi.shape[0]))        
        #logger.info(f"C.shape = {C.shape}")
        for j in range(C.shape[0]):
            for s in range(C.shape[1]-1):
                C[j,s,s+1] = coupling_parameter                    
                C[j,s+1,s] = coupling_parameter # raus weil es geht nur vorwaerts in der Zeit
        return C                    
        
     
    
    def get_adjacency_matrix(self, ipi):
        # ipi ist eine N x M  Array  
        # i element N ist die slice 
        # j element M die Verbindung von
        # return als A[i,j,k] mit i,j die Verbindung in einer Slice und k die Slice
        A = np.zeros((ipi.shape[1],ipi.shape[1],ipi.shape[0]))
        for i in range(ipi.shape[0]): # across Slices
            m = max(ipi[i,:])
            for j in range(ipi.shape[1]-1):
                A[j,j+1,i]=(m-abs(ipi[i,j]-ipi[i,j+1]))/m
                A[j+1,j,i]=A[j,j+1,i]
        return A
    
    def convert_to_array2D(self, list3):
        if isinstance(list3[0],np.ndarray):
            y_mat = np.asarray(list3)
        else:
            y = []
            for block in list3:
                for sequence in block:
                    y.append(sequence)
            y_mat = np.stack(y)
        return y_mat # array der dimension N x M   (N anzahl der korrekten Sequenzen, M Anzahl der Elemente pro sequenz)
        
    def get_simple_weights(self, ipi):
        # estimates similarities in IKIs 
        w = []
        for i in range(ipi.shape[0]):
            d = np.zeros((ipi.shape[1],ipi.shape[1]))
            m = max(ipi[i,:])
            for j in range(ipi.shape[1]-1):
                d[j,j]=0.03
                d[j,j+1]=(m-abs(ipi[i,j]-ipi[i,j+1]))/m
            w.append(d)
    

    def get_ipi_mean_arr(self, ipi):
        mean_arr = ipi.mean(axis=0)
        std_arr = ipi.std(axis=0)

        return (mean_arr, std_arr)        
    
    def get_mean_list3(self, ipi):
        mean_list = []
        for block in ipi:
            for sequence in block:
                mean_list.append(sum(sequence) / len(sequence))
        m = sum(mean_list) / len(mean_list)
        std = stdev(mean_list)
        return (m, std)        

    def get_normalized_ipi(self, ipi, m, std):

        ipi_new = []
        for block in ipi:
            block_new = []
            for sequence in block:
                keep = True
                for idx, p in enumerate(sequence):
                    if p>m[idx]+std[idx]*3 or p<m[idx]-std[idx]*3 :
                        keep = False
                if keep:
                    block_new.append(sequence)
            ipi_new.append(block_new)
        return ipi_new

    def get_normalized_ipi_arr(self, ipi, m, std):

        ipi_new = np.zeros((ipi.shape[0],ipi.shape[1]))
        seq_num = 0
        for row_idx in range(ipi.shape[0]):
            keep = True
            for col_idx in range(ipi.shape[1]):
                if ipi[row_idx,col_idx]>m[col_idx]+std[col_idx]*3 or ipi[row_idx,col_idx]<m[col_idx]-std[col_idx]*3:
                   # dann uebertrage nicht
                   keep = False
            if keep:
                ipi_new[seq_num,:] = ipi[row_idx,:]
                seq_num +=1
        ipi_norm = ipi_new[:seq_num,:]
        return ipi_norm


    def printlist3(self, list3):
        for idx, x in enumerate(list3):
            logger.info(f"Block nummer: {idx+1}")
            for y in x:
                logger.info(y)
#               logger.info(type(y[0]))#
#                
    def get_delta_q(self,g, i, s):
        A = self.A
        C = self.C
        community = g[i,s]
        # Sin  ...sum of the weights of the links inside the community
        # Stot ...sum of the weights of the links incident to nodes in C
        Sin, Stot = self.get_sum_of_weights_within_a_community(A,C,g,community)
        # k_i_in ... sum of the weights of the links from i to nodes in the community
        # k_i    ... sum of the weights of the links incident to node i
        (k_i_in, k_i) = self.get_sum_of_weights_of_links_from_i_to_nodes_in_community(A,C,g,community, i)
        #sum of the weights of all the links in the network
        m = sum(sum(sum(A)))+sum(sum(sum(C)))
        
        #dq = 
        # gebe deltaQ zurueck
        return dq
    
   
#    def get_sum_of_weights_of_links_incident_to_node_i(A,C,g, community):
#        Ais = np.sum(A,axis=1) # i x s ... eliminating j ... entsprechend der symmetrischen Natur von A gibt es 2 links fuer jeden Node
#        Cis = np.sum(C,axis=2) # i x s ... eleminating r
#        Sin = Ais[g==community] + Cis[g==community]
#        return Sin   
   
   
    def get_sum_of_weights_of_links_from_i_to_nodes_in_community(self, A, C, g, community, fokus_node_i, fokus_node_s):
        # sum of the weights of the links from i to nodes in the community
        # es ist so implementiert, dass es auch berechnet wird wenn fokus_node gar nicht in der community liegt
        # in der aktuellen Anwendung sollte das aber der fall sein durch das setzen von community
        g_bool = g==community
        k_i_in = 0 # sum of the weights of the links from i to nodes in the community
        k_i = 0
        start_i = (0 if fokus_node_i==0 else fokus_node_i-1)
        end_i = (g.shape[0] if fokus_node_i==g.shape[0] else fokus_node_i+1)
        start_s = (0 if fokus_node_s==0 else fokus_node_s-1)
        end_s = (g.shape[1] if fokus_node_s==g.shape[1] else fokus_node_s+1)
        
        # in Schicht s nur nach vorn und hinten ... wenn start_i == fokus_node_i ist das egal da dann A = 0
        k_i_in = k_i_in + (A[start_i,fokus_node_s,fokus_node_s] if g_bool[start_i,fokus_node_s] else 0)
        k_i_in = k_i_in + (A[end_i,fokus_node_s,fokus_node_s] if g_bool[start_i,fokus_node_s] else 0)
        # in i nur nach vorn und hinten ... wenn start_s == fokus_node_s ist das egal da dann C = 0
        k_i_in = k_i_in + (C[fokus_node_i,start_s,fokus_node_s] if g_bool[fokus_node_i,start_s] else 0)
        k_i_in = k_i_in + (C[fokus_node_i,end_s,fokus_node_s] if g_bool[fokus_node_i,end_s] else 0)
        
        # in Schicht s nur nach vorn und hinten ... wenn start_i == fokus_node_i ist das egal da dann A = 0
        k_i = k_i + A[start_i,fokus_node_s,fokus_node_s] 
        k_i = k_i + A[end_i,fokus_node_s,fokus_node_s]
        # in i nur nach vorn und hinten ... wenn start_s == fokus_node_s ist das egal da dann C = 0
        k_i = k_i + C[fokus_node_i,start_s,fokus_node_s] 
        k_i = k_i + C[fokus_node_i,end_s,fokus_node_s]
        
        return (k_i_in, k_i)

    def get_sum_of_weights_within_a_community(self, A, C, g, community):
        g_bool = g==community
        Sin = 0 #sum of the weights of the links inside the community
        Stot = 0 #
        for s in range(g.shape[1]-1): # i
            for i in range(g.shape[0]-1):
                if g_bool[i,s]:
                    Stot = Stot + A[i,i+1,s]
                    if g_bool[i+1,s]:
                        # dann gehoeren zwei nebeneinander stehende nodes in eine community
                        Sin = Sin + A[i,i+1,s]
                    Stot = Stot + C[i,s,s+1]
                    if g_bool[i,s+1]:
                        # dann gehoeren zwei untereinander stehende nodes in eine community
                        Sin = Sin + C[i,s,s+1]
        return (Sin, Stot)
        
    def clustering(self):
        ipi = self.ipi
        logger.info('clustering ...')
        c = abs(np.corrcoef(ipi.T))
        c = np.nan_to_num(c)
        #sns.heatmap(c)
        c2 = np.zeros((ipi.shape[1],ipi.shape[1]))
        for i in range(ipi.shape[1]):
            for j in range(ipi.shape[1]):
                c2[i,j], _ = pearsonr(ipi[:,i],ipi[:,j])
        #sns.heatmap(c2, annot = True)

        # logger.info(f"c..... ")
        # logger.info(f"{np.array2string(c, precision=2, separator = ' ')}")
        # logger.info(f"--------------")
                


        plt.figure(figsize=(10, 7))  
        plt.title("Dendrograms")  
        #logger.info(c)
        dendrogram = sch.dendrogram(sch.linkage(c, method='ward'))
        plt.axhline(y=6, color='r', linestyle='--')
        plt.show()

        model = AgglomerativeClustering(n_clusters=5, affinity='euclidean', linkage='ward')
        model.fit(c)
        labels = model.labels_
        for i in range(c.shape[0]):
            c[i,i]=0
        X=c
        #sns.heatmap(c)
        # plt.scatter(X[labels==0, 0], X[labels==0, 1], s=50, marker='o', color='red')
        # plt.scatter(X[labels==1, 0], X[labels==1, 1], s=50, marker='o', color='blue')
        # plt.scatter(X[labels==2, 0], X[labels==2, 1], s=50, marker='o', color='green')
        # plt.scatter(X[labels==3, 0], X[labels==3, 1], s=50, marker='o', color='purple')
        # plt.scatter(X[labels==4, 0], X[labels==4, 1], s=50, marker='o', color='orange')

        # plt.show()




    def print_results(self, print_shuffled_results = True):
        ''' printing der relevanten Informationen
        '''
        logger.info(".....................")
        logger.info("---print relevant Information---")
        logger.info(f"inputfile = ")
        logger.info(f"Qmulti-trial = {self.Q_list[0]}")
        if print_shuffled_results:
            logger.info(f"Qmulti-trial = {self.Q_list[0]} (p = {self.q_real_p}, t = {self.q_real_t})")
            q_fake_list_mean = sum(self.Q_list[1:])/(len(self.Q_list)-1)
            q_fake_list_std = np.std(np.asarray(self.Q_list[1:]), axis = 0)
            logger.info(f"Qmulti-trial-shuffled = {q_fake_list_mean} +- {q_fake_list_std:.4}")

        x = np.arange(len(self.phi_list[-1])-1)
        y = self.phi_list[-1][1:]
        slope,b = np.polyfit(x, y, 1)
        logger.info(f"slope of phi_real = {slope}")
    
    def print_Q_parts(self):
        """ analysiert die Zusammensetzung der Berechnung von Q und gibt diese als String zurueck"""
        return_string = ""
        return_string +="REAL Q\n"
        for idx, Q in enumerate(self.Q_list):
            
            A = self.A_list[idx]
            #print(f"A.shape = {A.shape}")
            my2 = self.my2_list[idx]
            gamma = self.gamma_list[idx]
            #print(f"gamma.shape = {gamma.shape}")
            k = self.k_list[idx]
            #print(f"k.shape = {k.shape}")
            m = self.m_list[idx]
            #print(f"m.shape = {m.shape}")
            delta_intra_slice = self.delta_intra_slice_list[idx]
            #print(f"delta_intra_slice.shape = {delta_intra_slice.shape}")
            delta_inter_slice = self.delta_inter_slice_list[idx]
            #print(f"delta_inter_slice.shape = {delta_inter_slice.shape}")
            C = self.C_list[idx]
            #print(f"C.shape = {C.shape}")
            g = self.g_list[idx]
            #print(f"g.shape = {g.shape}")
            A_sum = 0
            gamma_sum = 0
            C_sum = 0
            dg_sum = 0
            for i in range(A.shape[0]):
                for j in range(A.shape[1]):
                    for s in range(A.shape[2]):
                        for r in range(C.shape[2]):
                            A_sum +=A[i,j,s]
                            gamma_sum += gamma[s]*((k[i,s]*k[j,s])/2*m[s])*delta_inter_slice[s,r]
                            C_sum += delta_intra_slice[i,j] * C[j,s,r]
                            dg_sum += 1 if (g[i,s]==g[j,r]) else 0
            desc = "REAL Q \n" if idx==0 else "FAKE Q\n"

            return_string += f"{desc} ({idx}) Zusammensetzung of result Q of {Q:.3f}\n"
            return_string += f"Q = {1/my2:.5f} * Summe([{A_sum:.1f} (A) - {gamma_sum:.1f} (gamma*term) + {C_sum:.1f}] (C_term) * {dg_sum} (delta_gg))\n"
            return_string += f"unique elements in g: {np.unique(g).shape[0]}\n"
        return_string += f"number of network row = {self.ipi.shape[0]}\n"
        return return_string


            
if __name__ == '__main__':
    from mst import MST
    gofor = 'MST'
    #gofor = 'SRTT'
    is_sim = False
    is_estimate_Q = False
    is_test_against_random = True

    if gofor == 'MST':
        p = p = ".\\Data MST"
        if is_sim:
            sim = SIM('MST','.\\Data MST\\3Tag1_.csv', '.\\Data_MST_Simulation\\3Tag1_.csv')
            p = ".\\Data_MST_Simulation"

        filename = os.path.join(p,"3Tag1_.csv")
        #mst = MST(filename, sequence_length = 10)
        mst = MST(fullfilename = ".\\Data MST\\3Tag1_.csv", sequence_length = 10, path_output = ".\\Data_python", _id = "no_id")
    
        net = Network(mst.ipi_cor, coupling_parameter = 0.03,  resolution_parameter = 0.9)
        net.filename = mst.filename
        net.clustering()

    elif gofor == 'SRTT':
        filename = ".\\Data_SRTT\\03_3_SRTT_2020-02-05_09-06-38.txt"
        filename = ".\\Data_SRTT\\04_2_SRTT_2020-02-06_12-17-15.txt"
        srtt = SRTT(filename)
        net = Network(srtt.rts_cv_but, coupling_parameter = 0.03,  resolution_parameter = 0.9)
        net.filename = srtt.filename


#    logger.info(srtt.df.head())
 #   net = Network(srtt.rts_cv_but, coupling_parameter = 0.03,  resolution_parameter = 0.9)

    if is_estimate_Q:
        net.estimate_chunks(is_random = False)
        logger.info(f"q_real = {net.Q_list[0]}")
        net.estimate_chunk_magnitudes(net.g_list[-1])

        # only after estimation of real Q than the estimation of fals Q is performed
        for i in range(self.num_random_Q):
            net.estimate_chunks(is_random = True)
            Network.estimate_chunk_magnitudes(net.g_list[-1])
            results_json = net.get_results_as_json()
        net.print_results(print_shuffled_results = is_test_against_random)

    if gofor=='SRTT':
        srtt.clustering(srtt.rts_cv_seq)
        net.clustering()
#    srtt.clustering(srtt.rts_cv_but)
    if gofor=='MST':
        #net.clustering()
        pass
