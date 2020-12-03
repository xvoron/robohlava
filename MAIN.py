"""
ROBOHLAVA
version: 2.1

Author: Artyom Voronin
"""

greeting = open("txt_file/robohlava.txt", "r")
print(greeting.read())

print("-------------------Import start-------------------\n")

import os
# General packages import
import sys
import time

import cv2
from PyQt5.QtCore import (QThread, Qt, pyqtSignal, pyqtSlot, QSize,
                          QObject)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QFont
# PyQt import
from PyQt5.QtWidgets import (QWidget, QLabel, QApplication,
                             QDesktopWidget, QVBoxLayout, QAbstractButton,
                             QHBoxLayout, QButtonGroup)

import robohlava.config as config
import robohlava.core as core

print("-------------------Import Done-------------------\n")

PATH = os.getcwd()


class RobohlavaBackend(QObject):
    """Robohlava Core Back-end script"""
    change_pixmap = pyqtSignal(QImage, QImage, QImage, str)
    state_information = pyqtSignal(str)
    information = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.core = core.RobohlavaCore()
        self.current_state = None
        self.current_text = None
        self.btns_state = None
        self.flags = (False, False, False, False, False)

    def run(self):
        #TODO mini_images from state.run
        print("[TEST] Thread is working")
        while True:
            data_core = self.core.run(self.flags) #TODO
            rgb, depth, mini = data_core['rgb'], data_core['depth'], data_core['mini']
            state, text, num_persons = data_core['state'], data_core['text'], data_core['num_persons']

            rgb_img = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_img.shape
            bytes_per_line = ch * w
            convert_2Qt_format_rgb = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p_rgb = convert_2Qt_format_rgb.scaled(1280, 960, Qt.KeepAspectRatio)

            depth_img = cv2.cvtColor(depth, cv2.COLOR_BGR2RGB)
            h, w, ch = depth_img.shape
            bytes_per_line = ch * w
            convert_2Qt_format_depth = QImage(depth_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p_depth = convert_2Qt_format_depth.scaled(1280, 960, Qt.KeepAspectRatio)

            mini_img = cv2.cvtColor(mini, cv2.COLOR_BGR2RGB)
            h, w, ch = mini_img.shape
            bytes_per_line = ch * w
            convert_2Qt_format_mini = QImage(mini_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p_mini = convert_2Qt_format_mini.scaled(1280, 960, Qt.KeepAspectRatio)

            if text is not None and text != '[]':
                if self.current_text != text:
                    self.current_text = text
                    print("Current text: ", self.current_text)

            self.change_pixmap.emit(p_rgb, p_depth, p_mini,
                    str(self.current_text))
            if state is not None and self.current_state != state:
                self.current_state = state
                if self.current_state == 'games':
                    self.flags = (False, False, False, False, False)
                self.state_information.emit(str(self.current_state))
            self.information.emit([num_persons, self.current_state])

    def terminate_close(self):
        self.core.terminate()


class MainWindow(QWidget):
    """Main window displaying RGB, Depth and details frames"""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.actual_state = None

    @pyqtSlot(list)
    def set_information(self, infos):
        self.label_more_info.setText(
                "Number of Persons:{} \n Actual state: {}".format(infos[0],
                    infos[1]))

    @pyqtSlot(QImage, QImage, QImage, str)
    def setImage(self, img_rgb, img_depth, img_mini, text_info):
        self.label_rgb.setPixmap(QPixmap.fromImage(img_rgb))
        self.label_depth.setPixmap(QPixmap.fromImage(img_depth.scaled(640, 480,
            Qt.KeepAspectRatio)))
        self.label_mini.setPixmap(QPixmap.fromImage(img_mini.scaled(640, 480, Qt.KeepAspectRatio)))
        self.info_label.setText(text_info)

    @pyqtSlot(str)
    def process_state_from_robohlava(self, state):
        list_of_possible_states =['Games', "Book", "Yolo", "Professor", "Noname"]
        self.actual_state = state
        print("[INFO] Main window state robohlava:", state)
        if state == 'Games':
            self.touch_screen.blockSignals(False)
            print("[INFO] RESET BUTTONS")
            self.touch_screen.btns_reset()
            self.robohlava.flags = (False, False, False, False, False)
        elif state in list_of_possible_states:
            #self.touch_screen.blockSignals(True)
            pass
        else:
            self.touch_screen.btns_disable()

    @pyqtSlot(str)
    def process_state_from_touchscreen(self, state):
        """state

        flags:
            (book, professor, yolo, noname, cancel)
        """
        print("[INFO] Main window state touchscreen:", state)
        list_of_possible_states =['Games', "Book", "Yolo", "Professor", "Noname"]
        print(f"self.actual_state {self.actual_state}")
        if state and (self.actual_state in list_of_possible_states):
            if int(state) == 0:
                print("cancel")
                self.robohlava.flags = (False, False, False, False, True)
                self.touch_screen.btns_reset()
            elif int(state) == 1:
                self.robohlava.flags = (True, False, False, False, False)
            elif int(state) == 2:
                self.robohlava.flags = (False, True, False, False, False)
            elif int(state) == 3:
                self.robohlava.flags = (False, False, True, False, False)
            elif int(state) == 4:
                self.robohlava.flags = (False, False, False, True, False)
            else:
                self.robohlava.flags = (False, False, False, False, False)
        else:
            self.robohlava.flags = (False, False, False, False, False)

    @pyqtSlot(QImage)
    def process_persons_objects_imgs(self):
        pass

    def initUI(self):

        self.setWindowTitle("Main window")
        self.resize(1920, 1080)

        # Background color
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)

        self.label_rgb = QLabel(self)
        self.label_rgb.move(0, 0)
        self.label_rgb.resize(1280, 960)

        self.label_depth = QLabel(self)
        self.label_depth.move(1280, 0)
        self.label_depth.resize(640, 480)

        self.label_mini = QLabel(self)
        self.label_mini.move(1280, 480)
        self.label_mini.resize(640, 480)

        self.info_label = QLabel(self)
        self.info_label.setText("Information")
        self.info_label.move(0, 930)
        self.info_label.resize(1920, 120)
        self.info_label.setFont(QFont("Times", 25, QFont.Bold))
        self.info_label.setStyleSheet("color:#459b24")
        self.info_label.setWordWrap(True)

        self.label_text_rgb = QLabel(self)
        self.label_text_rgb.move(20, 20)
        self.label_text_rgb.setText("RGB image")
        self.label_text_rgb.setFont(QFont("Times", 30, QFont.Bold))
        self.label_text_rgb.setStyleSheet("color:#459b24")

        self.label_text_depth = QLabel(self)
        self.label_text_depth.move(1290, 20)
        self.label_text_depth.setText("Depth image")
        self.label_text_depth.setFont(QFont("Times", 30, QFont.Bold))
        self.label_text_depth.setStyleSheet("color:#459b24")

        self.label_more_info = QLabel(self)
        self.label_more_info.move(700, 20)
        self.label_more_info.resize(450, 100)
        self.label_more_info.setText("Number of Persons: \n Actual state: ")
        self.label_more_info.setFont(QFont("Times", 30, QFont.Bold))
        self.label_more_info.setStyleSheet("color:#459b24")

        self.touch_screen = TouchScreen()
        self.touch_screen.state_from_btn.connect(self.process_state_from_touchscreen)
        self.touch_screen.terminate_signal.connect(self.terminate_close_all)

        self.robohlava = RobohlavaBackend()
        self.robohlava.change_pixmap.connect(self.setImage)
        self.robohlava.state_information.connect(self.process_state_from_robohlava)
        self.robohlava.information.connect(self.set_information)

        self.th = QThread()
        self.robohlava.moveToThread(self.th)
        self.th.started.connect(self.robohlava.run)
        self.th.start()
        self.showFullScreen() # Full screen only when everything is done
        self.show()

    @pyqtSlot(bool)
    def terminate_close_all(self, flag):
        if flag == True:
            print("[TERM] Terminating and close application")
            self.robohlava.terminate_close()
            self.touch_screen.close()
            time.sleep(1)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            print("[TERM] Terminating and close application")
            self.robohlava.terminate_close()
            self.touch_screen.close()
            time.sleep(1)
            self.close()




class ImageButton(QAbstractButton):
    """Custom Bitmap Button"""
    def __init__(self, pixmap, pixmap_toggled, ID, info_text="info", parent=None):
        super(ImageButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_toggled = pixmap_toggled
        self.ID_state = ID

        self.pressed.connect(self.update)
        self.released.connect(self.update)
        self.setCheckable(True)
        self.info_text = info_text

    def paintEvent(self, event):
        if self.isChecked():
            pix = self.pixmap_toggled
        elif not self.isChecked():
            pix = self.pixmap
        else:
            pix = self.pixmap

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def sizeHint(self):
        return QSize(284, 470)


class TouchScreen(QWidget):
    """Touch screen window with buttons"""
    state_from_btn = pyqtSignal(str)
    terminate_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.checked_btn_id = None
        self.info_label_default_text = config.info_label_default_text
        self.btn1_text = config.btn1_text
        self.btn2_text = config.btn2_text
        self.btn3_text = config.btn3_text
        self.btn4_text = config.btn4_text
        self.button_ui()

    def button_ui(self):
        self.setWindowTitle("TouchScreen")

        # Background color
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)

        # Monitor arrangement
        display_monitor = 2
        monitor = QDesktopWidget().screenGeometry(display_monitor)

        self.ui_layout_h = QHBoxLayout()
        self.ui_layout_v = QVBoxLayout()

        self.btn1 = ImageButton(QPixmap("btns/btn1.png"),
                                QPixmap("btns/btn1_pressed.png"), 1, self.btn1_text)
        self.btn2 = ImageButton(QPixmap("btns/btn2.png"),
                                QPixmap("btns/btn2_pressed.png"), 2, self.btn2_text)
        self.btn3 = ImageButton(QPixmap("btns/btn3.png"),
                                QPixmap("btns/btn3_pressed.png"), 3, self.btn3_text)
        self.btn4 = ImageButton(QPixmap("btns/btn4.png"),
                                QPixmap("btns/btn4_pressed.png"), 4, self.btn4_text)

        self.group = QButtonGroup(self)
        self.group.addButton(self.btn1)
        self.group.addButton(self.btn2)
        self.group.addButton(self.btn3)
        self.group.addButton(self.btn4)
        self.group.setExclusive(True)

        self.info_label = QLabel(self.info_label_default_text)
        self.info_label.setFont(QFont("Times", 30, QFont.Bold))
        self.info_label.setStyleSheet("color:#459b24")

        self.group.buttonClicked.connect(self.buttons_clicked_processing)
        #self.btns_reset()

        self.ui_layout_h.addWidget(self.btn1)
        self.ui_layout_h.addWidget(self.btn2)
        self.ui_layout_h.addWidget(self.btn3)
        self.ui_layout_h.addWidget(self.btn4)

        self.ui_layout_v.addLayout(self.ui_layout_h)
        self.ui_layout_v.addWidget(self.info_label)

        self.setLayout(self.ui_layout_v)
        #self.resize(1920, 1080)
        self.move(0, 1100)
        self.showFullScreen() # Full screen only when everything is done
        self.show()


    def btns_reset(self):
        self.btns_enable()
        self.group.setExclusive(False)
        for btn in self.group.buttons():
            if btn.isChecked():
                btn.setChecked(False)
        self.group.setExclusive(True)
        self.label_text_change(config.info_label_game_text)

    def btns_disable(self):
        for btn in self.group.buttons():
            btn.setDisabled(True)
        self.label_text_change(config.info_label_default_text)

    def btns_enable(self):
        for btn in self.group.buttons():
            btn.setEnabled(True)
        self.label_text_change(config.info_label_game_text)

    def btns_active_1(self):
        for btn in self.group.buttons():
            if btn.isChecked():
                pass
            else:
                btn.setDisabled(True)

    def label_text_change(self, text=None):
        if text is not None:
            self.info_label.setText(text)
        else:
            self.info_label.setText(self.info_label_default_text)

    def buttons_clicked_processing(self, btn=None):
        if btn is not None:
            self.label_text_change(btn.info_text)
            if btn.ID_state == self.checked_btn_id:
                self.btns_reset()
                self.checked_btn_id = None
                print("[INFO] Cancel ", btn.ID_state, " state")
                self.state_from_btn.emit(str(0))
            else:
                self.checked_btn_id = btn.ID_state
                print("state_from_btn.emit: " + str(btn.ID_state))
                self.state_from_btn.emit(str(btn.ID_state))
                self.btns_active_1()
        else:
            self.label_text_change()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            print("[TERM] Terminating and close application from TouchScreen window")
            self.terminate_signal.emit(True)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
