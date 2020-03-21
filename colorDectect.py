import sys

import cv2
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QDialog


class ColorDetect(QDialog):
    def __init__(self):
        super(ColorDetect, self).__init__()
        loadUi('ui/colorDetect.ui', self)

        self.image = None
        self.startButton.clicked.connect(self.start_webcam)
        self.stopButton.clicked.connect(self.stop_webcam)

        self.trackButton.setCheckable(True)
        self.trackButton.toggled.connect(self.track_webcam_color)
        self.track_Enabled = False

        self.color1Button.clicked.connect(self.setColor1)
        self.color2Button.clicked.connect(self.setColor2)
        self.color3Button.clicked.connect(self.setColor3)

        # 先勾选了Check，而未setColor ,然后直接Track Color的时候，会出错
        # AttributeError: 'colorDetect' object has no attribute 'color1_lower'
        # 因为setColor里面初始化了color1_lower & color1_upper
        # 为了避免此问题，在__init__()函数里面初始化这些数值
        self.color1_lower = np.array([0, 0, 0], np.uint8)
        self.color1_upper = np.array([180, 255, 255], np.uint8) # opencv中HSV的最大取值

        self.color2_lower = np.array([0, 0, 0], np.uint8)
        self.color2_upper = np.array([180, 255, 255], np.uint8)

        self.color3_lower = np.array([0, 0, 0], np.uint8)
        self.color3_upper = np.array([180, 255, 255], np.uint8)

    def track_webcam_color(self, status):
            if status:
                self.track_Enabled = True
                self.trackButton.setText('Stop Tracking')
            else:
                self.track_Enabled = False
                self.trackButton.setText('Track Color')

    def setColor1(self):
        self.color1_lower = np.array([self.hminSlider.value(),
                                      self.sminSlider.value(),
                                      self.vminSlider.value()], np.uint8)
        self.color1_upper = np.array([self.hmaxSlider.value(),
                                      self.smaxSlider.value(),
                                      self.vmaxSlider.value()], np.uint8)

        self.color1Label.setText(f'Min : {self.color1_lower} Max: {self.color1_upper}')

    def setColor2(self):
        self.color2_lower = np.array([self.hminSlider.value(),
                                      self.sminSlider.value(),
                                      self.vminSlider.value()], np.uint8)
        self.color2_upper = np.array([self.hmaxSlider.value(),
                                      self.smaxSlider.value(),
                                      self.vmaxSlider.value()], np.uint8)

        self.color2Label.setText(f'Min : {self.color2_lower} Max: {self.color2_upper}')

    def setColor3(self):
        self.color3_lower = np.array([self.hminSlider.value(),
                                      self.sminSlider.value(),
                                      self.vminSlider.value()], np.uint8)
        self.color3_upper = np.array([self.hmaxSlider.value(),
                                      self.smaxSlider.value(),
                                      self.vmaxSlider.value()], np.uint8)

        self.color3Label.setText(f'Min : {self.color3_lower} Max: {self.color3_upper}')

    def start_webcam(self):
        self.capture = cv2.VideoCapture(0) # s少写一个0
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer = QTimer(self) # 少写一个self
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def stop_webcam(self):
        self.timer.stop()

    def update_frame(self):
        ret, frame = self.capture.read()
        self.image = cv2.flip(frame, 1)
        self.displayImage(self.image, 1)

        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        color_lower = np.array([self.hminSlider.value(),
                                self.sminSlider.value(),
                                self.vminSlider.value()], np.uint8)
        color_upper = np.array([self.hmaxSlider.value(),
                                self.smaxSlider.value(),
                                self.vmaxSlider.value()], np.uint8)
        color_mask = cv2.inRange(hsv, color_lower, color_upper)
        self.displayImage(color_mask, 2)

        if self.track_Enabled and \
                  (self.color1Check.isChecked() or
                   self.color2Check.isChecked() or
                   self.color3Check.isChecked()):
            trackedImage = self.track_multi_colored_objects(self.image.copy())
            self.displayImage(trackedImage, 1)
        else:
            self.displayImage(self.image, 1)

    @staticmethod
    def track_colored_object(img, color_lower, color_upper):
        """
        A pipeline which does a series of operations to the image passed to the fuction.

        :param img:
        :param color_lower: [H,S,V] values
        :param color_upper: [H,S,V] values
        :return: None
        """
        blur = cv2.blur(img, (3, 3))
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

        color_mask = cv2.inRange(hsv, color_lower, color_upper)

        erode = cv2.erode(color_mask, None, iterations=2)
        dilate = cv2.dilate(erode, None, iterations=10)

        kernelOpen = np.ones((5, 5))
        kernelClose = np.ones((20, 20))

        maskOpen = cv2.morphologyEx(dilate, cv2.MORPH_OPEN, kernelOpen)
        maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose)

        contours, hierachy = cv2.findContours(maskClose, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 5000:
                x, y, w, h = cv2.boundingRect(contour)
                img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(img, 'Objected Deteced', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    def track_multi_colored_objects(self, img):
        if self.color1Check.isChecked():
            self.track_colored_object(img, self.color1_lower, self.color1_upper)

        if self.color2Check.isChecked():
            self.track_colored_object(img, self.color2_lower, self.color2_upper)

        if self.color3Check.isChecked():
            self.track_colored_object(img, self.color3_lower, self.color3_upper)

        return img

    def displayImage(self, img, window=1):
        qformat = QImage.Format_Indexed8

        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)

        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)
        if window == 2:
            self.processedLabel.setPixmap(QPixmap.fromImage(outImage))
            self.processedLabel.setScaledContents(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ColorDetect()
    window.setWindowTitle('Detect Color Object')
    window.show()
    sys.exit(app.exec_())