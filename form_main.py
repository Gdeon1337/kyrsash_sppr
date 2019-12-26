from datetime import datetime

from PyQt5 import QtWidgets, QtCore
import os

from view_main import Ui_MainWindow
from PyQt5.QtGui import QPixmap
from fit_lstm import get_plot
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QHeaderView


class ClassMain(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.path_csv = None
        self.path_dohod_csv = None
        self.pushButton.clicked.connect(self.file_dailog)
        self.pushButton_2.clicked.connect(self.train)
        self.pushButton_3.clicked.connect(self.save_model)
        self.pushButton_5.clicked.connect(self.file_dailog_dohod)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tableWidget.verticalHeader().hide()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setHorizontalHeaderLabels(["Дата", "Данные", "Предикт"])
        self.tableWidget.horizontalHeaderItem(0).setToolTip("Дата")
        self.tableWidget.horizontalHeaderItem(1).setToolTip("Изначальные данные")
        self.tableWidget.horizontalHeaderItem(2).setToolTip("Данные полученные спомощью временного ряда")

        self.tableWidget_2.setColumnCount(3)
        self.tableWidget_2.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tableWidget_2.verticalHeader().hide()
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget_2.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget_2.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_2.setHorizontalHeaderLabels(["Дата", "Данные", "Предикт"])
        self.tableWidget_2.horizontalHeaderItem(0).setToolTip("Дата")
        self.tableWidget_2.horizontalHeaderItem(1).setToolTip("Изначальные данные")
        self.tableWidget_2.horizontalHeaderItem(2).setToolTip("Данные полученные спомощью временного ряда")

    def save_model(self):
        if self.model_fit:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fname, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                   "All Files (*);;h5 Files (*.h5)", options=options)
            if fname:
                self.model_fit.save(str(fname))

    def file_dailog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        path_csv = QFileDialog.getOpenFileName(
            self, "Open File", os.getcwd(), "CSV Files (*.csv)", options=options)
        if path_csv:
            self.path_csv = path_csv[0]

    def file_dailog_dohod(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        path_dohod_csv = QFileDialog.getOpenFileName(
            self, "Open File", os.getcwd(), "CSV Files (*.csv)", options=options)
        if path_dohod_csv:
            self.path_dohod_csv = path_dohod_csv[0]

    def train(self):
        plot_image, logger, plot_image_dohod, logger_dohod = get_plot(self.path_csv, self.path_dohod_csv)
        if plot_image:
            pm = QPixmap()
            pm.loadFromData(plot_image)
            self.label.setPixmap(pm.scaled(
                self.label.width(), self.label.height(), QtCore.Qt.KeepAspectRatio))
        if plot_image_dohod:
            pm_ = QPixmap()
            pm_.loadFromData(plot_image_dohod)
            self.label_3.setPixmap(pm_.scaled(
                self.label_3.width(), self.label_3.height(), QtCore.Qt.KeepAspectRatio))
        self.tableWidget.setRowCount(len(logger))
        for i in range(len(logger)):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(datetime.strftime(logger[i].get('date'), '%d:%m:%Y')))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(str(logger[i].get('value'))))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(str(logger[i].get('predict_value'))))
        self.tableWidget.resizeColumnsToContents()

        self.tableWidget_2.setRowCount(len(logger_dohod))
        for i in range(len(logger_dohod)):
            self.tableWidget_2.setItem(i, 0, QTableWidgetItem(datetime.strftime(logger_dohod[i].get('date'), '%d:%m:%Y')))
            self.tableWidget_2.setItem(i, 1, QTableWidgetItem(str(logger_dohod[i].get('value'))))
            self.tableWidget_2.setItem(i, 2, QTableWidgetItem(str(logger_dohod[i].get('predict_value'))))
        self.tableWidget_2.resizeColumnsToContents()
