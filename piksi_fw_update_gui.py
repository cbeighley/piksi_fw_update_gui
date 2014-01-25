#!/usr/bin/env python
import sys
#TODO: seeing if only importing used objects reduces pyinstaller
#      generated binary size
from PyQt4 import QtGui, QtCore, QtSvg
from PyQt4.QtGui import QSizePolicy

REV = 0.1
# TODO: see if there's a better way to size and position things
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 400
BUTTON_MAX_WIDTH = 200
BOXES_MAX_WIDTH = 350
#LOGO_HEIGHT = 300
#LOGO_WIDTH = 200

def download():
  print "yes"

class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

# Swift Navigation Logo with a fixed aspect ratio.
class SwiftNavLogo(QtSvg.QSvgWidget):
  filename = 'sn_logo.svg'
  h_to_w = float(232)/350

  def __init__(self, parent=None):
    QtSvg.QSvgWidget.__init__(self, self.filename, parent)
    policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
    policy.setHeightForWidth(True)
    policy.setWidthForHeight(True)
    self.setSizePolicy(policy)

  def heightForWidth(self, width):
    return int(width*self.h_to_w)

  def widthForHeight(self, height):
    return int(height*(1/self.h_to_w))

class PiksiUpdateGUI(QtGui.QWidget):

  def __init__(self):
    super(PiksiUpdateGUI, self).__init__()

    sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)

    # Start window in center of screen, make its size fixed.
    dt = QtGui.QApplication.desktop().availableGeometry()
    dt_center = dt.center()
#    self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    self.setGeometry(dt_center.x()-self.width()*0.5, dt_center.y()-self.height()*0.5, WINDOW_WIDTH, WINDOW_HEIGHT)
#    self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    self.move(dt_center.x()-self.width()*0.5, dt_center.y()-self.height()*0.5)

    vbox_l = QtGui.QVBoxLayout()
    vbox_r = QtGui.QVBoxLayout()
    hbox = QtGui.QHBoxLayout()
    hbox.insertStretch(1)
    hbox.addLayout(vbox_l, stretch = 1)
    hbox.insertStretch(3)
    hbox.addLayout(vbox_r, stretch = 1)

    # Swift Navigation Inc logo.
    logo = SwiftNavLogo()

    # Buttons
    prog_btn = QtGui.QPushButton('Program', self)
    prog_btn.setToolTip('Program Piksi with the downloaded firmware')
    prog_btn.setMaximumWidth(BUTTON_MAX_WIDTH)
    prog_btn.clicked.connect(self.program)

    dl_btn = QtGui.QPushButton('Download', self)
    dl_btn.setToolTip('Download the latest firmware from Swift Navigation')
    dl_btn.setMaximumWidth(BUTTON_MAX_WIDTH)
    dl_btn.clicked.connect(download)

    # TODO: make quit button the same as window quit button, or remove?
    quit_btn = QtGui.QPushButton('Quit', self)
    quit_btn.setToolTip('Exit the program')
    quit_btn.setMaximumWidth(BUTTON_MAX_WIDTH)
    quit_btn.clicked.connect(QtCore.QCoreApplication.instance().quit)

    # Progress bar.
    self.pbar = QtGui.QProgressBar(self)
#    self.pbar.setMaximumWidth(BOXES_MAX_WIDTH)
    self.pbar_val = 0

    # Console output.
    self.output = QtGui.QTextEdit()
#    self.output.setMaximumWidth(BOXES_MAX_WIDTH)

    # Add widgets to boxes and set positions.
    vbox_l.addWidget(logo)
    vbox_l.addWidget(prog_btn)
    vbox_l.addWidget(dl_btn)
    vbox_l.addWidget(quit_btn)
    vbox_l.insertStretch(4)

    vbox_r.addWidget(self.output)
    vbox_r.addWidget(self.pbar)

    self.setLayout(hbox)

    self.setWindowTitle('Piksi Firmware Update Tool v' + str(REV))
    self.show()


  # TODO: warn if firmware update or download is in process
  def closeEvent(self, event):
    reply = QtGui.QMessageBox.question(self, 'Message',
                                 "Are you sure to quit?",
                                 QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                 QtGui.QMessageBox.No)
    if reply == QtGui.QMessageBox.Yes:
      event.accept()
    else:
      event.ignore()

  def normalOutputWritten(self, text):
    """Append text to the QTextEdit."""
    # Maybe QTextEdit.append() works as well, but this is how I do it:
    cursor = self.output.textCursor()
    cursor.movePosition(QtGui.QTextCursor.End)
    cursor.insertText(text)
    self.output.setTextCursor(cursor)
    self.output.ensureCursorVisible()

  # TODO: Add console
  # TODO: Add progress bar

  def program(self):
    print "herro"
    self.pbar.setValue(self.pbar_val)
    self.pbar_val += 10

#TODO : add visible flag to see if firmware is most current release
def main():

  app = QtGui.QApplication(sys.argv)
  gui = PiksiUpdateGUI()
  sys.exit(app.exec_())


if __name__ == '__main__':
  main()
