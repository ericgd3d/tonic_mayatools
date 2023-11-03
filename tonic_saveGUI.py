import sys
from maya import OpenMayaUI as mui
from shiboken2 import wrapInstance
from PySide2.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QRadioButton, QWidget

class TonicSaveDialog(QDialog):
    def __init__(self, parent=None):
        super(TonicSaveDialog, self).__init__(parent)
        self.setWindowTitle("TonicDNA Save")
        self.setFixedSize(750, 320)
        self.setStyleSheet("background-color: rgb(50, 50, 50); alternate-background-color: rgb(212, 0, 0); selection-color: rgb(210, 210, 210); color: rgb(255, 255, 255); selection-background-color: rgb(66, 66, 66);")

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Create a horizontal layout for the top section (logo and filename)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 10, 0, 0)

        lbl_logo = QLabel()
        lbl_logo.setFixedSize(125, 75)
        lbl_logo.setPixmap(QtGui.QPixmap("C:/TonicDNA/Pipeline/scripts/tonic_gui/TonicDNA_monogram-GREEN_RGB-768x536.png"))
        lbl_logo.setScaledContents(True)
        top_layout.addWidget(lbl_logo)

        lbl_filename = QLabel("filename")
        lbl_filename.setFont(QtGui.QFont("", 18))
        lbl_filename.setAlignment(QtCore.Qt.AlignCenter)
        top_layout.addWidget(lbl_filename)

        layout.addLayout(top_layout)


        # Create a vertical layout for the middle section (radio buttons, media path, and comments)
        radio_layout = QVBoxLayout()
        radio_layout.setContentsMargins(45,20,0,0)



        rb_wip = QRadioButton("Save New Version of Work in Progress")
        rb_approval = QRadioButton("Save New Version and Send for Approval")

        radio_layout.addWidget(rb_wip)
        radio_layout.addWidget(rb_approval)

        layout.addLayout(radio_layout)

        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(100, 0, 0, 10)

        lbl_media = QLabel("Path of Media:")
        le_path = QLineEdit()
        btn_browse = QPushButton("Browse")

        path_layout.addWidget(lbl_media)
        path_layout.addWidget(le_path)
        path_layout.addWidget(btn_browse)

        layout.addLayout(path_layout)


        # Create a separator (QFrame) between "Path of Media" and "Comments"
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        comm_layout = QHBoxLayout()
        comm_layout.setContentsMargins(45, 10, 0, 10)

        lbl_comments = QLabel("Comments:")
        comm_layout.addWidget(lbl_comments)

        le_comments = QLineEdit()
        comm_layout.addWidget(le_comments)

        layout.addLayout(comm_layout)

        # Create a separator (QFrame) between "Path of Media" and "Comments"
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator2)

        # Create a horizontal layout for the bottom section (save and cancel buttons)
        button_layout = QHBoxLayout()
        #button_layout.setContentsMargins(300, 0, 30, 20)
        # Create an empty spacer with a width of 100 pixels to offset the buttons to the right
        button_spacer = QSpacerItem(500, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_layout.addItem(button_spacer)

        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")

        button_layout.addWidget(btn_save)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)

        msg_layout = QHBoxLayout()
        msg_layout.setContentsMargins(10, 0, 0, 0)
        lbl_message = QLabel("message")
        msg_layout.addWidget(lbl_message)
        layout.addLayout(msg_layout)

        self.setLayout(layout)

def main():
    app = QApplication.instance()
    if not app:
        app = QApplication([])

    dialog = TonicSaveDialog(wrapInstance(int(mui.MQtUtil.mainWindow()), QWidget))
    dialog.show()

    app.exec_()  # Start the event loop

if __name__ == '__main__':
    main()