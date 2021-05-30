from group import get_and_save_data_for_one_subj
from group import Group
from mst import MST
from seq import SEQ
from srtt import SRTT

filename = "./Data_Rogens/SEQ_Sim/34_SEQsimpleFRA1fertig.csv"
path_outputfiles="./tmp"
_id=0

subj_class = SRTT(fullfilename = filename, path_output = path_outputfiles, _id = _id)
# get_and_save_data_for_one_subj(filename, experiment="SEQ",
#                                is_estimate_network=True,
#                                sequence_length=8,
#                                path_outputfiles="./tmp",
#                                _id=0,
#                                coupling_parameter=0.03,
#                                resolution_parameter=0.9,
#                                is_estimate_clustering=False,
#                                is_estimate_Q=False,
#                                num_random_Q=5)
                               