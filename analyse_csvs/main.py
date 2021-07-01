import sys
from qtpy import QtWidgets

from ui.mainwindow import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
import json, os
from statistic_ck import Statistic
from group_analysis import Group_analysis
#from group import Group
from lern_table import LearnTable
from statistic_exp_txt_ck import Statistic_Exp_Dir
import logging

logging.basicConfig(level=logging.DEBUG, filename='logfile2.log', 
    format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s')
logger = logging.getLogger(__name__)

app = QtWidgets.QApplication(sys.argv)



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        logger.debug("start of main window")
        self.setWindowTitle("Analyser_v01")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButtonChangeMainDir.clicked.connect(self.changeMainDir)
        self.ui.pushButtonSaveConfig.clicked.connect(self.saveConfig)
        self.config_file_name = "analyse_csv_config.json"
        self.ui.pushButtonChangeStartEstimation.clicked.connect(self.estimate)
        self.ui.pushButtonAddTargetToTable.clicked.connect(self.addTargetToTable)
        self.ui.pushButtonChooseTableFile.clicked.connect(self.chooseTableFile)
        self.ui.pushButtonChangeStatDir.clicked.connect(self.changeStatDir)
        self.ui.pushButtonEstimateStatistics.clicked.connect(self.estimateStatistics)
        self.ui.pushButtonCreateCSV.clicked.connect(self.create_one_csv)
        self.load_last_config()
        
    def load_last_config(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_file = os.path.join(dir_path, "last_dir.json")
        if os.path.isfile(dir_file):
            with open(dir_file, 'r') as j:
                self.config_data = json.load(j)
            self.adapt_gui_to_config()

    def chooseTableFile(self):
        filename = QFileDialog.getOpenFileName()
        self.ui.lineEditTableFile.setText(filename[0])


    def changeMainDir(self):
        # setting the main Directory where all config files and estimations will be saved
#        filename = QFileDialog.getOpenFileName()
        dirname = QFileDialog.getExistingDirectory()
        self.ui.lineEditMainDir.setText(dirname)
        # config file
        self.config_data = {"lineEditMainDir" : self.ui.lineEditMainDir.text()}
        config_file = os.path.join(dirname, self.config_file_name)
        if os.path.isfile(config_file):
            with open(config_file, 'r') as j:
                self.config_data = json.load(j)
            self.adapt_gui_to_config()


    def changeStatDir(self):
        # setting the main Directory where all config files and estimations will be saved
#        filename = QFileDialog.getOpenFileName()
        dirname = QFileDialog.getExistingDirectory()
        self.ui.lineEditStatDir.setText(dirname)


    def saveConfig(self):
        # Idea is to save all parameters in the gui in a json file
        # by loading it will be checked whether the label exist 
        # if so than the value will be used... in the other case than
        # a default value will be used
        config = {
            "lineEditMainDir"                   : self.ui.lineEditMainDir.text(),
            "textEditMSTjson"                   : self.ui.textEditMSTjson.toPlainText(),
            "textEditSEQjson"                   : self.ui.textEditSEQjson.toPlainText(),
            "textEditSRTTjson"                  : self.ui.textEditSRTTjson.toPlainText(),
            "checkBoxEstimateMST"               : self.ui.checkBoxEstimateMST.isChecked(),
            "checkBoxEstimateSEQ"               : self.ui.checkBoxEstimateSEQ.isChecked(),
            "checkBoxEstimateSRTT"              : self.ui.checkBoxEstimateSRTT.isChecked(),
            "spinBoxMultiProcessor"             : self.ui.spinBoxMultiProcessor.value(),
            "lineEditTableFile"                 : self.ui.lineEditTableFile.text(),
            "lineEditTargetGroupFilePattern"    : self.ui.lineEditTargetGroupFilePattern.text(),
            "lineEditStatDir"                   : self.ui.lineEditStatDir.text(),
        }

        with open(os.path.join(self.ui.lineEditMainDir.text(), self.config_file_name), 'w') as file:
            json.dump(config, file)
        # die letzte gespeicherte config soll beim naechsten Start als erstes geladen werden
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "last_dir.json"), 'w') as file:
            json.dump(config, file)


    def adapt_gui_to_config(self):
        # adapts the gui to the json config data in self.config_data
        for (key, value) in self.config_data.items():
            if hasattr(self.ui, key):
                attr = getattr(self.ui, key)
                if "lineEdit" in key:
                    attr.setText(str(value))
                if "textEdit" in key:
                    attr.setText(str(value))
                if "checkBox" in key:
                    attr.setChecked(bool(value))
                if "spinBox" in key:
                    attr. setValue(value)
            
    def estimate(self):
        if self.ui.checkBoxEstimateMST.isChecked():
            self.perform(eval(self.ui.textEditMSTjson.toPlainText()))
        if self.ui.checkBoxEstimateSEQ.isChecked():
            self.perform(eval(self.ui.textEditSEQjson.toPlainText()))
        if self.ui.checkBoxEstimateSRTT.isChecked():
            self.perform(eval(self.ui.textEditSRTTjson.toPlainText()))
        # table = LearnTable(".\\Data_Rogens\\Lernspiel_Auswertung_2020b.csv")
        # table.add_experimental_columns_to_table(dicMST)
        # table.add_to_table(dicMST)

    def perform(self, dic):
        """ es wird ein dictionary mit parametern uebergeben"""
        print(f"num_processes {self.ui.spinBoxMultiProcessor.value()}")
        analysis = Group_analysis(dic["path_outputfiles"])
        if dic["is_perform_analysis"]:
            for group_idx in range(len(dic["filepattern"])):
                analysis.add_group(
                    experiment_name=dic["experiment_name"],
                    path_inputfiles=dic["path_inputfiles"],
                    filepattern=dic["filepattern"][group_idx],
                    path_outputfiles=dic["path_outputfiles"],
                    sequence_length=dic["sequence_length"],
                    _id=dic["_ids"][group_idx],
                    is_estimate_network=dic["is_estimate_network"],
                    is_clustering=dic["is_clustering"],
                    is_multiprocessing=dic["is_multiprocessing"],
                    show_images=dic["show_images"],
                    target_color=dic["target_color"],
                    num_processes=self.ui.spinBoxMultiProcessor.value()
                    )
    def addTargetToTable(self):
        myLearnTable = LearnTable(self.ui.lineEditTableFile.text())
        myLearnTable.add_estimated_results_to_learn_table(
            results_directory = os.path.join(self.ui.lineEditMainDir.text(),"Experiment_data"),
            experiment_name_list = eval(self.ui.lineEditTargetGroupFilePattern.text()))

    def estimateStatistics(self):
        f = "estimate my new statistik"
        print(f)
        self.ui.textBrowserStatistics.setText(f)
        stat = Statistic_Exp_Dir(self.ui.lineEditStatDir.text(), 
                                 self.ui.lineEditMainDir.text(), 
                                 output_filename=self.ui.lineEditOutputFilename.text()
                                 )
        stat.perform_all_available_analyses()
        # self.ui.textBrowserStatistics.setText("\n".join(stat.print_output))
        self.ui.textBrowserStatistics.setText(" ".join(stat.print_output))

    def create_one_csv(self):
        """ creating one big csv with all available data with one line for each experiment"""
        stat = Statistic_Exp_Dir(self.ui.lineEditStatDir.text(), 
                                 self.ui.lineEditMainDir.text(), 
                                 output_filename=self.ui.lineEditOutputFilename.text()
                                 )
        stat.create_one_csv()

if __name__ == '__main__':
    ui_window = MainWindow()
    ui_window.show()
    sys.exit(app.exec_())





# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self, parent = None):
#         super().__init__(parent)
#         self.setWindowTitle("AdminToolTeleStrokeKIDataBase")
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)
#         self.ui.pushButton_import_tables.clicked.connect(self.import_tables)
#         self.ui.pushButton_db_connect.clicked.connect(self.db_connect)
#     def import_tables(self):
#         p = '.\\Exel_Tables'
#         p = self.ui.lineEdit_table_path.text()

# #window = QtWidgets.QMainWindow()
# #window.setWindowTitle("Database Frontend")
# #db_frontend_window.setupUi(window)
# db_frontend_window = MainWindow()
# db_frontend_window.show()

# sys.exit(app.exec_())

