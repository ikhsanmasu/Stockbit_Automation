from stocbit import StockbitBase
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
from PyQt5.QtWidgets import QApplication, QWidget
import logging
import sys
import os
import re
from cryptography.fernet import Fernet
fernet = Fernet(b's5GlPDeDXT8h49oaBIqrRIruTMgTDpUFH3jhKHZSgMk=')

from start_trading import StartTrading
from update_emiten import UpdateEmiten
import configparser

application_path = getattr(sys, '_MEIPASS', os.getcwd())

file = ".config.ini"
# file = application_path + "/file source/config.ini"
hide_password_icon_dir = application_path + "/file source/hide password.png"
show_password_icon_dir = application_path + "/file source/show password.png"

# file = "config.ini"
# hide_password_icon_dir = "file source/hide password.png"
# show_password_icon_dir = "file source/show password.png"

conf_file = configparser.ConfigParser()
try:
    conf_file.read(file)
    SAVED_EMAIL = conf_file['account']['email']
    SAVED_PASSWORD = bytes(str(fernet.decrypt(conf_file['account']['password'])), 'utf-8').decode()[2:-1]
    SAVED_PIN = bytes(str(fernet.decrypt(conf_file['account']['pin'])), 'utf8').decode()[2:-1]
    # SAVED_PASSWORD = conf_file['account']['password']
    # SAVED_PIN = conf_file['account']['pin']
    SAVED_JAM_TRADING = conf_file['trading']['jam trading']
    SAVED_SALDO_TRADING = conf_file['trading']['saldo trading']
    SAVED_PERSENTASE_HARGA = conf_file['trading']['persentase harga']
    SAVED_JUMLAH_SAHAM = conf_file['trading']['jumlah saham']
    SAVED_RANGE_VALUE = conf_file['trading']['range value']
    SAVED_RANGE_HARGA = conf_file['trading']['range harga']
    SAVED_PRIORITAS1 = conf_file['trading']['prioritas 1']
    SAVED_PRIORITAS2 = conf_file['trading']['prioritas 2']
    SAVED_PRIORITAS3 = conf_file['trading']['prioritas 3']
    SAVED_PRIORITAS4 = conf_file['trading']['prioritas 4']
    SAVED_PRIORITAS5 = conf_file['trading']['prioritas 5']
    SAVED_PRIORITAS6 = conf_file['trading']['prioritas 6']
except:
    SAVED_EMAIL = "email@gmail.com"
    SAVED_PASSWORD = "password"
    SAVED_PIN = "123456"
    SAVED_JAM_LOGIN = "15:50:00"
    SAVED_JAM_TRADING = "16:01:00"
    SAVED_SALDO_TRADING = "1.000.000"
    SAVED_PERSENTASE_HARGA = "5"
    SAVED_JUMLAH_SAHAM = "10"
    SAVED_RANGE_VALUE = "1.000.000.000"
    SAVED_RANGE_HARGA = "100-1.000"
    SAVED_PRIORITAS1 = "100-123"
    SAVED_PRIORITAS2 = "500-615"
    SAVED_PRIORITAS3 = "124-141"
    SAVED_PRIORITAS4 = "627-705"
    SAVED_PRIORITAS5 = "142-197"
    SAVED_PRIORITAS6 = "710-985"

    try:
        conf_file.add_section('account')
    except Exception as e:
        print(e)
    conf_file['account']['email'] = SAVED_EMAIL
    conf_file['account']['password'] = SAVED_PASSWORD
    conf_file['account']['pin'] = SAVED_PIN
    try:
        conf_file.add_section('trading')
    except Exception as e:
        print(e)
    conf_file['trading']['jam trading'] = SAVED_JAM_TRADING
    conf_file['trading']['saldo trading'] = SAVED_SALDO_TRADING
    conf_file['trading']['persentase harga'] = SAVED_PERSENTASE_HARGA
    conf_file['trading']['jumlah saham'] = SAVED_JUMLAH_SAHAM
    conf_file['trading']['range value'] = SAVED_RANGE_VALUE
    conf_file['trading']['range harga'] = SAVED_RANGE_HARGA
    conf_file['trading']['prioritas 1'] = SAVED_PRIORITAS1
    conf_file['trading']['prioritas 2'] = SAVED_PRIORITAS2
    conf_file['trading']['prioritas 3'] = SAVED_PRIORITAS3
    conf_file['trading']['prioritas 4'] = SAVED_PRIORITAS4
    conf_file['trading']['prioritas 5'] = SAVED_PRIORITAS5
    conf_file['trading']['prioritas 6'] = SAVED_PRIORITAS6
    with open(file, 'w') as configfile:
       conf_file.write(configfile)

logging.basicConfig(format="%(message)s", level=logging.INFO)
mutex = QMutex()

class UpdateSaldo(QThread):
    # tes login dan update saldo
    finished = pyqtSignal(str)
    progress = pyqtSignal(str)
    update_saldo = pyqtSignal(str)
    email = None
    password = None
    pin = None

    def run(self):
        try:
            client = StockbitBase()

            response = self.__login(client)

            if response.replace(",", "").isalnum():
                self.update_saldo.emit(f"{response}")
                self.progress.emit(f"{datetime.now()} - INFO - Update saldo berhasil {response}")
            else:
                self.progress.emit(f"{datetime.now()} - WARNING - {response}")

            client.close_driver()
            self.finished.emit(f"{datetime.now()} - INFO - Proses Update Saldo Selesai")
        except:
            self.finished.emit(f"{datetime.now()} - WARNING - Window tertutup saat proses")

    def __login(self, client):
        trying = True
        count = 0
        response = "Fail"
        while trying:
            try:
                client.login(self.progress, email=self.email, password=self.password, pin=self.pin)
                response = client.get_data_saldo()
                trying = False
            except Exception as e:
                if count > 3:
                    self.progress.emit(
                        f"{datetime.now()} - WARNING - Proses Login Gagal sebanyak {count} berhenti mencoba login")
                    trying = False
                    continue
                self.progress.emit(
                    f"{datetime.now()} - WARNING - Proses Login Gagal, mencoba percobaan ke {count + 2} login kembali ")
                count += 1

        self.progress.emit(f"{datetime.now()} - INFO - Proses Update Saldo Selesai")
        return response


class UiStockbitBot(object):
    def setup_ui(self, STOCKBITBOT):

        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.height = self.screenRect.height()
        self.width = self.screenRect.width()

        self.__button_released_style = "color: rgb(255, 255, 255);background-color: rgb(143, 142, 205);\n border-radius: 10px;\n padding: 10px;"
        self.__button_pressed_style = "background-color: rgb(232, 232, 232);\n color: rgb(255, 255, 255);\n border-radius: 10px;\n padding: 10px;"
        self.start_syle = "background-color: rgb(142, 204, 200);\n color: rgb(255, 255, 255);\n border-radius: 10px;\n padding: 10px;"

        self.hide_or_show_icon = QtGui.QIcon()
        self.hide_or_show_icon.addPixmap(QtGui.QPixmap(show_password_icon_dir), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.show_password_icon = QtGui.QIcon()
        self.show_password_icon.addPixmap(QtGui.QPixmap(hide_password_icon_dir), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        if self.width >= 1280:
            STOCKBITBOT.resize(1280, 720)
        else:
            STOCKBITBOT.resize(800, 600)

        STOCKBITBOT.setObjectName("STOCKBITBOT")
        # STOCKBITBOT.resize(800, 600)
        STOCKBITBOT.setMinimumSize(QtCore.QSize(150, 0))
        font = QtGui.QFont()
        font.setPointSize(12)
        STOCKBITBOT.setFont(font)
        STOCKBITBOT.setStyleSheet("background-color: rgb(210, 224, 251);")
        self.centralwidget = QtWidgets.QWidget(STOCKBITBOT)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setStyleSheet("color: rgb(106, 130, 153);")
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 8, 2, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet("color: rgb(106, 130, 153);")
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.update_watchlist_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.update_watchlist_button.sizePolicy().hasHeightForWidth())
        self.update_watchlist_button.setSizePolicy(sizePolicy)
        self.update_watchlist_button.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.update_watchlist_button.setFont(font)
        self.update_watchlist_button.setStyleSheet("color: rgb(255, 255, 255);background-color: rgb(143, 142, 205);\n"
                                                   "border-radius: 10px;\n"
                                                   "padding: 10px;")
        self.update_watchlist_button.setObjectName("update_watchlist_button")
        self.gridLayout_4.addWidget(self.update_watchlist_button, 0, 1, 1, 1)
        self.update_saldo_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.update_saldo_button.sizePolicy().hasHeightForWidth())
        self.update_saldo_button.setSizePolicy(sizePolicy)
        self.update_saldo_button.setMinimumSize(QtCore.QSize(0, 0))
        self.update_saldo_button.setSizeIncrement(QtCore.QSize(0, 0))
        self.update_saldo_button.setBaseSize(QtCore.QSize(10, 10))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.update_saldo_button.setFont(font)
        self.update_saldo_button.setStyleSheet("background-color: rgb(143, 142, 205);\n"
                                               "color: rgb(255, 255, 255);\n"
                                               "border-radius: 10px;\n"
                                               "padding: 1px;\n"
                                               "")
        self.update_saldo_button.setCheckable(False)
        self.update_saldo_button.setAutoDefault(False)
        self.update_saldo_button.setDefault(False)
        self.update_saldo_button.setFlat(False)
        self.update_saldo_button.setObjectName("update_saldo_button")
        self.gridLayout_4.addWidget(self.update_saldo_button, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_4, 6, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 6, 3, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 5, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.activity_log_button = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.activity_log_button.sizePolicy().hasHeightForWidth())
        self.activity_log_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.activity_log_button.setFont(font)
        self.activity_log_button.setStyleSheet("color: rgb(106, 130, 153);")
        self.activity_log_button.setObjectName("activity_log_button")
        self.horizontalLayout_3.addWidget(self.activity_log_button)
        self.timer_start_trading = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.timer_start_trading.sizePolicy().hasHeightForWidth())
        self.timer_start_trading.setSizePolicy(sizePolicy)
        self.timer_start_trading.setStyleSheet("color: rgb(255, 0, 0);")
        self.timer_start_trading.setText("")
        self.timer_start_trading.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.timer_start_trading.setObjectName("timer_start_trading")
        self.horizontalLayout_3.addWidget(self.timer_start_trading)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 4, 1, 1)
        self.loggerPanel = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.loggerPanel.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loggerPanel.sizePolicy().hasHeightForWidth())
        self.loggerPanel.setSizePolicy(sizePolicy)
        self.loggerPanel.setMinimumSize(QtCore.QSize(300, 0))
        self.loggerPanel.setSizeIncrement(QtCore.QSize(5, 0))
        self.loggerPanel.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.loggerPanel.setFont(font)
        self.loggerPanel.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "color: rgb(0, 0, 0);\n"
                                       "padding: 10px;")
        self.loggerPanel.setPlainText("")
        self.loggerPanel.setObjectName("loggerPanel")
        self.gridLayout.addWidget(self.loggerPanel, 2, 4, 11, 1)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem4, 1, 2, 1, 1)
        self.pin_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pin_label.setFont(font)
        self.pin_label.setStyleSheet("color: rgb(106, 130, 153);")
        self.pin_label.setObjectName("pin_label")
        self.gridLayout_3.addWidget(self.pin_label, 2, 1, 1, 1)
        self.pin_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pin_input.sizePolicy().hasHeightForWidth())
        self.pin_input.setSizePolicy(sizePolicy)
        self.pin_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pin_input.setFont(font)
        self.pin_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                     "border-radius: 10px;\n"
                                     "color: rgb(255, 255, 255);\n"
                                     "padding: 8px;\n"
                                     "background-color: rgb(142, 172, 205);")
        self.pin_input.setObjectName("pin_input")
        self.gridLayout_3.addWidget(self.pin_input, 2, 3, 1, 1)
        self.password_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.password_input.sizePolicy().hasHeightForWidth())
        self.password_input.setSizePolicy(sizePolicy)
        self.password_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.password_input.setFont(font)
        self.password_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                          "border-radius: 10px;\n"
                                          "background-color: rgb(142, 172, 205);\n"
                                          "color: rgb(255, 255, 255);\n"
                                          "padding:8px;")
        self.password_input.setObjectName("password_input")
        self.gridLayout_3.addWidget(self.password_input, 1, 3, 1, 1)
        self.password_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.password_label.setFont(font)
        self.password_label.setStyleSheet("color: rgb(106, 130, 153);")
        self.password_label.setObjectName("password_label")
        self.gridLayout_3.addWidget(self.password_label, 1, 1, 1, 1)
        self.email_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.email_label.setFont(font)
        self.email_label.setStyleSheet("color: rgb(106, 130, 153);")
        self.email_label.setObjectName("email_label")
        self.gridLayout_3.addWidget(self.email_label, 0, 1, 1, 1)
        self.hide_pin_button = QtWidgets.QPushButton(self.centralwidget)
        self.hide_pin_button.setStyleSheet("border-radius: 10px;\n"
                                           "padding: 5x;")
        self.hide_pin_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../stocbit2/file source/show password.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.hide_pin_button.setIcon(self.hide_or_show_icon)
        self.hide_pin_button.setObjectName("hide_pin_button")
        self.gridLayout_3.addWidget(self.hide_pin_button, 2, 4, 1, 1)
        self.email_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.email_input.sizePolicy().hasHeightForWidth())
        self.email_input.setSizePolicy(sizePolicy)
        self.email_input.setMinimumSize(QtCore.QSize(0, 0))
        self.email_input.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.email_input.setFont(font)
        self.email_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 255, 255);")
        self.email_input.setObjectName("email_input")
        self.gridLayout_3.addWidget(self.email_input, 0, 3, 1, 2)
        self.hide_password_button = QtWidgets.QPushButton(self.centralwidget)
        self.hide_password_button.setStyleSheet("border-radius: 10px;\n"
                                                "padding: 5x;")
        self.hide_password_button.setText("")
        self.hide_password_button.setIcon(self.hide_or_show_icon)
        self.hide_password_button.setObjectName("hide_password_button")
        self.gridLayout_3.addWidget(self.hide_password_button, 1, 4, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 2, 2, 1, 1)
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem5, 6, 2, 1, 1)
        self.prioritas5_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prioritas5_input.sizePolicy().hasHeightForWidth())
        self.prioritas5_input.setSizePolicy(sizePolicy)
        self.prioritas5_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.prioritas5_input.setFont(font)
        self.prioritas5_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                            "border-radius: 10px;\n"
                                            "background-color: rgb(142, 172, 205);\n"
                                            "color: rgb(255, 255, 255);\n"
                                            "padding: 5px;")
        self.prioritas5_input.setObjectName("prioritas5_input")
        self.gridLayout_6.addWidget(self.prioritas5_input, 5, 4, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setStyleSheet("color: rgb(106, 130, 153);")
        self.label_7.setObjectName("label_7")
        self.gridLayout_6.addWidget(self.label_7, 6, 3, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setStyleSheet("color: rgb(106, 130, 153);")
        self.label_5.setObjectName("label_5")
        self.gridLayout_6.addWidget(self.label_5, 5, 3, 1, 1)
        self.prioritas2_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prioritas2_input.sizePolicy().hasHeightForWidth())
        self.prioritas2_input.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.prioritas2_input.setFont(font)
        self.prioritas2_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                            "border-radius: 10px;\n"
                                            "background-color: rgb(142, 172, 205);\n"
                                            "color: rgb(255, 255, 255);\n"
                                            "padding: 5px;")
        self.prioritas2_input.setObjectName("prioritas2_input")
        self.gridLayout_6.addWidget(self.prioritas2_input, 2, 4, 1, 1)
        self.prioritas1_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prioritas1_input.sizePolicy().hasHeightForWidth())
        self.prioritas1_input.setSizePolicy(sizePolicy)
        self.prioritas1_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.prioritas1_input.setFont(font)
        self.prioritas1_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                            "border-radius: 10px;\n"
                                            "color: rgb(255, 255, 255);\n"
                                            "padding: 5px;\n"
                                            "background-color: rgb(142, 172, 205);")
        self.prioritas1_input.setObjectName("prioritas1_input")
        self.gridLayout_6.addWidget(self.prioritas1_input, 1, 4, 1, 1)
        self.range_harga_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.range_harga_label.setFont(font)
        self.range_harga_label.setStyleSheet("color: rgb(106, 130, 153);")
        self.range_harga_label.setObjectName("range_harga_label")
        self.gridLayout_6.addWidget(self.range_harga_label, 6, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: rgb(106, 130, 153);")
        self.label_2.setObjectName("label_2")
        self.gridLayout_6.addWidget(self.label_2, 2, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("color: rgb(106, 130, 153);")
        self.label.setObjectName("label")
        self.gridLayout_6.addWidget(self.label, 1, 3, 1, 1)
        self.prioritas6_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prioritas6_input.sizePolicy().hasHeightForWidth())
        self.prioritas6_input.setSizePolicy(sizePolicy)
        self.prioritas6_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.prioritas6_input.setFont(font)
        self.prioritas6_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                            "border-radius: 10px;\n"
                                            "background-color: rgb(142, 172, 205);\n"
                                            "color: rgb(255, 255, 255);\n"
                                            "padding: 5px;")
        self.prioritas6_input.setObjectName("prioritas6_input")
        self.gridLayout_6.addWidget(self.prioritas6_input, 6, 4, 1, 1)
        self.range_harga_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.range_harga_input.sizePolicy().hasHeightForWidth())
        self.range_harga_input.setSizePolicy(sizePolicy)
        self.range_harga_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.range_harga_input.setFont(font)
        self.range_harga_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                             "border-radius: 10px;\n"
                                             "background-color: rgb(142, 172, 205);\n"
                                             "color: rgb(255, 255, 255);\n"
                                             "padding: 5px;")
        self.range_harga_input.setObjectName("range_harga_input")
        self.gridLayout_6.addWidget(self.range_harga_input, 6, 1, 1, 1)
        self.prioritas3_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prioritas3_input.sizePolicy().hasHeightForWidth())
        self.prioritas3_input.setSizePolicy(sizePolicy)
        self.prioritas3_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.prioritas3_input.setFont(font)
        self.prioritas3_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                            "border-radius: 10px;\n"
                                            "background-color: rgb(142, 172, 205);\n"
                                            "color: rgb(255, 255, 255);\n"
                                            "padding: 5px;")
        self.prioritas3_input.setObjectName("prioritas3_input")
        self.gridLayout_6.addWidget(self.prioritas3_input, 3, 4, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("color: rgb(106, 130, 153);")
        self.label_3.setObjectName("label_3")
        self.gridLayout_6.addWidget(self.label_3, 3, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet("color: rgb(106, 130, 153);")
        self.label_4.setObjectName("label_4")
        self.gridLayout_6.addWidget(self.label_4, 4, 3, 1, 1)
        self.prioritas4_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.prioritas4_input.sizePolicy().hasHeightForWidth())
        self.prioritas4_input.setSizePolicy(sizePolicy)
        self.prioritas4_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.prioritas4_input.setFont(font)
        self.prioritas4_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                            "border-radius: 10px;\n"
                                            "background-color: rgb(142, 172, 205);\n"
                                            "color: rgb(255, 255, 255);\n"
                                            "padding: 5px;")
        self.prioritas4_input.setObjectName("prioritas4_input")
        self.gridLayout_6.addWidget(self.prioritas4_input, 4, 4, 1, 1)
        self.persentase_saham_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.persentase_saham_input.sizePolicy().hasHeightForWidth())
        self.persentase_saham_input.setSizePolicy(sizePolicy)
        self.persentase_saham_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.persentase_saham_input.setFont(font)
        self.persentase_saham_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                                  "border-radius: 10px;\n"
                                                  "background-color: rgb(142, 172, 205);\n"
                                                  "color: rgb(255, 255, 255);\n"
                                                  "padding: 5px;")
        self.persentase_saham_input.setObjectName("persentase_saham_input")
        self.gridLayout_6.addWidget(self.persentase_saham_input, 3, 1, 1, 1)
        self.range_value_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.range_value_label.setFont(font)
        self.range_value_label.setStyleSheet("color: rgb(106, 130, 153);")
        self.range_value_label.setObjectName("range_value_label")
        self.gridLayout_6.addWidget(self.range_value_label, 5, 0, 1, 1)
        self.jumlah_saham_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.jumlah_saham_input.sizePolicy().hasHeightForWidth())
        self.jumlah_saham_input.setSizePolicy(sizePolicy)
        self.jumlah_saham_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.jumlah_saham_input.setFont(font)
        self.jumlah_saham_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                              "border-radius: 10px;\n"
                                              "background-color: rgb(142, 172, 205);\n"
                                              "color: rgb(255, 255, 255);\n"
                                              "padding: 5px;")
        self.jumlah_saham_input.setObjectName("jumlah_saham_input")
        self.gridLayout_6.addWidget(self.jumlah_saham_input, 4, 1, 1, 1)
        self.max_saham_dibeli_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.max_saham_dibeli_label.setFont(font)
        self.max_saham_dibeli_label.setStyleSheet("color: rgb(106, 130, 153);")
        self.max_saham_dibeli_label.setObjectName("max_saham_dibeli_label")
        self.gridLayout_6.addWidget(self.max_saham_dibeli_label, 4, 0, 1, 1)
        self.persentase_kenaikan_saham_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.persentase_kenaikan_saham_label.setFont(font)
        self.persentase_kenaikan_saham_label.setStyleSheet("color: rgb(106, 130, 153);")
        self.persentase_kenaikan_saham_label.setObjectName("persentase_kenaikan_saham_label")
        self.gridLayout_6.addWidget(self.persentase_kenaikan_saham_label, 3, 0, 1, 1)
        self.saldo_trading_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.saldo_trading_label.setFont(font)
        self.saldo_trading_label.setStyleSheet("color: rgb(106, 130, 153);")
        self.saldo_trading_label.setObjectName("saldo_trading_label")
        self.gridLayout_6.addWidget(self.saldo_trading_label, 2, 0, 1, 1)
        self.jam_trading_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.jam_trading_label.setFont(font)
        self.jam_trading_label.setStyleSheet("color: rgb(106, 130, 153);")
        self.jam_trading_label.setObjectName("jam_trading_label")
        self.gridLayout_6.addWidget(self.jam_trading_label, 1, 0, 1, 1)
        self.jam_trading_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.jam_trading_input.sizePolicy().hasHeightForWidth())
        self.jam_trading_input.setSizePolicy(sizePolicy)
        self.jam_trading_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.jam_trading_input.setFont(font)
        self.jam_trading_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                             "border-radius: 10px;\n"
                                             "background-color: rgb(142, 172, 205);\n"
                                             "color: rgb(255, 255, 255);\n"
                                             "padding: 5px;")
        self.jam_trading_input.setObjectName("jam_trading_input")
        self.gridLayout_6.addWidget(self.jam_trading_input, 1, 1, 1, 1)
        self.range_value_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.range_value_input.sizePolicy().hasHeightForWidth())
        self.range_value_input.setSizePolicy(sizePolicy)
        self.range_value_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.range_value_input.setFont(font)
        self.range_value_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                             "border-radius: 10px;\n"
                                             "background-color: rgb(142, 172, 205);\n"
                                             "color: rgb(255, 255, 255);\n"
                                             "padding: 5px;")
        self.range_value_input.setObjectName("range_value_input")
        self.gridLayout_6.addWidget(self.range_value_input, 5, 1, 1, 1)
        self.saldo_trading_input = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saldo_trading_input.sizePolicy().hasHeightForWidth())
        self.saldo_trading_input.setSizePolicy(sizePolicy)
        self.saldo_trading_input.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.saldo_trading_input.setFont(font)
        self.saldo_trading_input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                               "border-radius: 10px;\n"
                                               "background-color: rgb(142, 172, 205);\n"
                                               "color: rgb(255, 255, 255);\n"
                                               "padding: 5px;")
        self.saldo_trading_input.setObjectName("saldo_trading_input")
        self.gridLayout_6.addWidget(self.saldo_trading_input, 2, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_6, 9, 2, 1, 1)
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start_button.sizePolicy().hasHeightForWidth())
        self.start_button.setSizePolicy(sizePolicy)
        self.start_button.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.start_button.setFont(font)
        self.start_button.setStyleSheet("background-color: rgb(142, 204, 200);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "border-radius: 10px;\n"
                                        "padding: 10px;")
        self.start_button.setObjectName("start_button")
        self.gridLayout.addWidget(self.start_button, 11, 2, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem6, 13, 4, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem7, 7, 2, 1, 1)
        STOCKBITBOT.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(STOCKBITBOT)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        STOCKBITBOT.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(STOCKBITBOT)
        self.statusbar.setObjectName("statusbar")
        STOCKBITBOT.setStatusBar(self.statusbar)

        self.retranslateUi(STOCKBITBOT)
        QtCore.QMetaObject.connectSlotsByName(STOCKBITBOT)
        STOCKBITBOT.setTabOrder(self.email_input, self.password_input)
        STOCKBITBOT.setTabOrder(self.password_input, self.pin_input)
        STOCKBITBOT.setTabOrder(self.pin_input, self.update_saldo_button)
        STOCKBITBOT.setTabOrder(self.update_saldo_button, self.update_watchlist_button)
        STOCKBITBOT.setTabOrder(self.update_watchlist_button, self.jam_trading_input)
        STOCKBITBOT.setTabOrder(self.jam_trading_input, self.saldo_trading_input)
        STOCKBITBOT.setTabOrder(self.saldo_trading_input, self.persentase_saham_input)
        STOCKBITBOT.setTabOrder(self.persentase_saham_input, self.jumlah_saham_input)
        STOCKBITBOT.setTabOrder(self.jumlah_saham_input, self.range_value_input)
        STOCKBITBOT.setTabOrder(self.range_value_input, self.range_harga_input)
        STOCKBITBOT.setTabOrder(self.range_harga_input, self.prioritas1_input)
        STOCKBITBOT.setTabOrder(self.prioritas1_input, self.prioritas2_input)
        STOCKBITBOT.setTabOrder(self.prioritas2_input, self.prioritas3_input)
        STOCKBITBOT.setTabOrder(self.prioritas3_input, self.prioritas4_input)
        STOCKBITBOT.setTabOrder(self.prioritas4_input, self.prioritas5_input)
        STOCKBITBOT.setTabOrder(self.prioritas5_input, self.prioritas6_input)
        STOCKBITBOT.setTabOrder(self.prioritas6_input, self.start_button)
        STOCKBITBOT.setTabOrder(self.start_button, self.hide_password_button)
        STOCKBITBOT.setTabOrder(self.hide_password_button, self.hide_pin_button)
        STOCKBITBOT.setTabOrder(self.hide_pin_button, self.loggerPanel)

        self.addition_init_setup()

    def retranslateUi(self, STOCKBITBOT):
        _translate = QtCore.QCoreApplication.translate
        STOCKBITBOT.setWindowTitle(_translate("STOCKBITBOT", "Stockbit Bot"))
        self.label_8.setText(_translate("STOCKBITBOT", "TRADING DATA"))
        self.label_6.setText(_translate("STOCKBITBOT", "LOGIN DATA"))
        self.update_watchlist_button.setText(_translate("STOCKBITBOT", "UPDATE WATCHLIST"))
        self.update_saldo_button.setText(_translate("STOCKBITBOT", " UPDATE SALDO"))
        self.activity_log_button.setText(_translate("STOCKBITBOT", "ACTIVITY LOG"))
        self.pin_label.setText(_translate("STOCKBITBOT", "Pin"))
        self.pin_input.setText(_translate("STOCKBITBOT", "********"))
        self.password_input.setText(_translate("STOCKBITBOT", "*********"))
        self.password_label.setText(_translate("STOCKBITBOT", "Password"))
        self.email_label.setText(_translate("STOCKBITBOT", "Email"))
        self.email_input.setText(_translate("STOCKBITBOT", "email@gmail.com"))
        self.prioritas5_input.setText(_translate("STOCKBITBOT", "142-197"))
        self.label_7.setText(_translate("STOCKBITBOT", "Prioritas 6"))
        self.label_5.setText(_translate("STOCKBITBOT", "Prioritas 5"))
        self.prioritas2_input.setText(_translate("STOCKBITBOT", "500-615"))
        self.prioritas1_input.setText(_translate("STOCKBITBOT", "100-123"))
        self.range_harga_label.setText(_translate("STOCKBITBOT", "Range Harga"))
        self.label_2.setText(_translate("STOCKBITBOT", "Prioritas 2"))
        self.label.setText(_translate("STOCKBITBOT", "Prioritas 1"))
        self.prioritas6_input.setText(_translate("STOCKBITBOT", "710-985"))
        self.range_harga_input.setText(_translate("STOCKBITBOT", "100-1.000"))
        self.prioritas3_input.setText(_translate("STOCKBITBOT", "124-141"))
        self.label_3.setText(_translate("STOCKBITBOT", "Prioritas 3"))
        self.label_4.setText(_translate("STOCKBITBOT", "Prioritas 4"))
        self.prioritas4_input.setText(_translate("STOCKBITBOT", "620-705"))
        self.persentase_saham_input.setText(_translate("STOCKBITBOT", "5"))
        self.range_value_label.setText(_translate("STOCKBITBOT", "Minimal Value"))
        self.jumlah_saham_input.setText(_translate("STOCKBITBOT", "5"))
        self.max_saham_dibeli_label.setText(_translate("STOCKBITBOT", "Jumlah Saham"))
        self.persentase_kenaikan_saham_label.setText(_translate("STOCKBITBOT", "% Minimal"))
        self.saldo_trading_label.setText(_translate("STOCKBITBOT", "Saldo Trading"))
        self.jam_trading_label.setText(_translate("STOCKBITBOT", "Jam Trading"))
        self.jam_trading_input.setText(_translate("STOCKBITBOT", "16:01:00"))
        self.range_value_input.setText(_translate("STOCKBITBOT", "1.000.000.000"))
        self.saldo_trading_input.setText(_translate("STOCKBITBOT", "1.000.000"))
        self.start_button.setText(_translate("STOCKBITBOT", "START BOT"))

        self.email_input.setText(_translate("STOCKBITBOT", SAVED_EMAIL))
        self.password_input.setText(_translate("STOCKBITBOT", SAVED_PASSWORD))
        self.pin_input.setText(_translate("STOCKBITBOT", SAVED_PIN))
        self.jam_trading_input.setText(_translate("STOCKBITBOT", SAVED_JAM_TRADING))
        self.saldo_trading_input.setText(_translate("STOCKBITBOT", SAVED_SALDO_TRADING))
        self.persentase_saham_input.setText(_translate("STOCKBITBOT", SAVED_PERSENTASE_HARGA))
        self.jumlah_saham_input.setText(_translate("STOCKBITBOT", SAVED_JUMLAH_SAHAM))
        self.range_value_input.setText(_translate("STOCKBITBOT", SAVED_RANGE_VALUE))
        self.range_harga_input.setText(_translate("STOCKBITBOT", SAVED_RANGE_HARGA))
        self.prioritas1_input.setText(_translate("STOCKBITBOT", SAVED_PRIORITAS1))
        self.prioritas2_input.setText(_translate("STOCKBITBOT", SAVED_PRIORITAS2))
        self.prioritas3_input.setText(_translate("STOCKBITBOT", SAVED_PRIORITAS3))
        self.prioritas4_input.setText(_translate("STOCKBITBOT", SAVED_PRIORITAS4))
        self.prioritas5_input.setText(_translate("STOCKBITBOT", SAVED_PRIORITAS5))
        self.prioritas6_input.setText(_translate("STOCKBITBOT", SAVED_PRIORITAS6))

    def addition_init_setup(self):
        self.button_linking()
        self.create_update_saldo_thread()
        self.create_update_watchlist_thread()
        self.create_start_trading_thread()
        self.update_config_file()

    def button_linking(self):
        # hide and show typed password
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.hide_password_button.clicked.connect(self.change_visibility_password)

        # hide and show typed pin
        self.pin_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.hide_pin_button.clicked.connect(self.change_visibility_pin)

        # update saldo button clicked style
        self.update_saldo_button.pressed.connect(self.pressed_login_style)
        self.update_saldo_button.released.connect(self.normal_login_style)

        # update watchlist button clicked style
        self.update_watchlist_button.pressed.connect(self.pressed_watchlist_style)
        self.update_watchlist_button.released.connect(self.normal_watchlist_style)

        # update saldo start
        self.update_saldo_button.pressed.connect(self.change_update_saldo_parameter)
        self.update_saldo_button.released.connect(self.update_saldo_start)

        # update wathclist start
        self.update_watchlist_button.pressed.connect(self.change_update_watchlist_parameter)
        self.update_watchlist_button.released.connect(self.update_watchlist_start)

        # start bot start
        self.start_button.pressed.connect(self.start_cancle_pressed)
        self.start_button.released.connect(self.start_cancle_released)

        # start bot button clicked style
        self.start_button.pressed.connect(self.pressed_start_style)
        self.start_button.released.connect(self.normal_start_style)

        self.email_input.textChanged.connect(self.update_config_file)
        self.password_input.textChanged.connect(self.update_config_file)
        self.pin_input.textChanged.connect(self.update_config_file)
        self.jam_trading_input.textChanged.connect(self.update_config_file)
        self.saldo_trading_input.textChanged.connect(self.update_config_file)
        self.persentase_saham_input.textChanged.connect(self.update_config_file)
        self.jumlah_saham_input.textChanged.connect(self.update_config_file)
        self.range_value_input.textChanged.connect(self.update_config_file)
        self.range_harga_input.textChanged.connect(self.update_config_file)
        self.prioritas1_input.textChanged.connect(self.update_config_file)
        self.prioritas2_input.textChanged.connect(self.update_config_file)
        self.prioritas3_input.textChanged.connect(self.update_config_file)
        self.prioritas4_input.textChanged.connect(self.update_config_file)
        self.prioritas5_input.textChanged.connect(self.update_config_file)
        self.prioritas6_input.textChanged.connect(self.update_config_file)

    def start_cancle_pressed(self):
        if self.start_button.text() == "START BOT":
            self.change_start_trading_parameter()

    def start_cancle_released(self):
        if self.start_button.text() == "START BOT":
            self.start_trading()
        else:
            self.stockbit_start_trading.terminate()
            # self.stockbit_start_trading.client.close_driver()
            self.update_logging(f"{datetime.now()} - INFO - tombol CANCLE BOT ditekan")
            self.timer_start_trading.setText("")
            self.enable_all_button()

    def create_update_saldo_thread(self):
        self.stockbit_login = UpdateSaldo()
        self.stockbit_login.finished.connect(self.enable_all_button)
        self.stockbit_login.finished.connect(self.update_logging)
        self.stockbit_login.progress.connect(self.update_logging)
        self.stockbit_login.update_saldo.connect(self.update_saldo)

    def update_button(self):
        self.start_button.setText("START BOT")
        self.start_button.setStyleSheet(self.start_syle)

    def create_update_watchlist_thread(self):
        self.update_wathlist_thread = UpdateEmiten()
        self.update_wathlist_thread.finished.connect(self.enable_all_button)
        self.update_wathlist_thread.finished.connect(self.update_logging)
        self.update_wathlist_thread.progress.connect(self.update_logging)

    def create_start_trading_thread(self):
        self.stockbit_start_trading = StartTrading()
        self.stockbit_start_trading.finished.connect(self.update_button)
        self.stockbit_start_trading.finished.connect(self.enable_all_button)
        self.stockbit_start_trading.finished.connect(self.update_logging)
        self.stockbit_start_trading.progress.connect(self.update_logging)
        self.stockbit_start_trading.update_timer.connect(self.update_timer)

    def change_update_saldo_parameter(self):
        self.disable_all_button()
        self.stockbit_login.email = self.email_input.text()
        self.stockbit_login.password = self.password_input.text()
        self.stockbit_login.pin = self.pin_input.text()

    def change_update_watchlist_parameter(self):
        self.disable_all_button()
        self.update_wathlist_thread.email = self.email_input.text()
        self.update_wathlist_thread.password = self.password_input.text()
        self.update_wathlist_thread.pin = self.pin_input.text()

    def change_start_trading_parameter(self):
        self.disable_except_start_button()

        self.stockbit_start_trading.email = self.email_input.text()
        self.stockbit_start_trading.password = self.password_input.text()
        self.stockbit_start_trading.pin = self.pin_input.text()

        self.stockbit_start_trading.jam_trading = self.jam_trading_input.text()
        self.stockbit_start_trading.saldo_trading = self.saldo_trading_input.text()
        self.stockbit_start_trading.persentase_minimum = float(self.persentase_saham_input.text().replace(".", "").replace(",", ".").replace("%",""))
        self.stockbit_start_trading.jumlah_emiten = int(self.jumlah_saham_input.text())

        self.stockbit_start_trading.range_value = self.range_value_input.text().replace(".", "").replace("_", "")
        self.stockbit_start_trading.range_harga = self.range_harga_input.text().replace(".", "").replace("_", "")

        self.stockbit_start_trading.prioritas1 = self.prioritas1_input.text().replace(".", "").replace("_", "")
        self.stockbit_start_trading.prioritas2 = self.prioritas2_input.text().replace(".", "").replace("_", "")
        self.stockbit_start_trading.prioritas3 = self.prioritas3_input.text().replace(".", "").replace("_", "")
        self.stockbit_start_trading.prioritas4 = self.prioritas4_input.text().replace(".", "").replace("_", "")
        self.stockbit_start_trading.prioritas5 = self.prioritas5_input.text().replace(".", "").replace("_", "")
        self.stockbit_start_trading.prioritas6 = self.prioritas6_input.text().replace(".", "").replace("_", "")

    # button update saldo
    def update_saldo_start(self):
        self.update_logging(f"{datetime.now()} - INFO - Update Saldo ditekan")
        try:
            self.stockbit_login.start()
        except Exception as e:
            self.loggerPanel.appendPlainText(e)

    # button update emiten
    def update_watchlist_start(self):
        self.update_logging(f"{datetime.now()} - INFO - Update Watchlist ditekan")
        try:
            self.update_wathlist_thread.start()
        except Exception as e:
            self.loggerPanel.appendPlainText(e)

    # button start trading
    def start_trading(self):
        self.update_logging(f"{datetime.now()} - INFO - tombol START BOT ditekan")
        try:
            self.stockbit_start_trading.start()
        except Exception as e:
            self.loggerPanel.appendPlainText(e)

    #------- UPDATING
    def update_config_file(self):
        self.validate_email(self.email_input)
        self.validate_password(self.password_input)
        self.validate_pin(self.pin_input)

        self.validate_jam(self.jam_trading_input)
        self.validate_harga(self.saldo_trading_input)
        self.validate_persen(self.persentase_saham_input)
        self.validate_harga(self.jumlah_saham_input)
        self.validate_harga(self.range_value_input)
        self.validate_range_harga(self.range_harga_input)

        self.validate_range(self.prioritas1_input)
        self.validate_range(self.prioritas2_input)
        self.validate_range(self.prioritas3_input)
        self.validate_range(self.prioritas4_input)
        self.validate_range(self.prioritas5_input)
        self.validate_range(self.prioritas6_input)

        # Use like normal configparser class
        # conf_file.add_section('account')
        conf_file['account']['email'] = self.email_input.text().replace("%", "%%")
        __password = str(fernet.encrypt(str(self.password_input.text()).encode()))[2:-1]
        conf_file['account']['password'] = __password
        __pin = str(fernet.encrypt(str(self.pin_input.text()).encode()))[2:-1]
        conf_file['account']['pin'] = __pin
        # conf_file['account']['password'] = self.password_input.text()
        # conf_file['account']['pin'] = self.pin_input.text()

        # Use like normal configparser class
        # conf_file.add_section('trading')
        conf_file['trading']['jam trading'] = self.jam_trading_input.text().replace("%", "%%")
        conf_file['trading']['saldo trading'] = self.saldo_trading_input.text().replace("%", "%%")
        conf_file['trading']['persentase harga'] = self.persentase_saham_input.text().replace("%", "%%")
        conf_file['trading']['jumlah saham'] = self.jumlah_saham_input.text().replace("%", "%%")
        conf_file['trading']['range value'] = self.range_value_input.text().replace("%", "%%")
        conf_file['trading']['range harga'] = self.range_harga_input.text().replace("%", "%%")
        conf_file['trading']['prioritas 1'] = self.prioritas1_input.text().replace("%", "%%")
        conf_file['trading']['prioritas 2'] = self.prioritas2_input.text().replace("%", "%%")
        conf_file['trading']['prioritas 3'] = self.prioritas3_input.text().replace("%", "%%")
        conf_file['trading']['prioritas 4'] = self.prioritas4_input.text().replace("%", "%%")
        conf_file['trading']['prioritas 5'] = self.prioritas5_input.text().replace("%", "%%")
        conf_file['trading']['prioritas 6'] = self.prioritas6_input.text().replace("%", "%%")

        # Write encrypted config file
        with open(file, 'w') as file_handle:
            conf_file.write(file_handle)

    def validate_email(self, input):
        regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
        if self.isValid(regex, input.text()):
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 255, 255);")
        else:
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 0, 0);")

    def validate_password(self, input):
        regex = re.compile(r'^.{6,}$')
        if self.isValid(regex, input.text()):
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 255, 255);")
        else:
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 0, 0);")

    def validate_pin(self, input):
        regex = re.compile(r"\d{6}")
        if self.isValid(regex, input.text()):
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 255, 255);")
        else:
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 0, 0);")

    def validate_jam(self, input):
        regex = re.compile(r'^(?:[01]\d|2[0-4]):[0-5]\d:[0-5]\d$')
        if self.isValid(regex, input.text()):
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 255, 255);")
        else:
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 0, 0);")

    def validate_persen(self, input):
        regex = re.compile(r"^[0-9.,]+%?$")
        if self.isValid(regex, input.text()):
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 255, 255);")
        else:
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 0, 0);")

    def validate_harga(self, input):
        regex = re.compile(r"^[\d.,]+$")
        if self.isValid(regex, input.text()):
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 255, 255);")
        else:
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 0, 0);")

    def validate_range_harga(self, input):
        regex = re.compile(r"^[\d.]+-[\d.]+$")
        if self.isValid(regex, input.text()):
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 255, 255);")
        else:
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 0, 0);")

    def validate_range(self, input):
        regex = re.compile(r"^\d+-\d+$")
        if self.isValid(regex, input.text()):
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 255, 255);")
        else:
            input.setStyleSheet("border-color: rgb(0, 255, 127);\n"
                                       "border-radius: 10px;\n"
                                       "background-color: rgb(142, 172, 205);\n"
                                       "padding: 8px;\n"
                                       "color: rgb(255, 0, 0);")

    def isValid(self, regex, email):
        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def update_logging(self, string):
        self.loggerPanel.appendPlainText(string)

    def update_timer(self, string):
        self.timer_start_trading.setText(string)

    def update_saldo(self, string):
        # penulisan mata uang di indonesia umumnya . untuk ribuan , untuk change Rp 100.000
        harga = string.replace(".", "*")
        harga = harga.replace(",", ".")
        harga = harga.replace("*", ",")
        self.saldo_trading_input.setText(harga)

    #-------- UI
    def disable_all_button(self):
        self.update_saldo_button.setDisabled(True)
        self.update_watchlist_button.setDisabled(True)
        self.start_button.setDisabled(True)
        self.pressed_start_style()
        self.pressed_login_style()
        self.pressed_watchlist_style()

        self.email_input.setDisabled(True)
        self.password_input.setDisabled(True)
        self.pin_input.setDisabled(True)

        self.jam_trading_input.setDisabled(True)
        self.saldo_trading_input.setDisabled(True)
        self.persentase_saham_input.setDisabled(True)
        self.jumlah_saham_input.setDisabled(True)
        self.range_value_input.setDisabled(True)
        self.range_harga_input.setDisabled(True)

        self.prioritas1_input.setDisabled(True)
        self.prioritas2_input.setDisabled(True)
        self.prioritas3_input.setDisabled(True)
        self.prioritas4_input.setDisabled(True)
        self.prioritas5_input.setDisabled(True)
        self.prioritas6_input.setDisabled(True)

        disable_style = "border-color: rgb(232, 232, 232); border-radius: 10px;color: rgb(255, 255, 255);padding: 8px;"

        self.email_input.setStyleSheet(disable_style)
        self.password_input.setStyleSheet(disable_style)
        self.pin_input.setStyleSheet(disable_style)

        self.jam_trading_input.setStyleSheet(disable_style)
        self.saldo_trading_input.setStyleSheet(disable_style)
        self.persentase_saham_input.setStyleSheet(disable_style)
        self.jumlah_saham_input.setStyleSheet(disable_style)
        self.range_value_input.setStyleSheet(disable_style)
        self.range_harga_input.setStyleSheet(disable_style)

        self.prioritas1_input.setStyleSheet(disable_style)
        self.prioritas2_input.setStyleSheet(disable_style)
        self.prioritas3_input.setStyleSheet(disable_style)
        self.prioritas4_input.setStyleSheet(disable_style)
        self.prioritas5_input.setStyleSheet(disable_style)
        self.prioritas6_input.setStyleSheet(disable_style)


    def disable_except_start_button(self):
        self.update_saldo_button.setDisabled(True)
        self.update_watchlist_button.setDisabled(True)
        self.pressed_login_style()
        self.pressed_watchlist_style()

        self.password_input.setDisabled(False)

    def enable_all_button(self):
        self.update_saldo_button.setDisabled(False)
        self.update_watchlist_button.setDisabled(False)
        self.start_button.setDisabled(False)
        self.normal_login_style()
        self.normal_watchlist_style()
        self.timer_start_trading.setText("")
        if self.start_button.text() == "START BOT":
            self.start_button.setStyleSheet(self.start_syle)

        self.email_input.setDisabled(False)
        self.password_input.setDisabled(False)
        self.pin_input.setDisabled(False)

        self.jam_trading_input.setDisabled(False)
        self.saldo_trading_input.setDisabled(False)
        self.persentase_saham_input.setDisabled(False)
        self.jumlah_saham_input.setDisabled(False)
        self.range_value_input.setDisabled(False)
        self.range_harga_input.setDisabled(False)

        self.prioritas1_input.setDisabled(False)
        self.prioritas2_input.setDisabled(False)
        self.prioritas3_input.setDisabled(False)
        self.prioritas4_input.setDisabled(False)
        self.prioritas5_input.setDisabled(False)
        self.prioritas6_input.setDisabled(False)

        enable_style = "border-radius: 10px;color: rgb(255, 255, 255);padding: 8px;background-color: rgb(142, 172, 205);"

        self.email_input.setStyleSheet(enable_style)
        self.password_input.setStyleSheet(enable_style)
        self.pin_input.setStyleSheet(enable_style)

        self.jam_trading_input.setStyleSheet(enable_style)
        self.saldo_trading_input.setStyleSheet(enable_style)
        self.persentase_saham_input.setStyleSheet(enable_style)
        self.jumlah_saham_input.setStyleSheet(enable_style)
        self.range_value_input.setStyleSheet(enable_style)
        self.range_harga_input.setStyleSheet(enable_style)

        self.prioritas1_input.setStyleSheet(enable_style)
        self.prioritas2_input.setStyleSheet(enable_style)
        self.prioritas3_input.setStyleSheet(enable_style)
        self.prioritas4_input.setStyleSheet(enable_style)
        self.prioritas5_input.setStyleSheet(enable_style)
        self.prioritas6_input.setStyleSheet(enable_style)

    def change_visibility_password(self):
        # Show Password
        if self.hide_password_button.icon().cacheKey() == self.hide_or_show_icon.cacheKey():
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.hide_password_button.setIcon(self.show_password_icon)
        # Hide Password
        elif self.hide_password_button.icon().cacheKey() == self.show_password_icon.cacheKey():
            self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
            self.hide_password_button.setIcon(self.hide_or_show_icon)

    def change_visibility_pin(self):
        # Show Password
        if self.hide_pin_button.icon().cacheKey() == self.hide_or_show_icon.cacheKey():
            self.pin_input.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.hide_pin_button.setIcon(self.show_password_icon)
        # Hide Password
        elif self.hide_pin_button.icon().cacheKey() == self.show_password_icon.cacheKey():
            self.pin_input.setEchoMode(QtWidgets.QLineEdit.Password)
            self.hide_pin_button.setIcon(self.hide_or_show_icon)

    def pressed_login_style(self):
        self.update_saldo_button.setStyleSheet(self.__button_pressed_style)

    def normal_login_style(self):
        self.update_saldo_button.setStyleSheet(self.__button_released_style)

    def pressed_watchlist_style(self):
        self.update_config_file()
        self.update_watchlist_button.setStyleSheet(self.__button_pressed_style)

    def normal_watchlist_style(self):
        self.update_config_file()
        self.update_watchlist_button.setStyleSheet(self.__button_released_style)

    def pressed_start_style(self):
        self.start_button.setStyleSheet(self.__button_pressed_style)

    def normal_start_style(self):
        # self.start_button.setStyleSheet(self.start_syle)

        if self.start_button.text() == "START BOT":
            self.start_button.setText("CANCLE BOT")
            self.start_button.setStyleSheet("background-color: red;\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "border-radius: 10px;\n"
                                        "padding: 10px;")
        else:
            self.start_button.setText("START BOT")
            self.start_button.setStyleSheet(self.start_syle)


def start():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    STOCKBITBOT = QtWidgets.QMainWindow()
    ui = UiStockbitBot()
    ui.setup_ui(STOCKBITBOT)
    STOCKBITBOT.show()
    sys.exit(app.exec_())
