import sys

import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QDialog


class surveilMotion(QDialog):

    def __init__(self):
        super(surveilMotion, self).__init__()
        loadUi('ui/surveil.ui', self)

        self.image = None
        self.startButton.clicked.connect(self.start_webcam)
        self.stopButton.clicked.connect(self.stop_webcam)

        self.motionButton.setCheckable(True)
        self.motionButton.toggled.connect(self.detect_webcam_motion)
        self.motion_Enabled = False

        self.setRImgButton.clicked.connect(self.set_motion_image)
        self.motionFrame = None

    def detect_webcam_motion(self, status):
        if status:
            self.motion_Enabled = True
            self.motionButton.setText('Stop Motion Dectecting')
        else:
            self.motion_Enabled = False
            self.motionButton.setText('Detect Motion')

    def set_motion_image(self):
        gray = cv2.cvtColor(self.image.copy(), cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        self.motionFrame = gray
        self.displayImage(self.motionFrame, 2)

    def start_webcam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def stop_webcam(self):
        self.timer.stop()

    def update_frame(self):
        ret, self.image = self.capture.read()
        # flipcode: 1-水平翻转，0-垂直翻转， -1-水平&垂直翻转
        self.image = cv2.flip(self.image, 1)

        if self.motion_Enabled:
            detected_motion = self.detect_motion(self.image.copy())
            self.displayImage(detected_motion, 1)
        else:
            self.displayImage(self.image, 1)

    def detect_motion(self, input_img):
        self.text = 'No Motion'
        gray = cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        frameDiff = cv2.absdiff(self.motionFrame, gray)
        thresh = cv2.threshold(frameDiff, 40, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=5)

        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        height, width, channels = input_img.shape
        min_x, min_y = width, height
        max_x = max_y = 0

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            min_x, max_x = min(x, min_x), max(x + w, max_x)
            min_y, max_y = min(y, min_y), max(y + h, max_y)

        if max_x - min_x > 80 and max_y - min_y > 80:
            cv2.rectangle(input_img, (min_x, min_y), (max_x, max_y), (0, 255, 0), 3)
            self.text = 'Motion Detected'

        cv2.putText(input_img, f'Motion Status: {self.text}', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return input_img

    # def displayImage(self, img, window=1):
    #     qformat = QImage.Format_Indexed8
    #
    #     if len(img) == 3: # len(img.shape)
    #         if img.shape[2] == 4:
    #             qformat = QImage.Format_RGBA8888
    #         else:
    #             qformat = QImage.Format_RGB888
    #     outImg = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
    #
    #     outImg = outImg.rgbSwapped()
    #
    #     if window == 1:
    #         self.imgLabel.setPixmap(QPixmap.fromImage(outImg))
    #         self.imgLabel.setScaledContents(True)
    #     if window == 2:
    #         self.motionLabel.setPixmap(QPixmap.fromImage(outImg))
    #         self.motionLabel.setScaledContents(True)
    def displayImage(self, img, window=1):
        qformat = QImage.Format_Indexed8

        if len(img.shape) == 3:  # [0]=rows, [1]=cols, [2]=channels
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        # BGR --> RGB
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)
        if window == 2:
            self.motionLabel.setPixmap(QPixmap.fromImage(outImage))
            self.motionLabel.setScaledContents(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = surveilMotion()
    window.setWindowTitle('Surveillance Window')
    window.show()
    sys.exit(app.exec_())
