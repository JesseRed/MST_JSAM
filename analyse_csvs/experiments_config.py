from statistic_ck import Statistic
from group_analysis import Group_analysis
from group import Group
from mst import MST
from lern_table import LearnTable
import logging
##################################
### logging 
log_level = logging.INFO

logging.basicConfig(level=log_level, filename='logfile.log', 
    format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s',
    filemode='w')
logger = logging.getLogger(__name__)


def analyse_preestimated_Rogens():

    path_outputfiles = ".\\Data_Rogens\\Results"
    analysis = Group_analysis(path_outputfiles)

    dicSEQ1 = {
        "experiment_name"           :   "SEQ",
        "path_inputfiles"           :   ".\\Experiment_data",
        "filepattern"               :   "SEQ_1",
        "vpns"                      :   [15, 16, 17, 18, 19, 20, 21, 22],
        "day"                       :   1,
        "path_outputfiles"          :   path_outputfiles,
        "sequence_length"           :   8,
        "paradigma"                 :   0,
    }

    
    
    dicSEQ2 = {
        "experiment_name"           :   "SEQ",
        "path_inputfiles"           :   ".\\Experiment_data",
        "filepattern"               :   "SEQ_2",
        "vpns"                      :   [15, 16, 17, 18, 19, 20, 21, 22],
        "day"                       :   2,
        "path_outputfiles"          :   path_outputfiles,
        "sequence_length"           :   8,
        "paradigma"                 :   0,
    }

    analysis.add_pre_estimated_group(dicSEQ1)
    analysis.add_pre_estimated_group(dicSEQ2)
    
    analysis.make_statistic(paradigma = 0)

     

def estimate_Rogens():
    logger.info("Start...")
    
#    experiment_name = 'SRTT'
    #experiment_name = 'ASTEROID'

    dicMST = {
        "is_perform_analysis"       :   True,
        "is_estimate_network"       :   False,
        "is_perform_statistic"      :   False,
        "is_sim"                    :   False,
        "is_estimate_Q"             :   True,
        "is_test_Q_against_random"  :   True,
        "num_random_Q"              :   10,
        "is_clustering"             :   False,
        "num_random_Q"              :   10,
        "coupling_parameter"        :   0.3,
        "resolution_parameter"      :   0.9,
        "experiment_name"           :   "MST",
        "path_inputfiles"           :   ".\\Data_Rogens\\MST",
        "filepattern"               :   ["REST1", "REST2"],
        "_ids"                      :   ["MST_G1", "MST_G2"],
        "sequence_length"           :   10,
        "path_outputfiles"          :   ".\\Data_Rogens\\Results",
        "is_multiprocessing"        :   False,
        "show_images"               :   False,
        "target_color"              :   0,
        "table"                     :   ".\\Data_Rogens\\Lernspiel_Auswertung_2020b.csv",
    }

    dicSEQ8 = {
        "is_perform_analysis"       :   True,
        "is_estimate_network"       :   False,
        "is_perform_statistic"      :   False,
        "is_sim"                    :   False,
        "is_estimate_Q"             :   True,
        "is_test_Q_against_random"  :   True,
        "num_random_Q"              :   10,
        "is_clustering"             :   False,
        "num_random_Q"              :   10,
        "coupling_parameter"        :   0.3,
        "resolution_parameter"      :   0.9,
        "experiment_name"           :   "SEQ",
        "path_inputfiles"           :   ".\\Data_Rogens\\SEQ8",
        "filepattern"               :   ["FRA1", "FRA2"],
        "_ids"                      :   ["SEQ8_G1", "SEQ8_G2"],
        "sequence_length"           :   8,
        "path_outputfiles"          :   ".\\Data_Rogens\\Results",
        "is_multiprocessing"        :   False,
        "show_images"               :   False,
        "target_color"              :   8,
        "table"                     :   ".\\Data_Rogens\\Lernspiel_Auswertung_2020b.csv",
    }

    
    dicSRTT = {
        "is_perform_analysis"       :   True,
        "is_estimate_network"       :   False,
        "is_perform_statistic"      :   False,
        "is_sim"                    :   False,
        "is_estimate_Q"             :   True,
        "is_test_Q_against_random"  :   True,
        "num_random_Q"              :   10,
        "is_clustering"             :   False,
        "num_random_Q"              :   10,
        "coupling_parameter"        :   0.3,
        "resolution_parameter"      :   0.9,
        "experiment_name"           :   "SRTT",
        "path_inputfiles"           :   ".\\Data_Rogens\\SRTT",
        "filepattern"               :   ["SRTT1", "SRTT2"],
        "_ids"                      :   ["SRTT_G1", "SRTT_G2"],
        "sequence_length"           :   12,
        "path_outputfiles"          :   ".\\Data_Rogens\\Results",
        "is_multiprocessing"        :   False,
        "show_images"               :   False,
        "target_color"              :   0,
        "table"                     :   ".\\Data_Rogens\\Lernspiel_Auswertung_2020b.csv",
    }

    #print(dicMST)
    perform(dicMST)
    perform(dicSEQ8)
    perform(dicSRTT)
    table = LearnTable(".\\Data_Rogens\\Lernspiel_Auswertung_2020b.csv")
    table.add_experimental_columns_to_table(dicMST)
    table.add_to_table(dicMST)

def perform(dic):    
    """ es wird ein dictionary mit parametern uebergeben"""
    analysis = Group_analysis(dic["path_outputfiles"])
    if dic["is_perform_analysis"]:
#        analysis.add_group(experiment = dic["experiment_name"], 
        analysis.add_group(experiment = dic["experiment_name"], 
            path_inputfiles = dic["path_inputfiles"], filepattern=dic["filepattern"][0], 
            path_outputfiles = dic["path_outputfiles"], sequence_length = dic["sequence_length"], 
            _id = dic["_ids"][0], is_estimate_network = dic["is_estimate_network"], 
            is_clustering = dic["is_clustering"], is_multiprocessing = dic["is_multiprocessing"],
            show_images = dic["show_images"], target_color = dic["target_color"])

        #analysis.add_group(experiment = dic["experiment_name"], 
        analysis.add_group(experiment = dic["experiment_name"], 
            path_inputfiles = dic["path_inputfiles"], filepattern=dic["filepattern"][1], 
            path_outputfiles = dic["path_outputfiles"], sequence_length = dic["sequence_length"], 
            _id = dic["_ids"][1], is_estimate_network = dic["is_estimate_network"],
            is_clustering = dic["is_clustering"], is_multiprocessing = dic["is_multiprocessing"],
            show_images = dic["show_images"], target_color = dic["target_color"])
    
def perform_with_preexisting_data(analysis, dic):    
    """ es wird ein dictionary mit parametern uebergeben"""
    
    analysis.add_pre_estimated_group(experiment = dic["experiment_name"], 
        path_inputfiles = dic["path_inputfiles"], filepattern=dic["filepattern"][1], 
        path_outputfiles = dic["path_outputfiles"], sequence_length = dic["sequence_length"], 
        target_color = dic["target_color"], vpns = dic["vpns"])
    # my_stat = Statistic(experiment=dic["experiment_name"], group_list=analysis.groups, data_path=dic["path_outputfiles", _ids=dic["_ids"])
    # keys = ["corrsq_slope", "abs_corr_seq", "pos_of_first_best_block", "pos_of_last_best_block"]
    # for key in keys:
    #     my_stat.test_group_differences_ttest(key = key, is_independent = False)
    #     my_stat.show_group_differences(key)
    
    # my_stat.plot_one_group_sequence("corrsq")


    

    

    # if dic["is_estimate_network:

    #     net = Network(mst.ipi_cor, coupling_parameter = 0.03,  resolution_parameter = 0.9)
    #     net.filename = mst.filename
    #     net.clustering()
    #     if dic["is_estimate_Q:
    #         g_real,q_real = net.estimate_chunks(is_random = False)
    #     print(f"q_real = {q_real}")
    #     net.phi_real = net.estimate_chunk_magnitudes(g_real)
    #     if is_test_Q_against_random:
    #         net.test_chunking_against_random(rand_iterations=3)
    #         #print(f"q_real = {q_real}")
    #         results_json = net.get_results_as_json()
    #     net.print_results(print_shuffled_results = is_test_Q_against_random)


    # my_stat = Statistic(experiment=experiment_name, group_list=analysis.groups, data_path=".\\Results\\Rogens", _ids=_ids)
    # keys = ["corrsq_slope", "abs_corr_seq", "pos_of_first_best_block", "pos_of_last_best_block"]
    # for key in keys:
    #     my_stat.test_group_differences_ttest(key = key, is_independent = False)
    #     my_stat.show_group_differences(key)



    # from mst import MST
    # gofor = 'MST'
    # #gofor = 'SRTT'
    # is_sim = False

    # is_estimate_Q = False
    # is_test_Q_against_random = True

    # if gofor == 'MST':
    #     p = p = ".\\Data MST"
    #     if is_sim:
    #         sim = SIM('MST','.\\Data MST\\3Tag1_.csv', '.\\Data_MST_Simulation\\3Tag1_.csv')
    #         p = ".\\Data_MST_Simulation"

    #     filename = os.path.join(p,"3Tag1_.csv")
    #     #mst = MST(filename, sequence_length = 10)
    #     mst = MST(fullfilename = ".\\Data MST\\3Tag1_.csv", sequence_length = 10, path_output = ".\\Data_python", _id = "no_id")
    
    #     net = Network(mst.ipi_cor, coupling_parameter = 0.03,  resolution_parameter = 0.9)
    #     net.filename = mst.filename
    #     net.clustering()

    # elif gofor == 'SRTT':
    #     filename = ".\\Data_SRTT\\03_3_SRTT_2020-02-05_09-06-38.txt"
    #     filename = ".\\Data_SRTT\\04_2_SRTT_2020-02-06_12-17-15.txt"
    #     srtt = SRTT(filename)
    #     net = Network(srtt.rts_cv_but, coupling_parameter = 0.03,  resolution_parameter = 0.9)
    #     net.filename = srtt.filename


#    print(srtt.df.head())
 #   net = Network(srtt.rts_cv_but, coupling_parameter = 0.03,  resolution_parameter = 0.9)

#     if is_estimate_Q:
#         g_real,q_real = net.estimate_chunks(is_random = False)
#         print(f"q_real = {q_real}")
#         net.phi_real = net.estimate_chunk_magnitudes(g_real)
#         if is_test_Q_against_random:
#             net.test_chunking_against_random(rand_iterations=3)
#             #print(f"q_real = {q_real}")
#             results_json = net.get_results_as_json()
#         net.print_results(print_shuffled_results = is_test_Q_against_random)

#     if gofor=='SRTT':
#         srtt.clustering(srtt.rts_cv_seq)
#         net.clustering()
# #    srtt.clustering(srtt.rts_cv_but)
#     if gofor=='MST':
#         #net.clustering()
#         pass

#         my_stat = Statistic(experiment=experiment_name, group_list=[], data_path=".\\Data_python", _ids=_ids)
#         #my_stat.test_group_differences_ttest('corrsq_slope')
#         my_stat.test_group_differences_ttest('success_per_block')
#         my_stat.test_group_differences_ttest('abs_success')
#         for key, val in my_stat.data[0][1].items():
#             print(key)
#         print(my_stat.data[1][0]['phi_real_slope'])
        
#         y = my_stat.data[1][0]['phi_real']
#         x = list(range(len(y)))
#         plt.scatter(x,y)
#         plt.show()
# #    my_stat = Statistic(experiment = experiment_name, group_list= analysis.groups, data_path = ".\\Data_python", _ids = _ids)
# #    analysis.perform_statistics()

    #######################################
    # SEQ 8



#    my_stat.plot_one_group_sequence("corrsq")
    