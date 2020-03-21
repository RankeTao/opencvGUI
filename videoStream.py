import sys

import cv2
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap


class webCam(QDialog):
    def __init__(self):
        super(webCam, self).__init__()
        loadUi('ui/webcam.ui', self)

        self.image = None
        self.processedImage = None
        self.startButton.clicked.connect(self.start_webcam)
        self.stopButton.clicked.connect(self.stop_webcam)
        self.cannyButton.toggled.connect(self.canny_webcam)
        self.cannyButton.setCheckable(True)
        self.canny_Enabled = False
        self.detectButton.setCheckable(True)
        self.detectButton.toggled.connect(self.detect_webcam_face)
        self.face_Enabled = False

        self.faceCascade = cv2.CascadeClassifier('opencvfiles/haarcascade_frontalface_default.xml')

    def detect_webcam_face(self, status):
        if status:
            self.detectButton.setText('Stop Dectection')
            self.face_Enabled = True
        else:
            self.detectButton.setText('Dectect Face')
            self.face_Enabled = False


    def canny_webcam(self, status):
        if status:
            self.canny_Enabled = True
            self.cannyButton.setText('Canny Stop')
        else:
            self.canny_Enabled = False
            self.cannyButton.setText('Canny')

    def start_webcam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def update_frame(self):
        ret, self.image = self.capture.read()
        self.image = cv2.flip(self.image, 1)

        if self.face_Enabled:
            detected_image = self.detect_face(self.image)
            self.displayImage(detected_image, 1)
        else:
            self.displayImage(self.image, 1)

        if self.canny_Enabled:
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) if len(self.image.shape) >=3 else self.image
            self.processedImage = cv2.Canny(gray, 100, 200)
            self.displayImage(self.processedImage, 2)
        else:
            img = cv2.imread('image/4436.JPG')
            self.displayImage(img, 2)

    def detect_face(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(gray, 1.3, 5, minSize=(90, 90))
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        return img

    def stop_webcam(self):
        self.timer.stop()

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
            self.processedLabel.setPixmap(QPixmap.fromImage(outImage))
            self.processedLabel.setScaledContents(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = webCam()
    window.setWindowTitle('Web Cam Stream')
    window.show()
    sys.exit(app.exec_())