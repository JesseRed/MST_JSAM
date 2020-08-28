import sys
from qtpy import QtWidgets

from ui.mainwindow import Ui_MainWindow

app = QtWidgets.QApplication(sys.argv)

# window = QtWidgets.QMainWindow()
# window.setWindowTitle("Analyser")

# ui_window = Ui_MainWindow()
# ui_window.setupUi(window)

# window.show()

# sys.exit(app.exec_())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setWindowTitle("Analyser_v01")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.test)
        print("main window")

    def test(self):
        print("thats a main window test")


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

