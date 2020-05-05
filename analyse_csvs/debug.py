import pandas as pd
import numpy as np
import os

class Debug:
    def __init__(self, experiment):
        """[initialisiert mit den Attributen von der Experiment Klasse]

        Arguments:
            experiment {[type]} -- [description]
        """        
        self.exp = experiment
        self.df = self.exp.df
        self.df_ipi = self.exp.df_ipi
        self.write_debug_file(self.exp.all_ipi_lsln, 'all_ipi_lsln', 'lsln')
        self.write_debug_file(self.exp.cor_ipi_lsln, 'cor_ipi_lsln', 'lsln')
        self.write_debug_file(self.exp.err_ipi_lsln, 'err_ipi_lsln', 'lsln')
        self.write_debug_file(self.exp.all_hits_lsln, 'all_hits_lsln', 'lsln')
        self.write_debug_file(self.exp.all_ipi_lblsln, 'all_ipi_lblsln', 'lblsln')
        self.write_debug_file(self.exp.cor_ipi_lblsln, 'cor_ipi_lblsln', 'lblsln')
        self.write_debug_file(self.exp.err_ipi_lblsln, 'err_ipi_lblsln', 'lblsln')
        self.write_debug_file(self.exp.all_hits_lblsln, 'all_hits_lblsln', 'lblsln')
        
        self.write_debug_file(self.exp.all_ipi_lplblsln, 'all_ipi_lplblsln', 'lplblsln')
        self.write_debug_file(self.exp.cor_ipi_lplblsln, 'cor_ipi_lplblsln', 'lplblsln')
        self.write_debug_file(self.exp.err_ipi_lplblsln, 'err_ipi_lplblsln', 'lplblsln')
        self.write_debug_file(self.exp.all_hits_lplblsln, 'all_hits_lplblsln', 'lplblsln')
        
        self.write_debug_file(self.exp.all_seqsum_lpn, 'all_seqsum_lpn', 'lpn')
        self.write_debug_file(self.exp.cor_seqsum_lpn, 'cor_seqsum_lpn', 'lpn')
        self.write_debug_file(self.exp.err_seqsum_lpn, 'err_seqsum_lpn', 'lpn')
        
        self.write_debug_file(self.exp.all_seqsum_lplbn, 'all_seqsum_lplbn', 'lsln')
        self.write_debug_file(self.exp.cor_seqsum_lplbn, 'cor_seqsum_lplbn', 'lsln')
        self.write_debug_file(self.exp.err_seqsum_lplbn, 'err_seqsum_lplbn', 'lsln')
        
        self.write_debug_file(self.exp.all_seqtimesum_lplsn, 'all_seqtimesum_lplsn', 'lsln')
        self.write_debug_file(self.exp.cor_seqtimesum_lplsn, 'cor_seqtimesum_lplsn', 'lsln')
        self.write_debug_file(self.exp.err_seqtimesum_lplsn, 'err_seqtimesum_lplsn', 'lsln')
        
        self.write_debug_file(self.exp.all_seqtimesum_lplblsn, 'all_seqtimesum_lplblsn', 'lblsln')
        self.write_debug_file(self.exp.cor_seqtimesum_lplblsn, 'cor_seqtimesum_lplblsn', 'lblsln')
        self.write_debug_file(self.exp.err_seqtimesum_lplblsn, 'err_seqtimesum_lplblsn', 'lblsln')
        
        
        self.write_debug_file(self.exp.all_seqtimesum_slope_lpn, 'all_seqtimesum_slope_lpn', 'lpn')
        self.write_debug_file(self.exp.cor_seqtimesum_slope_lpn, 'cor_seqtimesum_slope_lpn', 'lpn')
        self.write_debug_file(self.exp.err_seqtimesum_slope_lpn, 'err_seqtimesum_slope_lpn', 'lpn')
        
        self.write_debug_file(self.exp.all_seqtimesum_per_block_slope_lpn, 'all_seqtimesum_per_block_slope_lpn', 'lpn')
        self.write_debug_file(self.exp.cor_seqtimesum_per_block_slope_lpn, 'cor_seqtimesum_per_block_slope_lpn', 'lpn')
        self.write_debug_file(self.exp.err_seqtimesum_per_block_slope_lpn, 'err_seqtimesum_per_block_slope_lpn', 'lpn')

       
        self.write_debug_file(self.exp.all_seqtimesum_to_max_slope_lpn, 'all_seqtimesum_to_max_slope_lpn', 'lpn')
        self.write_debug_file(self.exp.cor_seqtimesum_to_max_slope_lpn, 'cor_seqtimesum_to_max_slope_lpn', 'lpn')
        self.write_debug_file(self.exp.err_seqtimesum_to_max_slope_lpn, 'err_seqtimesum_to_max_slope_lpn', 'lpn')
       
        self.write_debug_file(self.exp.all_seqtimesum_per_block_to_max_slope_lpn, 'all_seqtimesum_per_block_to_max_slope_lpn', 'lpn')
        self.write_debug_file(self.exp.cor_seqtimesum_per_block_to_max_slope_lpn, 'cor_seqtimesum_per_block_to_max_slope_lpn', 'lpn')
        self.write_debug_file(self.exp.err_seqtimesum_per_block_to_max_slope_lpn, 'err_seqtimesum_per_block_to_max_slope_lpn', 'lpn')
       
        self.write_debug_file(self.exp.all_seqnum_per_block_slope_lpn, 'all_seqnum_per_block_slope_lpn', 'lpn')
        self.write_debug_file(self.exp.cor_seqnum_per_block_slope_lpn, 'cor_seqnum_per_block_slope_lpn', 'lpn')
        self.write_debug_file(self.exp.err_seqnum_per_block_slope_lpn, 'err_seqnum_per_block_slope_lpn', 'lpn')
        
        
        self.write_dfs()

    def write_dfs(self):
        '''
        '''
        self.df.to_csv('.\\debug\\experiment_input.csv', index = False, sep = '\t')
        self.df_ipi.to_csv('.\\debug\\experiment_input_ipi.csv', index = False, sep = '\t')

        dfshow = self.df[['EventNumber','Time','isHit']].copy()
        dfshow['Timeipi'] = 0
        for idx in range(dfshow.shape[0]):
            dfshow.loc[idx,'Timeipi'] = self.df_ipi.loc[idx,'Time']
        flat_list = [item for sublist in self.exp.all_ipi_lsln for item in sublist]
        flat_list_hit = [item for sublist in self.exp.all_hits_lsln for item in sublist]
        dfshow["all_lsln"] = flat_list
        dfshow["hit_lsln"] = flat_list_hit
        dfshow.to_csv('.\\debug\\time_all_lsln.csv', index = False, sep = '\t')
        

    def write_debug_file(self, var, name, code):
        filename = os.path.join('.\\debug',name+'.csv')
        if code == "lsln":
           with open(filename,'w') as fp:
            fp.write("[\n")
            for l in var:
                fp.write("\t" + str(l) + '\n')
            fp.write("]")

        if code == "lblsln":
            with open(filename,'w') as fp:
                fp.write("[\n")
                for b in var:
                    fp.write("\t[\n")
                    for l in b:
                        fp.write("\t\t" + str(l) + '\n') 
                    fp.write("\t]," + '\n')
                fp.write("]")

        if code == "lpn":
            with open(filename,'w') as fp:
                fp.write("[\n")
                for p in var:
                    fp.write("\t" + str(p) + '\n') 
                    
                fp.write("]")


        if code == "lplblsln":
            with open(filename,'w') as fp:
                fp.write("[ paradigmen\n")
                for p in var: 
                    fp.write("\t[ bloecke\n")
                    for b in p:
                        fp.write("\t\t[ sequence \n")
                        for l in b:
                            fp.write("\t\t\t" + str(l) + '\n') 
                        fp.write("\t\t]," + '\n')
                    fp.write("\t]")
                fp.write("]")




    def add_parameter_to_df_debug(self, all_ipi_lsln, string):
        self.df_debug = self.add_lsln(self.df_debug, all_ipi_lsln, string)

    def add_lsln(self, df, lsln, col_name):
        flat_list = [item for sublist in lsln for item in sublist]
        print(len(flat_list))
        print(self.df_debug.shape)
        df[col_name] = flat_list

        return df