#!/usr/bin/env python
import sys
#TODO: seeing if only importing used objects reduces pyinstaller
#      generated binary size
from PyQt4 import QtGui, QtCore, QtSvg
from PyQt4.QtGui import QSizePolicy, QMessageBox, QFileDialog
from intelhex import IntelHex, HexRecordError
from os.path import relpath

# TODO: Set icon to Swift Nav Logo

REV = 0.1
# TODO: see if there's a better way to size and position things
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 425
LEFT_MAX_WIDTH = 250

def download():
  print "yes"

class ConsoleStream(QtCore.QObject):
  textWritten = QtCore.pyqtSignal(str)

  def write(self, text):
    self.textWritten.emit(str(text))

class Console(QtGui.QTextEdit):

  def __init__(self):
    super(Console, self).__init__()
    sys.stdout = ConsoleStream(textWritten = self.write_text)

  def __del__(self):
    self.stop()

  def stop(self):
    sys.stdout = sys.__stdout__

  def write_text(self, text):
    cursor = self.textCursor()
    cursor.movePosition(QtGui.QTextCursor.End)
    cursor.insertText(text)
    self.setTextCursor(cursor)
    self.ensureCursorVisible()

# Swift Navigation Logo with a fixed aspect ratio.
class SwiftNavLogo(QtSvg.QSvgWidget):
  filename = 'sn_logo.svg'
  h_to_w = float(232)/350 # Aspect ratio of original image.

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

class EmptyIntelHexError(Exception):

   def __init__(self):
      super(EmptyIntelHexError, self).__init__()

class Firmware(QtGui.QLineEdit):

  def __init__(self):
    super(Firmware, self).__init__()
    self.ihx = None
    self.setReadOnly(True)

  def load(self, fname):
    tmp = IntelHex(fname)
    # If empty file is loaded IntelHex instantiation doesn't raise an error.
    if tmp.addresses() == []:
      raise EmptyIntelHexError
    else:
      self.ihx = tmp
      self.setText(relpath(fname))

# TODO: add add actions to menu
class PiksiUpdateGUI(QtGui.QMainWindow):

  def __init__(self):
    super(PiksiUpdateGUI, self).__init__()

    # Main window of GUI.
    win = QtGui.QWidget()

    # File dialog for loading firmware files.
    openFile = QtGui.QAction(QtGui.QIcon('free.png'), 'Open', self)
    openFile.setShortcut('Ctrl+O')
    openFile.setStatusTip('Open new File')
    openFile.triggered.connect(self.loadFirmwaresDialog)

    # Start window in center of screen, make its size fixed.
    dt = QtGui.QApplication.desktop().availableGeometry()
    dt_center = dt.center()
    self.setGeometry(dt_center.x()-self.width()*0.5,
                     dt_center.y()-self.height()*0.5,
                     WINDOW_WIDTH, WINDOW_HEIGHT)
    self.move(dt_center.x()-self.width()*0.5, dt_center.y()-self.height()*0.5)

    # Swift Navigation Inc logo.
    logo = SwiftNavLogo()

    # Buttons
    prog_btn = QtGui.QPushButton('Program', self)
    prog_btn.setToolTip('Program Piksi with the selected firmware')
    prog_btn.setMaximumWidth(LEFT_MAX_WIDTH)
    prog_btn.clicked.connect(self.program)

    dl_btn = QtGui.QPushButton('Download', self)
    dl_btn.setToolTip('Download the latest firmware from Swift Navigation')
    dl_btn.setMaximumWidth(LEFT_MAX_WIDTH)
    dl_btn.clicked.connect(download)

    quit_btn = QtGui.QPushButton('Quit', self)
    quit_btn.setToolTip('Exit the program')
    quit_btn.setMaximumWidth(LEFT_MAX_WIDTH)
    quit_btn.clicked.connect(self.close)

    load_btn = QtGui.QPushButton('Load', self)
    load_btn.setToolTip('Load firmware files to program Piksi with')
    load_btn.setMaximumWidth(LEFT_MAX_WIDTH)
    load_btn.clicked.connect(self.loadFirmwaresDialog)

    # Progress bar.
    self.pbar = QtGui.QProgressBar(self)
    self.pbar_val = 0

    # Console output.
    self.console = Console()

    # Lines that have Intel Hex firmware files associated with them.
    self.stm_fw = Firmware()
    self.stm_fw.setMaximumWidth(LEFT_MAX_WIDTH)
    self.stm_label = QtGui.QLabel('STM Firmware', self)
    self.fpga_fw = Firmware()
    self.fpga_fw.setMaximumWidth(LEFT_MAX_WIDTH)
    self.fpga_label = QtGui.QLabel('FPGA Firmware', self)

    # Set vertical boxes.
    vbox_l = QtGui.QVBoxLayout()
    vbox_r = QtGui.QVBoxLayout()
    hbox = QtGui.QHBoxLayout()
    hbox.insertStretch(1)
    hbox.addLayout(vbox_l, stretch = 1)
    hbox.insertStretch(3)
    hbox.addLayout(vbox_r, stretch = 1)

    # Add widgets to boxes and set positions.
    vbox_l.addWidget(logo)
    vbox_l.addWidget(prog_btn)
    vbox_l.addWidget(dl_btn)
    vbox_l.addWidget(load_btn)
    vbox_l.addWidget(quit_btn)
    vbox_l.addWidget(self.stm_label)
    vbox_l.addWidget(self.stm_fw)
    vbox_l.addWidget(self.fpga_label)
    vbox_l.addWidget(self.fpga_fw)
    vbox_l.insertStretch(-1)

    vbox_r.addWidget(self.console)
    vbox_r.addWidget(self.pbar)

    # Menu for alternate actions.
    menubar = self.menuBar()
    fileMenu = menubar.addMenu('&File')
    fileMenu.addAction(openFile)

    win.setLayout(hbox)

    self.setWindowTitle('Piksi Firmware Update Tool v' + str(REV))
    self.setCentralWidget(win)
    self.show()

  def __del__(self):
    self.console.stop()

  # TODO: warn if firmware update or download is in process
  def closeEvent(self, event):
    reply = QMessageBox.question(self, 'Message',
                                 "Are you sure you want to quit?",
                                 QMessageBox.Yes | QMessageBox.No,
                                 QMessageBox.No)
    if reply == QMessageBox.Yes:
      event.accept()
    else:
      event.ignore()

  def program(self):
    print "herro"
    self.pbar_val += 10
    self.pbar.setValue(self.pbar_val)

  def loadFirmwaresDialog(self):
    fname = str(QFileDialog.getOpenFileName(self, 'Select STM Firmware File'))
    if fname:
      try:
        self.stm_fw.load(fname)
      except HexRecordError : # Incorrect file type.
        QMessageBox.warning(self, "Error : Incorrect file type",
                            "Incorrect file type (not an Intel Hex file).")
        return
      except EmptyIntelHexError : # Empty file loaded.
        QMessageBox.warning(self, "Error : Empty file", "Hex file is empty.")
        return
    else:
      return

    fname = str(QFileDialog.getOpenFileName(self, 'Select FPGA Firmware File'))
    if fname:
      try:
        self.fpga_fw.load(fname)
      except HexRecordError : # Incorrect file type.
        QMessageBox.warning(self, "Error : Incorrect file type",
                            "Incorrect file type (not an Intel Hex file).")
      except EmptyIntelHexError : # Empty file loaded.
        QMessageBox.warning(self, "Error : Empty file", "Hex file is empty.")

#TODO : add visible flag to see if firmware is most current release
def main():
  app = QtGui.QApplication(sys.argv)
  gui = PiksiUpdateGUI()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
