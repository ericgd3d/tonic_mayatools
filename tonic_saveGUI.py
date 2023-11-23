import sys
from maya import OpenMayaUI as mui
from shiboken2 import wrapInstance
from PySide2.QtWidgets import QApplication, QDialog, QFileDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QRadioButton, QWidget, QFrame, QSpacerItem, QSizePolicy
from PySide2.QtCore import Qt
from PySide2 import QtGui, QtCore
import sg_utils
import tonic_nodeUtil
import os

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

        server = os.environ["TONIC_SERVER"]
        self.current_sgtask = None
        self.next_publish_file = None
        if server:
            self.sg = sg_utils.get_sg(server)
            self.current_sgtask = tonic_nodeUtil.tonic_get_current_sgtask(self.sg)

        if self.current_sgtask:
            print(self.current_sgtask)
            next_version_number = 1
            published_files = sg_utils.tonic_get_publish_files(self.sg, self.current_sgtask)
            if published_files:
                latest_publish = published_files[0]
                latest_version_number = latest_publish['version_number']
                if latest_version_number:
                    next_version_number = latest_version_number + 1

            #server, sg, template_name, task_dict, version):

            if self.current_sgtask['entity']['type'] == 'Asset':
                template_name = 'maya_asset_work'
            elif self.current_sgtask['entity']['type'] == 'Shot':
                template_name = 'maya_shot_work'


            self.next_publish_file = sg_utils.tonic_get_path_from_template(server, self.sg, template_name=template_name, task_dict=self.current_sgtask, version=next_version_number)
            if self.next_publish_file:
                print(self.next_publish_file)

        if self.next_publish_file:
            lbl_filename = QLabel(os.path.basename(self.next_publish_file))
        else:
            lbl_filename = QLabel("filename")

        lbl_filename.setFont(QtGui.QFont("", 18))
        lbl_filename.setAlignment(QtCore.Qt.AlignCenter)
        top_layout.addWidget(lbl_filename)

        layout.addLayout(top_layout)


        # Create a vertical layout for the middle section (radio buttons, media path, and comments)
        radio_layout = QVBoxLayout()
        radio_layout.setContentsMargins(45,20,0,0)



        self.rb_wip = QRadioButton("Save New Version of Work in Progress")
        self.rb_approval = QRadioButton("Save New Version and Send for Approval")

        radio_layout.addWidget(self.rb_wip)
        radio_layout.addWidget(self.rb_approval)

        layout.addLayout(radio_layout)

        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(100, 0, 0, 10)

        self.lbl_media = QLabel("Path of Media:")
        self.le_path = QLineEdit()
        self.btn_browse = QPushButton("Browse")
        self.btn_browse.clicked.connect(self.browse_file)

        path_layout.addWidget(self.lbl_media)
        path_layout.addWidget(self.le_path)
        path_layout.addWidget(self.btn_browse)

        layout.addLayout(path_layout)
        self.rb_wip.setChecked(True)  # Set the first radio button to be selected by default
        self.rb_approval.toggled.connect(self.tonic_make_browser_enable)
        self.tonic_make_browser_enable()


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
        btn_cancel.clicked.connect(self.tonic_cancel)


        button_layout.addWidget(btn_save)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)

        msg_layout = QHBoxLayout()
        msg_layout.setContentsMargins(10, 0, 0, 0)
        lbl_message = QLabel("")
        msg_layout.addWidget(lbl_message)
        layout.addLayout(msg_layout)



        self.setLayout(layout)

    def tonic_cancel(self):
        print('cancel')
        self.close()

    def tonic_make_browser_enable(self):
        if self.rb_approval.isChecked():
            print('appr')
            self.lbl_media.setText("Path of Media:")
            self.le_path.setVisible(True)
            self.btn_browse.setVisible(True)
        else:
            print('wip')
            self.lbl_media.setText(" ")
            self.le_path.setVisible(False)
            self.btn_browse.setVisible(False)

    def browse_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # Make sure the user can only select existing files

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a File",
            "",  # Provide a directory path to start in, or leave it empty for the default location
            "All Files (*);;Jpeg Files (*.jpg);;Movie Files (*.mov)"  # Define the file filters if needed
        )

        if file_path:
            self.le_path.setText(file_path)



def main():
    app = QApplication.instance()
    if not app:
        app = QApplication([])

    dialog = TonicSaveDialog(wrapInstance(int(mui.MQtUtil.mainWindow()), QWidget))
    dialog.show()

    app.exec_()  # Start the event loop

#if __name__ == '__main__':
#    main()