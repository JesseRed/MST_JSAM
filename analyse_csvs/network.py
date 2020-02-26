import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, rename
from os.path import isfile, join
from statistics import mean, stdev
import statistics
import networkx
import time
from mst import MST
from srtt import SRTT
import random

class Network():
    def __init__(self, ipi, coupling_parameter = 0.03,  resolution_parameter = 0.9):
        # whether in the adaptation process it will be tried to set the
        # node in the next trial to the same node of the previous
        self.is_adapt_communities_across_trials = False 
        
        self.ipi = ipi
        self.coupling_parameter = coupling_parameter
        self.resolution_parameter = resolution_parameter    
        ipi = self.ipi
        self.ipi_arr = self.convert_to_array2D(self.ipi)
        #print(self.ipi_arr.shape)
        m, std = self.get_ipi_mean_arr(self.ipi_arr)

        self.ipi_norm = self.get_normalized_ipi(ipi, m, std)
        self.ipi_norm_arr = self.convert_to_array2D(self.ipi_norm)
        self.A = self.get_adjacency_matrix(self.ipi_norm_arr) 
        self.C = self.get_inter_slice_coupling(self.ipi_norm_arr, self.coupling_parameter)
        self.delta_intra_slice = self.get_delta_intra_slice(self.A)
        self.delta_inter_slice = self.get_delta_inter_slice(self.C)

        self.c = np.sum(self.C,axis=2)
        self.k = np.sum(self.A,axis=0)
        self.kappa = self.k + self.c
        self.my2 = sum(sum(self.kappa))
        self.m = np.sum(self.k, axis=0)
        self.gamma = np.zeros((self.A.shape[2]))+self.resolution_parameter


        #Randomize
        self.ipi_norm_arr_shuffled = self.shuffle(self.ipi_norm_arr)
        self.P_list = []
        for i in range(100):
            self.ipi_norm_arr_shuffled = self.shuffle(self.ipi_norm_arr)
            self.P_list.append(self.get_adjacency_matrix(self.ipi_norm_arr_shuffled))
            
        self.P = self.P_list[0]

        
        # the partition optimized by Qmulti_trial
        #self.g = self.estimate_chunks()
        
        #self.phi = self.estimate_chunk_magnitudes(self.g)
        
    def shuffle(self, ipi):
        for i in range(ipi.shape[0]):
            random.shuffle(ipi[i,:])
        return ipi
        
    def estimate_chunk_magnitudes(self, g):
        '''
        Chunk magnitude (ϕ) is defined as 1/Qsingle–trial. Low values of ϕ correspond to trials with
        greater segmentation, which are computationally easier to split into chunks and high values
        of ϕ correspond to trials with greater chunk concatenation, which contain chunks that are
        more difficult to computationally isolate. We normalized the values of ϕ across correct trials
        for each frequent sequence: (Wymbs et al. 2013)
        
        '''
        print("estimating chunk magnitudes")
        #print(g.T)
        P = self.P
        phi = []
        for slice in range(g.shape[1]):
            Q_st = self.estimate_Q_st(g[:,slice],self.A[:,:,slice], P[:,:,slice])
            
            phi.append(1/Q_st)
        #normalization
        m = sum(phi)/len(phi)
        for i in phi:
            i = (i-m)/m
        self.phi = phi
        return phi


    def estimate_Q_st(self, trial, W, P):
        summe = 0
        for i in range(W.shape[0]):
            for j in range(W.shape[1]):
                summe = summe +(W[i,j]-P[i,j])*self.get_delta_2d(trial[i],trial[j])
        return summe
    
    def get_delta_2d(self,i,j):
        ret = (1 if i==j else 0)
        return ret
    
    def estimate_chunks(self, is_random=False):
        ''' A ist die Adjacency matrix anhand der die Berechnung der chunks
            erfolgt. Diese kann dann auch durch die Random Adjacency matrix 
            ersetzt werden.
        '''
        if not is_random:
            A = self.A # setzte die normale Adjecency matrix
        else:
            # Shuffle the data
            ipi_norm_arr_shuffled = self.shuffle(self.ipi_norm_arr)
            A = self.get_adjacency_matrix(ipi_norm_arr_shuffled)
            
        g = self.initialize_g() # jedes node ist seine eigene community
        start = time.time()
        Qms_old = self.get_Qms_opt(g, A)
        print(f"Qms execution time = {time.time()-start:.3} s")
        idx = 0
        while True:
            idx +=1
            start = time.time()
            g = self.adapt_communities(g,A)
            Qms = self.get_Qms_opt(g, A)
            if Qms<=Qms_old:
                break
            else:
                Qms_old=Qms
#            print(g.T)
            print(f"------------------------------------------")
            print(f"----------Durchlauf = {idx} --------------")
            print(f"postadapt ... unique elements in g: {np.unique(g).shape[0]}")
            print(f"adapt_communities execution time = {time.time()-start:.3} s")                    
            print(f"durchlauf={idx} mit Qms = {Qms}")
        Qms = self.get_Qms_opt(g, A)
        print(f"Final Qms = {Qms}")
        return (g, Qms)
        #self.w = self.get_simple_weights(self.ipi_norm_arr)
        #self.w_norm = self.get_normalized_weigths(self.ipi_norm)
        
    def adapt_communities(self,g, A):
        # Anpassung von g entsprechend dem Algorithmus von Blondel 2008
        # g wird durchgegangen und g[i,s] wird in seinerm community
        # ersetzt durch g[i-1,s] und g[i+1,s]
        # wenn sich eine Verbesserung einstellt dann wird die neue
        # Zuordnung beibehalten

#        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
 
        index = 0
        for s in range(g.shape[1]):
            for i in range(g.shape[0]):
                index+=1
                #print(f"{i} ... unique elements in g: {np.unique(g).shape[0]}")
                #print(f"{g[:,0]}")
                #print(f"g[i,s]= {g[i,s]}")
                community_org = g[i,s]
                community_links = -1
                community_rechts = -1
                community_unten = -1
                q_org = self.get_Qms_opt(g,A)
                q_links = -999
                q_rechts = -999
                q_unten = -999
                #print(f"original Q0 = {q_org}")
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
                #print(f"adapt communites results = {results}")
                g_communities = [community_org, community_links, community_rechts, community_unten]
                # ist Q wirklich immer positiv wenn es besser wird????
                g[i,s] = g_communities[results.index(max(results))] # die community zuordnung des maximums
   
                #self.g = g

        


        return g
        #print(f"postadapt ... unique elements in g: {np.unique(g).shape[0]}")
                
                

    def initialize_g(self):
        # initialization with every node is a community
        g = np.arange(self.A.shape[0]*self.A.shape[2]).reshape(self.A.shape[0],self.A.shape[2])
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
                            #print(self.get_delta_community(g[i,s],g[j,r]))
                        #if i==0:
                        #    print(f"[i,j,s,r] = [{i},{j},{s},{r}]")
#                        if i==0 and j==1 and s==0 and r==0:
#                            print(f"A[{i},{j},{s}]={A[i,j,s]}")
#                            xxx = ((gamma[s]*k[i,s]*k[j,s])/(2*m[s]))
#                            print(f"gamma[s]*k[i,s]*k[j,s])/(2*m[s]) = {xxx}")
#                            print(f"delta_inter_slice[{s},{r}]={delta_inter_slice[s,r]}")
#                            print(f"delta_intra_slice[{i},{j}]={delta_intra_slice[i,j]}")
#                            print(f"C[{j},{s},{r}]={C[j,s,r]}]")
#                            print(f"self.get_delta_community(g[{i},{s}],g[{j},{r}]) = {self.get_delta_community(g[i,s],g[j,r])}")
#        
        Qms = 1/self.my2 * summe
        
        #print(f"estimation time = {time.time()-start} s")
        return Qms
    
    def get_Qms_optx(self, g, i, s):
        A = self.A
        C = self.C
        print(f"----------------------")
        print(f"start estimate Qms")
        print(f"{g[:,0]}")
        print(f"{g[:,1]}")
        #print(f"C.shape = {C.shape}")
        #print("C")
        #print(C)
        c = np.sum(C,axis=2)
        #print("c")
        #print(c)
        k = np.sum(A,axis=0)
        #print("k")
        #print(k)
        kappa = k + c
        #print("kappa")
        #print(kappa)
        my2 = sum(sum(kappa))
#        print("my2")
#        print(my2)
        m = np.sum(k, axis=0)
#        print("m")
#        print(m)
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
                            #print(self.get_delta_community(g[i,s],g[j,r]))
                        if i==0 and j==1 and s==0 and r==0:
                            print(f"A[{i},{j},{s}]={A[i,j,s]}")
                            xxx = ((gamma[s]*k[i,s]*k[j,s])/(2*m[s]))
                            print(f"gamma[s]*k[i,s]*k[j,s])/(2*m[s]) = {xxx}")
                            print(f"delta_inter_slice[{s},{r}]={delta_inter_slice[s,r]}")
                            print(f"delta_intra_slice[{i},{j}]={delta_intra_slice[i,j]}")
                            print(f"C[{j},{s},{r}={C[j,s,r]}]")
                            print(f"self.get_delta_community(g[{i},{s}],g[{j},{r}]) = {self.get_delta_community(g[i,s],g[j,r])}")
        print("summe")
        print(summe)
        

        Qms = 1/my2 * summe
        print(f"Qms = {Qms}")
        print(f"estimation time = {time.time()-start} s")
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
        #print(f"C.shape = {C.shape}")
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
        y = []
        for block in list3:
             for sequence in block:
                 y.append(sequence)
        y_mat = np.stack(y)
        return y_mat # array der dimension N x M   (N anzahl der korrekten Sequenzen, M Anzahl der Elemente pro sequenz)
        
    def get_simple_weights(self, ipi_arr):
        # estimates similarities in IKIs 
        w = []
        for i in range(ipi_arr.shape[0]):
            d = np.zeros((10,10))
            m = max(ipi_arr[i,:])
            for j in range(ipi_arr.shape[1]-1):
                d[j,j]=0.03
                d[j,j+1]=(m-abs(ipi_arr[i,j]-ipi_arr[i,j+1]))/m
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

    def printlist3(self, list3):
        for idx, x in enumerate(list3):
            print(f"Block nummer: {idx+1}")
            for y in x:
                print(y)
 #               print(type(y[0]))


    def get_inter_key_intervals_only_cor(self, num_cor_press):
        """reduziert die ipi (inter Press Intervals) auf nur die korrekten Druecker
            dazu werden ausschliesslich korrekte Sequenzen herangezogen
            Wir behaupten, dass man nicht mehr als 10 druecker chunkt
            Daher ketten wir maximal 2 aneinander
            Nachher die anhehaengte wird gedoppelt
            hier muessen wir nacher darauf achten, dass wir keine Sequenzen nehmen die nur in der 2. 
            Sequenz stattfinden da sie dann doppelte gezaehlt waeren
            num_cor_press definiert wie viele korrekte vorhanden sein muessen um eine komplette "Sequenz" zu definieren
        """        
        ipi_cor = []

        
        for idx, i in enumerate(self.ipi):
            # print(f'block number: {idx} mit blocklaenge von: {i.shape}')
            # am Anfang des blockes gibt es kein ipi fuer den ersten Tastendruck
            # hier fuege ich einen dummy des durchschnitts der Tastendruecke ein           
            ipi = np.array(np.mean(i))
            ipi = np.append(ipi, i)

            h = self.hits[idx]
            ipi_corr_block = []
            ipi_corr_seq = []
            # Schleife ueber das Array eines Blocks
            seq_idx = 0
            arr_idx = 0
            while arr_idx <ipi.shape[0]:
                #print(f"arr_idx = {arr_idx}")
                if h[arr_idx]==0:
                    # abbruch der Sequenz bei einem Fehler nun neubegin
                    # setze arr_idx auf den begin der naechsten Sequenz 
                    # ggf. vor oder zurueck
                    if seq_idx < 5:
                        arr_idx = arr_idx + 5 -seq_idx
                    if seq_idx > 5:
                        arr_idx = arr_idx - (seq_idx-5)
                    # loesche den aktuellen Sequenzblock
                    ipi_corr_seq = []
                    # setze den aktuellen Sequenzmarker zureck
                    seq_idx = 0
                else:
                    # es wurde korrekt gedrueckt
                    ipi_corr_seq.append(ipi[arr_idx])
                    seq_idx+= 1
                    arr_idx+= 1

                if seq_idx==num_cor_press:
                    # wenn diese Stelle erreicht wird dann war die Sequenz bis hierher erfolgreich
                    # und wir speichern die Sequenz ab
                    ipi_corr_block.append(ipi_corr_seq)
                    ipi_corr_seq = []
                    seq_idx = 0
            ipi_cor.append(ipi_corr_block) # liste einer liste einer Liste
        return ipi_cor

    def get_inter_key_intervals(self):
        """ in einem numpy Array werden die inter Key intervalls gespeichert
            die Zeit zum ersten key press entfaellt 
            Liste von Arrays
        """ 
        blcktmp = 0
        ipi = []
        hits = []
        key_press_time = 0
        for index, row in self.df.iterrows():
            if row["BlockNumber"]!=blcktmp:
                if blcktmp > 0:
                    ipi.append(np.asarray(ipi_block_list_tmp, dtype = np.float32))
                    hits.append(np.asarray(block_hits, dtype = np.int8))
                # ein neuer Block
                blcktmp +=1
                ipi_block_list_tmp = []
                key_press_time = float(row["Time Since Block start"].replace(',','.')) # dummy 
                block_hits = []
                block_hits.append(row['isHit'])
                continue # der erste in jedem Block wird nicht gespeichert
                
            ipi_block_list_tmp.append(float(row["Time Since Block start"].replace(',','.'))-key_press_time)
            key_press_time = float(row["Time Since Block start"].replace(',','.'))
            block_hits.append(row['isHit'])
        ipi.append(np.asarray(ipi_block_list_tmp, dtype = np.float32))
        hits.append(np.asarray(block_hits, dtype = np.int8))
        return (ipi, hits)
            

    def estimate_correct_seqences(self):
        corrsq=[]
        tmpcount=0
        num_sq=[]
        blcktmp=-1
        num_blck_ev=0
        num_blck_tmp=0
        durchschnitt_blck=[]
        for index, row in self.df.iterrows():
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
            if ((index+1)%5)==0: # eine Serie komplett
                if tmpcount==5:
                    corrsq[-1]=corrsq[-1]+1
                tmpcount=0
                num_sq[-1]=num_sq[-1]+1
        #print(f"{corrsq}")   
        return corrsq

    def estimate_improvement(self):
        X = [1,2,3,4,5,6,7,8,9,10,11,12]
        if not hasattr(self,'corrsq'):
            self.estimate_correct_seqences()
        improvement,b = np.polyfit(X, self.corrsq, 1)
        return improvement


                
#                
#    def get_delta_q(self,g, i, s):
#        A = self.A
#        C = self.C
#        community = g[i,s]
#        # Sin  ...sum of the weights of the links inside the community
#        # Stot ...sum of the weights of the links incident to nodes in C
#        Sin, Stot = self.get_sum_of_weights_within_a_community(A,C,g,community)
#        # k_i_in ... sum of the weights of the links from i to nodes in the community
#        # k_i    ... sum of the weights of the links incident to node i
#        (k_i_in, k_i) = self.get_sum_of_weights_of_links_from_i_to_nodes_in_community(A,C,g,community, i)
#        #sum of the weights of all the links in the network
#        m = sum(sum(sum(A)))+sum(sum(sum(C)))
#        
#        dq = 
#        # gebe deltaQ zurueck
#        return dq
#    
#    
##    def get_sum_of_weights_of_links_incident_to_node_i(A,C,g, community):
##        Ais = np.sum(A,axis=1) # i x s ... eliminating j ... entsprechend der symmetrischen Natur von A gibt es 2 links fuer jeden Node
##        Cis = np.sum(C,axis=2) # i x s ... eleminating r
##        Sin = Ais[g==community] + Cis[g==community]
##        return Sin   
#    
#    
#    def get_sum_of_weights_of_links_from_i_to_nodes_in_community(self, A, C, g, community, fokus_node_i, fokus_node_s):
#        # sum of the weights of the links from i to nodes in the community
#        # es ist so implementiert, dass es auch berechnet wird wenn fokus_node gar nicht in der community liegt
#        # in der aktuellen Anwendung sollte das aber der fall sein durch das setzen von community
#        g_bool = g==community
#        k_i_in = 0 # sum of the weights of the links from i to nodes in the community
#        k_i = 0
#        start_i = (0 if fokus_node_i==0 else fokus_node_i-1)
#        end_i = (g.shape[0] if fokus_node_i==g.shape[0] else fokus_node_i+1)
#        start_s = (0 if fokus_node_s==0 else fokus_node_s-1)
#        end_s = (g.shape[1] if fokus_node_s==g.shape[1] else fokus_node_s+1)
#        
#        # in Schicht s nur nach vorn und hinten ... wenn start_i == fokus_node_i ist das egal da dann A = 0
#        k_i_in = k_i_in + (A[start_i,fokus_node_s,fokus_node_s] if g_bool[start_i,fokus_node_s] else 0)
#        k_i_in = k_i_in + (A[end_i,fokus_node_s,fokus_node_s] if g_bool[start_i,fokus_node_s] else 0)
#        # in i nur nach vorn und hinten ... wenn start_s == fokus_node_s ist das egal da dann C = 0
#        k_i_in = k_i_in + (C[fokus_node_i,start_s,fokus_node_s] if g_bool[fokus_node_i,start_s] else 0)
#        k_i_in = k_i_in + (C[fokus_node_i,end_s,fokus_node_s] if g_bool[fokus_node_i,end_s] else 0)
#       
#        # in Schicht s nur nach vorn und hinten ... wenn start_i == fokus_node_i ist das egal da dann A = 0
#        k_i = k_i + A[start_i,fokus_node_s,fokus_node_s] 
#        k_i = k_i + A[end_i,fokus_node_s,fokus_node_s]
#        # in i nur nach vorn und hinten ... wenn start_s == fokus_node_s ist das egal da dann C = 0
#        k_i = k_i + C[fokus_node_i,start_s,fokus_node_s] 
#        k_i = k_i + C[fokus_node_i,end_s,fokus_node_s]
#       
#        return (k_i_in, k_i)
#
#    def get_sum_of_weights_within_a_community(self, A, C, g, community):
#        g_bool = g==community
#        Sin = 0 #sum of the weights of the links inside the community
#        Stot = 0 #
#        for s in range(g.shape[1]-1): # i
#            for i in range(g.shape[0]-1):
#                if g_bool[i,s]:
#                    Stot = Stot + A[i,i+1,s]
#                    if g_bool[i+1,s]:
#                        # dann gehoeren zwei nebeneinander stehende nodes in eine community
#                        Sin = Sin + A[i,i+1,s]
#                    Stot = Stot + C[i,s,s+1]
#                    if g_bool[i,s+1]:
#                        # dann gehoeren zwei untereinander stehende nodes in eine community
#                        Sin = Sin + C[i,s,s+1]
#        return (Sin, Stot)
#        

        

if __name__ == '__main__':
    filename = ".\\Data MST\\3Tag1_.csv"
    filename = ".\\Data_SRTT\\03_3_SRTT_2020-02-05_09-06-38.txt"
    srtt = SRTT(filename)
    print(srtt.df.head())
    # net = Network(mst.ipi_cor, coupling_parameter = 0.03,  resolution_parameter = 0.9)
    # g_real,q_real = net.estimate_chunks(is_random = False)
    # phi_real = net.estimate_chunk_magnitudes(g_real)
    # g_fake_list = []
    # q_fake_list = []
    # phi_fake_list = []
    # for i in range(10):
    #     g, q = net.estimate_chunks(is_random = True)
    #     phi = net.estimate_chunk_magnitudes(g)
    #     g_fake_list.append(g)
    #     q_fake_list.append(q)
    #     phi_fake_list.append(phi)
    # ipi = net.ipi_norm_arr






#    filename = ".\\Data MST\\3Tag1_.csv"
#     mst = MST(filename)

#     net = Network(mst.ipi_cor, coupling_parameter = 0.03,  resolution_parameter = 0.9)
#     #g = net.g
#     g_real,q_real = net.estimate_chunks(is_random = False)
#     phi_real = net.estimate_chunk_magnitudes(g_real)
#     g_fake_list = []
#     q_fake_list = []
#     phi_fake_list = []
#     for i in range(10):
#         g, q = net.estimate_chunks(is_random = True)
#         phi = net.estimate_chunk_magnitudes(g)
#         g_fake_list.append(g)
#         q_fake_list.append(q)
#         phi_fake_list.append(phi)
# #    g = np.load("g_arr.npy")
    
#     #Qms_list = net.Qms_list
#     ipi = net.ipi_norm_arr




    #the partition optimized by Qmulti_trial
    #g = self.estimate_chunks()
        
    
    #w_norm = mst.w_norm
    #print(type(mst.ipi_cor))
    #print(len(mst.ipi_cor))

#model.fit(ta.reshape(-1,1),phia)
#Out[36]: LinearRegression(copy_X=True, fit_intercept=True, n_jobs=1, normalize=False)
#
#model.intercept_
#Out[37]: 0.85201842328977
#
#model.coef_
#Out[38]: array([-0.04204932])
#
#from numpy.polynomial.polynomial import polyfit
#
#b, m = polyfit(ta, phia, 1)
#
#
#x = ta
#
#y = phi
#
#plt.plot(x, y, '.')
#plt.plot(x, b + m * x, '-')
#plt.show()
#t = list(range(63))
#
#ta = np.asarray(t, dtype=int)
#
#phia = np.asarray(phi, dtype=np.float32)
#with open("results_unten.txt","wb") as fp:
#    pickle.dump(q_real,fp)
#    pickle.dump(q_fake_list, fp)
#    pickle.dump(g_real,fp)
#    pickle.dump(g_fake_list,fp)