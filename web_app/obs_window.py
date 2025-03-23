import sys
from PyQt5 import QtWidgets, QtGui


class OBSWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.WINDOW_WIDTH = 30
        self.WINDOW_HEIGHT = 30

        self.set_window_properties()

    def set_window_properties(self):
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setWindowTitle("ModPlod AI")
        self.setWindowIcon(QtGui.QIcon('images/icon.png'))
        self.show()


def start_obs_audio_window():
    try: 
        app = QtWidgets.QApplication(sys.argv)
        window = OBSWindow()
        app.exec_()
    except Exception as e:
        print(f"Failed to start window: {e}")