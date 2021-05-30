import os, sys
import exp_est # hier sind alle Funktionen die etwas berechnenen fuer die ExperimentKlasse
from group import get_and_save_data_for_one_subj
from group import Group
from mst import MST
from seq import SEQ
from srtt import SRTT
from experiment import Experiment
from igraph import Graph

filename = "./Data_Rogens/SEQ_Sim/34_SEQsimpleFRA1fertig.csv"
path_outputfiles="./tmp"
_id="0"

subj_class = SEQ(fullfilename = filename, path_output = path_outputfiles, _id = _id)
# get_and_save_data_for_one_subj(filename, experiment="SEQ",
#                                is_estimate_network=True,
#                                sequence_length=8,
#                                path_outputfiles="./tmp",
#                                _id="0",
#                                coupling_parameter=0.03,
#                                resolution_parameter=0.9,
#                                is_estimate_clustering=False,
#                                is_estimate_Q=False,
#                                num_random_Q=5)
subj_exp = Experiment(subj_class.experiment_name, subj_class.vpn,
                      subj_class.day, subj_class.sequence_length,
                      path_outputfiles, is_load=False,
                      df=subj_class.df, paradigma=subj_class.paradigma)
ipi_cor = exp_est.make2dlist_to_2darray(subj_exp.cor_ipi_lplsln[subj_exp.paradigma][:][:])
# # ipi_cor
# array([[-711, 2932, 4261, 1797, 1056, 2504, 2052, 1424],
#        [-336, 6164,  633, 2084, 2584,  663,  957, 1499],
#        [-497, 2579, 1601, 2679, 1943,  685, 1069, 1554],
#        [-781, 2578, 1607, 1510,  700, 1007, 2409, 3002]])

edges = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]]
gl = list()
for i in range(len(ipi_cor)):
    g = Graph(n=8, edges = edges, directed = True)
    g.es['weight'] = ipi_cor[i]
    gl.append(g)
    
edges = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7]]
G_1 = Graph(n=8, edges = edges, directed = True)
G_1.es['weight'] = ipi_cor[1]
G_2 = Graph(n=8, edges = edges, directed = True)
G_2.es['weight'] = ipi_cor[2]
G_3 = Graph(n=8, edges = edges, directed = True)
G_3.es['weight'] = ipi_cor[3]
import leidenalg as la
optimiser = la.Optimiser()
#https://leidenalg.readthedocs.io/en/latest/multiplex.html#temporal-community-detection
G_1 = gl[0]
G_2 = gl[1]
G_3 = gl[2]
G_coupling = Graph.Formula('1 -- 2 -- 3')
G_coupling.es['weight'] = 0.1 # Interslice coupling strength
G_coupling.vs['slice'] = [G_1, G_2, G_3]
Gl_1 = la.slices_to_layers(G1)
membership, improvement = la.find_partition_temporal(
                            [G_1, G_2, G_3],
                            la.CPMVertexPartition,
                            interslice_weight=0.1,
                            resolution_parameter=0.9)