import os
import cv2
import time
import sys

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog

import darknet
from helmet import Ui_MainWindow

configPath = "helmet.cfg"
weightPath = "./backup/helmet_5000.weights"
metaPath = "helmet.data"



netMain = None
metaMain = None
altNames = None

video_img = cv2.imread("000.jpg")

video_name = cv2.imread('000.jpg')
picture_img = cv2.imread('000.jpg')
picture_name = cv2.imread('000.jpg')
ori_name = cv2.imread('000.jpg')

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxes(detections, img):
    for detection in detections:
        x, y, w, h = detection[2][0], \
                     detection[2][1], \
                     detection[2][2], \
                     detection[2][3]
        x_min, y_min, x_max, y_max = convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (x_min, y_min)
        pt2 = (x_max, y_max)
        if str(detection[0].decode()) == "person":
            cv2.rectangle(img, pt1, pt2, (255, 0, 0), 1)
            cv2.putText(img,
                        "warn",
                        #+":" + str(round(detection[1] * 100, 1)),
                        (pt1[0], pt2[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3,  (255, 0, 0), 1)

        if str(detection[0].decode()) == "hat":
            cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
            cv2.putText(img,
                        detection[0].decode(),
                        #+":" + str(round(detection[1] * 100, 1))

                        (pt1[0], pt2[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)

    return img


def YOLO():
    global metaMain, netMain, altNames
    global configPath, weightPath, metaPath
    global video_name, video_img, video_flag

    if not os.path.exists(configPath):
        raise ValueError("Invalid config path `" +
                         os.path.abspath(configPath) + "`")
    if not os.path.exists(weightPath):
        raise ValueError("Invalid weight path `" +
                         os.path.abspath(weightPath) + "`")
    if not os.path.exists(metaPath):
        raise ValueError("Invalid data file path `" +
                         os.path.abspath(metaPath) + "`")
    if netMain is None:
        netMain = darknet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
    if metaMain is None:
        metaMain = darknet.load_meta(metaPath.encode("ascii"))
    if altNames is None:
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", metaContents,
                                  re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass
    accum_time = 0
    curr_fps = 0
    fps = "FPS: ??"
    prev_time = time.time()
    # Create an image we reuse for each detect
    darknet_image = darknet.make_image(darknet.network_width(netMain),
                                       darknet.network_height(netMain), 3)
    while video_flag:
        frame_rgb = cv2.cvtColor(video_name, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb,
                                   (darknet.network_width(netMain),
                                    darknet.network_height(netMain)),
                                   interpolation=cv2.INTER_LINEAR)
        darknet.copy_image_from_bytes(darknet_image, frame_resized.tobytes())

        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.7)
        video_img = cvDrawBoxes(detections, frame_resized)
        # video_img = cv2.cvtColor(video_img, cv2.COLOR_RGB2BGR)
        curr_time = time.time()
        exec_time = curr_time - prev_time
        prev_time = curr_time
        accum_time = accum_time + exec_time
        curr_fps = curr_fps + 1
        if accum_time > 1:
            accum_time = accum_time - 1
            fps = "FPS: " + str(curr_fps)
            curr_fps = 0
        cv2.putText(video_img, text=fps, org=(3, 15), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.50, color=(255, 0, 0), thickness=2)



class dpv_thread(QThread):  # 检测的线程
    img_breakSignal = pyqtSignal(int)
    video_breakSignal = pyqtSignal(int)
    def __init__(self, parent=None):
        super(dpv_thread, self).__init__()

    def run(self):
        global picture_flag, video_flag, picture_img, picture_name, ori_name
        if picture_flag:
            picture_img = darknet.performDetect(picture_name)
            self.img_breakSignal.emit(picture_img)
        else:
            YOLO()
            self.video_breakSignal.emit(ori_name)


class rpv_thread(QThread):  # 读取图片或视频的线程
    def __init__(self, parent=None):
        super(rpv_thread, self).__init__()

    def run(self):
        global video_flag, video_name
        cap = cv2.VideoCapture(video_name)
        cap.set(3, 1280)
        cap.set(4, 720)
        while video_flag:
            video_flag, video_name = cap.read()  # 读入数据帧
            time.sleep(0.05)  # 如果是视频，加上这一句让读取速度为每30ms一帧，


class HelmetWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(HelmetWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("安全帽检测")  # 设置窗口程序标题
        self.Read.clicked.connect(self.read)
        self.StartDetect.clicked.connect(self.start_detect)
        self.DetectPicture.clicked.connect(self.detect_picture)
        self.DetectVideo.clicked.connect(self.detect_video)
        self.show_label.setScaledContents(True)

        self.RPV_thread = rpv_thread()  # 实例化读取图片或视频
        self.DPV_thread = dpv_thread()  # 实例化检测
        self.timer_detect = QtCore.QTimer()  # 定义定时器，用于控制显示检测输出视频流的帧率
        self.timer_detect.timeout.connect(self.show_detect)  # 若定时器结束，则调用show_detect()
        self.DPV_thread.img_breakSignal.connect(self.show_detect)
        self.DPV_thread.video_breakSignal.connect(self.ori)

    def read(self):
        global picture_flag, picture_name, video_flag, video_name
        if picture_flag:
            picture_name, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
            print(picture_name)
            if picture_name == '':
                return '图片打开失败'
        else:
            video_name, videoType = QFileDialog.getOpenFileName(self, '打开视频', '', '*.mp4')
            print(video_name)
            self.RPV_thread.start()  # 开始读取图片或视频线程


    def detect_picture(self):
        global picture_flag, video_flag, ori_name
        showImage = QtGui.QImage(ori_name.data, ori_name.shape[1], ori_name.shape[0],
                                 QtGui.QImage.Format_RGB888)
        self.show_label.setPixmap(QtGui.QPixmap.fromImage(showImage))
        picture_flag = True
        video_flag = False

    def detect_video(self):
        global video_flag, picture_flag
        video_flag = True
        picture_flag = False


    def ori(self):
        global ori_name
        showImage = QtGui.QImage(ori_name.data, ori_name.shape[1], ori_name.shape[0],
                                 QtGui.QImage.Format_RGB888)
        self.show_label.setPixmap(QtGui.QPixmap.fromImage(showImage))

    def start_detect(self):
        global picture_flag, video_flag
        if picture_flag:
            self.DPV_thread.start()
        if video_flag:
            self.DPV_thread.start()
            self.timer_detect.start(50)  # 定时器开始计时30ms，结果是每过30ms从摄像头中取一帧显示

    def show_detect(self):
        global picture_img, picture_flag
        global video_flag, video_img
        if picture_flag:
            showImage = QtGui.QImage(picture_img.data, picture_img.shape[1], picture_img.shape[0],
                                     QtGui.QImage.Format_RGB888)
            self.show_label.setPixmap(QtGui.QPixmap.fromImage(showImage))
        if video_flag:
            showImage = QtGui.QImage(video_img.data, video_img.shape[1], video_img.shape[0],
                                     QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            self.show_label.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage
    def closeEvent(self, event):  # 关闭窗口响应函数，在这里面弹出确认框，并销毁线程
        self.timer_detect.stop()
        reply = self.QtWidgets.QMessageBox.question(self,
                                                    '本程序',
                                                    "是否要退出程序？",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                    QtWidgets.QMessageBox.No)
        if reply == self.QtWidgets.QMessageBox.Yes:
            event.accept()
            os.exit(0)
        else:
            event.ignore()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = HelmetWindow()
    ui.show()
    sys.exit(app.exec_())
