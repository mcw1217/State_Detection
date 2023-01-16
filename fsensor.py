from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap


from PyQt5 import QtWidgets, uic

import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np

from time import sleep

from threading import Condition

import json
import urllib.request as wclient


# ------------------------------------------------#
#
#  Web Client thread
#
# ------------------------------------------------#
gURL = "http://192.168.20.102"

gSaveWorkingWeb = False
gSaveParaWeb = []
gControlMode = 0  # 0:local, 1:remote


class WebClientThread(QThread):
    signal_save_face = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def checkServer(self):
        global gSaveParaWeb, gSaveWorkingWeb, gControlMode
        global gURL

        if gControlMode != 1:
            # print('not remote mode ')
            return

        if gSaveWorkingWeb:
            return

        try:
            # url='http://localhost:7777/get_ask/[1]'
            url = gURL + "/get_ask/[1]"
            url = url.replace(" ", "%20")

            conn = wclient.urlopen(url)
            # print(type(conn),conn)
            data = conn.read()

            print("========>")
            print(type(data), conn.status, data)

            data = json.loads(data)

            if data["id"] == -1:
                print("no data id -1 .......")
                return

            gSaveParaWeb = data
            gSaveWorkingWeb = True  # start saving

            print("* siganl send: signal_save_face..")
            self.signal_save_face.emit(data)

        except wclient.HTTPError as e:
            print("web error <<<<<<<<<<<<<<<<<<")
            print(e)
        except:
            print("url connect error ...........")

    def updateCount(self):
        global gSaveParaWeb, gSaveWorkingWeb
        global gURL

        if not gSaveWorkingWeb:
            return

        try:
            sdata = {}
            sdata["id"] = gSaveParaWeb["id"]
            sdata["count"] = 5
            print("sdata:", sdata)

            para = json.dumps(sdata)

            # url='http://localhost:7777/update_count/'+ para
            url = gURL + "/update_count/" + para
            url = url.replace(" ", "%20")

            print("debug : send upate  url > ", url)

            conn = wclient.urlopen(url)
            # print(type(conn),conn)
            para = conn.read()

            print("========>")
            print(type(para), conn.status, para)

            data = json.loads(para)
            print("debug: ok update count from db msg>>")
            print(data)

            if data["re"] == 1:
                return True
            else:
                return False

        except wclient.HTTPError as e:
            print("web error <<<<<<<<<<<<<<<<<<")
            print(e)
            return False
        except:
            print("url conne")
            return False

    @pyqtSlot()
    def signal_save_end(self):
        print("@ R: signal_save_end")
        # 저장이 끝났음을 알리는 시그널 : db에 작업완료 update 필요
        global gSaveWorkingWeb

        while not self.updateCount():
            print("<signal_save_end>=> error not update db count ")
            sleep(2)

        gSaveWorkingWeb = False
        print("debug: ok siganl_save end received......")

    def run(self):
        while True:
            self.checkServer()
            sleep(5)

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


# ------------------------------------------------#
#
#  Thermal thread
#
# ------------------------------------------------#
gThermalFrame = None
gTempFrame = None


from seekcamera import (
    SeekCameraIOType,
    SeekCameraColorPalette,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
    SeekCamera,
    SeekFrame,
    SeekCameraShutterMode,
    SeekCameraAGCMode,
    SeekCameraTemperatureUnit,
)


class Renderer:
    def __init__(self):
        self.busy = False
        self.frame = SeekFrame()
        self.camera = SeekCamera()
        self.frame_condition = Condition()
        self.first_frame = True


def on_frame(_camera, camera_frame, renderer):
    with renderer.frame_condition:
        renderer.frame1 = camera_frame.thermography_float
        renderer.frame = camera_frame.color_argb8888
        renderer.frame_condition.notify()


def on_event(camera, event_type, event_status, renderer):
    print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        if renderer.busy:
            return
        renderer.busy = True
        renderer.camera = camera
        renderer.first_frame = True
        camera.color_palette = SeekCameraColorPalette.TYRIAN
        camera.shutter_mode = SeekCameraShutterMode.MANUAL
        camera.agMode = SeekCameraAGCMode.LINEAR
        camera.tempunit = SeekCameraTemperatureUnit.CELSIUS
        camera.register_frame_available_callback(on_frame, renderer)
        camera.capture_session_start(
            SeekCameraFrameFormat.THERMOGRAPHY_FLOAT
            | SeekCameraFrameFormat.COLOR_ARGB8888
        )
        # camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        if renderer.camera == camera:
            # Stop imaging and reset all the renderer state.
            camera.capture_session_stop()
            renderer.camera = None
            renderer.frame = None
            renderer.busy = False
    elif event_type == SeekCameraManagerEvent.ERROR:
        print("{}: {}".format(str(event_status), camera.chipid))
    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        return


def thermal():
    global gThermalFrame, gTempFrame

    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)

        while True:
            with renderer.frame_condition:
                if renderer.frame_condition.wait(150.0 / 1000.0):  # (150.0 / 1000.0)
                    img = renderer.frame.data
                    temp = renderer.frame1.data

                    if renderer.first_frame:
                        (height, width, _) = img.shape
                        # cv2.resizeWindow(window_name, width * 2, height * 2)
                        renderer.first_frame = False

                    gThermalFrame = img  # 이미지
                    gTempFrame = temp  # 온도


class ThermalThread(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        pass
        thermal()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


# ------------------------------------------------#
#
#  videio thread
#
# ------------------------------------------------#
class VideoThread(QThread):
    change_pixmap_signal1 = pyqtSignal(np.ndarray)
    change_pixmap_signal2 = pyqtSignal(np.ndarray)
    signal_save_end = pyqtSignal()

    def __init__(self):
        self.rect_count = 0
        super().__init__()
        self._run_flag = True
        self.faceCascade = cv2.CascadeClassifier(
            "haarcascades/haarcascade_frontalface_default.xml"
        )

    def drawRect(self, frame):
        global gFilePath, gIsSave, gThermalFrame, gTempFrame
        global gSaveParaWeb, gSaveWorkingWeb

        # draw rectangle
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 흑백으로
        faces = self.faceCascade.detectMultiScale(
            gray,  # 검출하고자 하는 원본이미지
            scaleFactor=1.2,  # 검색 윈도우 확대 비율, 1보다 커야 한다
            minNeighbors=6,  # 얼굴 사이 최소 간격(픽셀)
            minSize=(20, 20),  # 얼굴 최소 크기. 이것보다 작으면 무시
        )

        # 얼굴에 대해 rectangle 출력

        for (x, y, w, h) in faces:

            if self.rect_count > 0:
                img = frame.copy()
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

            # inputOutputArray, point1 , 2, colorBGR, thickness)
            if self.rect_count > 0:

                face_id = self.save_path
                count = self.rect_count
                f_path = face_id + "_" + str(count) + ".jpg"

                print("@ save org:", f_path)
                # cv2.imwrite(f_path,frame[y:y+h, x:x+w])
                cv2.imwrite(f_path, img)

                # sleep(0.01)

                f_path = f_path + ".png"
                print("@ save thermal:", f_path)
                # x = x + 20 # 28
                # y = y + 18 # 23
                # cv2.imwrite(f_path+'.png',gThermalFrame.data[y:y+h,x:x+w])
                writeStatus = cv2.imwrite(f_path, gThermalFrame)
                print("->", writeStatus)

                print("@ save temper:", f_path)
                np.save(f_path, gTempFrame)

                self.rect_count -= 1

                if gSaveWorkingWeb and self.rect_count <= 0:
                    # update db count
                    print("* siganl send: signal_save_end..")
                    self.signal_save_end.emit()

        return frame

    def run(self):
        global gThermalFrame

        # capture from web cam
        cap = cv2.VideoCapture(self.camera_id + cv2.CAP_DSHOW)
        # 동영상 크기 변환
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320) # 가로
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240) # 세로

        while self._run_flag:
            ret, cv_img = cap.read()

            if ret:
                cv_img = cv2.resize(cv_img, (320, 240))
                # print("@@:",cv_img.shape)
                # cv_img = self.calibration(cv_img)
                cv_img = self.drawRect(cv_img)

                # print('* signal send:change_pixmap_signal1')
                self.change_pixmap_signal1.emit(cv_img)

                # print('* signal send:change_pixmap_signal2')
                # self.change_pixmap_signal2.emit(gThermalFrame)
            sleep(0.1)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


# ------------------------------------------------#
#
#  main thread
#
# ------------------------------------------------#
import json
import os
from datetime import datetime


class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        # self.setWindowTitle("Qt live label demo")
        # self.disply_width = 320
        # self.display_height = 240

        uic.loadUi("fsensor.ui", self)
        self.MyIni()
        # --------------------------------
        # self.MyIni()
        # event handler
        self.pushButton_run.released.connect(
            lambda: self.pushButton_Run(self.pushButton_run)
        )

        # self.comboBox_id.currentIndexChanged.connect(self.comboBoxID)
        # self.comboBox_state.currentIndexChanged.connect(self.comboBoxState)
        self.runThread()

    def updateNameState_Remote(self):
        self.comboBox_id.clear()
        # self.comboBox_state.clear()

    def updateNameState_Local(self):
        f = open("id.json", "r", encoding="utf-8")
        self.id = json.load(f)

        self.comboBox_id.clear()
        for k, v in self.id.items():
            self.comboBox_id.addItem(k)

        # 상태
        f = open("state.json", "r", encoding="utf-8")
        self.state = json.load(f)

        self.comboBox_state.clear()
        for k, v in self.state.items():
            self.comboBox_state.addItem(k)

        f = open("config.json", "r", encoding="utf-8")
        self.config = json.load(f)

    def MyIni(self):

        self.updateNameState_Local()

        self.save_count = 0

        self.radioButton_local.clicked.connect(self.modeChange)
        self.radioButton_remote.clicked.connect(self.modeChange)

    def runThread(self):

        # networkclient thread
        self.thread_web = WebClientThread()
        self.thread_web.signal_save_face.connect(self.signal_save_face)
        # self.thread_web.start()

        # -------------------thermal
        # self.thread_thermal = ThermalThread()  ===> 나중에 복구
        # self.thread_thermal.start()

        # sleep(7)
        # print('start video thread >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

        # -------------------videio
        self.thread = VideoThread()
        self.thread.camera_id = self.config["camera_id"]

        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal1.connect(self.update_image1)
        # self.thread.change_pixmap_signal2.connect(self.update_image2) 나중에 복구
        self.thread.signal_save_end.connect(self.thread_web.signal_save_end)

        # start the thread

        # self.thread_thermal.start()  # 열화상  나중에 복구
        sleep(7)

        self.thread.start()  # video
        sleep(3)

        self.thread_web.start()  # Web

        print("ok all thread started ......................................")

    def modeChange(self):
        global gControlMode

        if self.radioButton_local.isChecked():
            gControlMode = 0
            self.updateNameState_Local()
            self.pushButton_run.setEnabled(True)
        elif self.radioButton_remote.isChecked():
            gControlMode = 1
            self.updateNameState_Remote()
            self.pushButton_run.setEnabled(False)

        print("contrl mode:", gControlMode)

    def make_folder(self, s_path):
        isExist = os.path.exists(s_path)
        if not isExist:
            os.makedirs(s_path)
            return True

        return False

    def saveImage(self, id, state, control_mode="L"):
        print("debug:<saveImage>..... ")
        print(id, state)

        # return  False

        f = open("config.json", "r", encoding="utf-8")
        config_data = json.load(f)

        self.save_path = config_data["save_path"]
        self.save_count = config_data["save_count"]

        self.make_folder(self.save_path)
        #
        d = datetime.now()
        msg = d.strftime("%Y%m%d%H%M%S")

        # id=self.id[id]
        # state = self.state[state]

        prefix = "{}/{}_{}_{}_{}".format(self.save_path, control_mode, id, msg, state)
        # print(prefix)

        self.thread.save_path = prefix
        self.thread.rect_count = self.save_count

    def pushButton_Run(self, button):
        print("save image.... ")
        # self.demo1()
        id = self.comboBox_id.currentText()

        state = self.comboBox_state.currentText()
        state = self.state[state]

        self.saveImage(id, state, "L")

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    @pyqtSlot(dict)
    def signal_save_face(self, data):
        global gSaveWorkingWeb

        print("@ R: signal_save_face")
        print("para:", data)

        self.comboBox_id.clear()
        self.comboBox_id.addItem(data["name"])

        # state_dic=['매우좋음','좋음','보통','나쁨','매우나쁨']
        self.comboBox_state.setCurrentIndex(data["state"] - 1)

        id = self.comboBox_id.currentText()
        state = self.comboBox_state.currentText()
        state = self.state[state]
        print("remote:", id, state)

        self.saveImage(id, state, "R")

    def updateProgressBar(self):
        save_count = self.save_count

        if save_count <= 0:
            self.progressBar1.setValue(0)
            return

        rect_count = self.thread.rect_count
        # if rect_count  <= 0:
        #     self.progressBar1.setValue(0)
        #     return

        w_count = save_count - rect_count
        if save_count > 0:
            w_rate = int((w_count / save_count) * 100)
        else:
            w_rate = 0

        self.progressBar1.setValue(w_rate)

    @pyqtSlot(np.ndarray)
    def update_image1(self, cv_img):

        # print('@ R: update_image1')
        # print('para:',data)

        self.updateProgressBar()

        """Updates the image_label with a new opencv image"""
        # qt_img = self.convert_cv_qt(cv_img)
        # self.image_label.setPixmap(qt_img)
        img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
        qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.label1.setPixmap(pixmap)
        self.label1.resize(pixmap.width(), pixmap.height())
        self.label1.show()

    @pyqtSlot(np.ndarray)
    def update_image2(self, cv_img):

        # print('@ R: update_image2')
        """Updates the image_label with a new opencv image"""
        # qt_img = self.convert_cv_qt(cv_img)
        # self.image_label.setPixmap(qt_img)
        img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, c = img.shape
        qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.label2.setPixmap(pixmap)
        self.label2.resize(pixmap.width(), pixmap.height())
        self.label2.show()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = Ui_MainWindow()
    win.show()
    sys.exit(app.exec_())


main()
