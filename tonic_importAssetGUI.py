import maya.cmds as cmds
from maya import OpenMayaUI as mui

from PySide2.QtCore import QFile, QTimer, QSettings
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtUiTools import QUiLoader

from shiboken2 import wrapInstance
import os
import sg_utils

DEBUG = True

class qTask(QtWidgets.QLabel):
        entity = ''
        entityType = ''
        entityId = ''
        step = ''
        task = ''
        duedate = ''
        status = ''
        comments = ''
        version = '-'
        bookmarks = ''
        id = ''
        usdPath = ''

        # color = white red green
        version_color = 'white'
        duedate_color = 'white'

        def __init__(self, entity='', step='', task='', duedate='', status='', comments=''):
            QtWidgets.QLabel.__init__(self)
            if entity and step and task and duedate and status and comments:
                self.create()

        def create(self):

            html_content = '<style type="text/css">p, li { white-space: pre-wrap; }</style>' \
                        '</head><body style=" font-family:"Cantarell"; font-size:11pt; font-weight:400; font-style:normal;">' \
                        '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; '\
                        'text-indent:0px; text-align:left; font-size:10pt">' \
                        '<span style=" font-weight:600;">%s </span> </p></body></html>' \
                           % (self.entity + '  (v' + '{:03d}'.format(int(self.version))+ ')')

            self.setFocusPolicy(QtCore.Qt.NoFocus)
            self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            self.setText(html_content)


def getMayaWindow():
    '''
    Get the maya main window as a QMainWindow instance
    '''

    mayaMainWindowPtr = mui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtGui.QWidget)
    return mayaMainWindow



if __name__ == '__main__':
    app = QApplication.instance()
    if app:
        # inside maya there is already a window widget
        mainwindow = MainWindow()

class MainWindow(QMainWindow):
    tasks_visible = False

    def __init__(self):
        super(MainWindow, self).__init__()

        # Init some class variable
        self.load_ui()

        # set window icon
        self.ui.setWindowIcon(QtGui.QIcon('C:/TonicDNA/Pipeline/scripts/tonic_gui/TonicDNA_monogram-GREEN_RGB-768x536.png'))


        #Override default values
        self.ui.setWindowTitle('Import Published Asset')
        self.ui.btn_ok.setText('Import')
        self.ui.btn_cancel.setText('Close')
        self.ui.chk_checkBox.setVisible(False)
        self.ui.cb_filter.removeItem(0)

        self.ui.show()


    def btn_clear_sel_click(self):
        for t in range(len(self.tables_tasks)):
            self.ui.tbl_tasks.setCurrentCell(t, 0, QtCore.QItemSelectionModel.Deselect | QtCore.QItemSelectionModel.Rows)

    def btn_cancel_click(self):
        self.ui.close()

    def btn_open_click(self):

        print('open click')

        for i in self.ui.tbl_tasks.selectedIndexes():
            print('ngs_importAsset2GUI| i: %s' % i)

            if self.tables_tasks:
                assetName = (self.tables_tasks[i.row()].entity).replace(' ', '')

                #Get the namespace name. We put R1 at the end for Reference1. Maya will get the next available number. We will retrieve this numver later
                cmds.namespace(set=':')
                assetNamespace = (assetName + '_R1')


                # Reference the Alembic file
                alembic_file_path = (self.tables_tasks[i.row()].filepath)
                all_nodes_before = set(cmds.ls(l=True))
                cmds.file(alembic_file_path, reference=True, namespace=assetNamespace)
                all_nodes_after = set(cmds.ls(l=True))
                new_nodes = list(all_nodes_after - all_nodes_before)

                if new_nodes:
                    import tonic_mayaUtil

                    #Create the root group with the same namespace as the referenced asset
                    #Time to retrieve the namespace name given automatically by maya
                    all_ns = tonic_mayaUtil.tonic_get_all_namespaces_of_list(new_nodes)
                    if all_ns:
                        root_group = cmds.group(name=all_ns[0]+':Root', em=True)
                    else:
                        root_group = cmds.group(name=assetNamespace+':Root', em=True)

                    #Parent the referenced asset to the root node
                    all_roots = tonic_mayaUtil.tonic_get_all_roots_of_list(new_nodes)
                    if all_roots:
                        cmds.parent(all_roots, root_group)



    def load_ui(self):
        # load UI
        dev_version = '0.01'
        ui_version = '0.01'


        self.TONIC_UIVERSION = '%s-ui-%s' % (dev_version, ui_version)
        uifile = QFile('C:/TonicDNA/Pipeline/scripts/tonic_gui/tonic_qTask_%s.ui' % ui_version)

        ver_html_content = '<html><head/><body><p><span style=" color:#646464;">%s</span></p></body></html>' % self.TONIC_UIVERSION

        uifile.open(QFile.ReadOnly)
        mainWindow = QUiLoader().load(uifile)
        uifile.close()

        self.TONIC_PROJECT = os.environ.get('TONIC_PROJECT')

        self.server = os.environ["TONIC_SERVER"]
        self.sg = sg_utils.get_sg(self.server)

        self.all_publishes = self.tonic_buildProjectPublishesList()

        # instance window class to access widget
        self.ui = mainWindow
        self.ui.lbl_uiversion.setText(ver_html_content)

        # force logo path
        self.ui.lbl_logo.setPixmap('C:/TonicDNA/Pipeline/scripts/tonic_gui/TonicDNA_monogram-GREEN_RGB-768x536.png')
        self.ui.btn_ok.clicked.connect(self.btn_open_click)
        self.ui.btn_cancel.clicked.connect(self.btn_cancel_click)
        self.ui.btn_clear_sel.clicked.connect(self.btn_clear_sel_click)

        self.ui.cb_filter.addItems(["All", "Character", "Prop", "Set", "Lightrig"])
        self.ui.cb_filter.currentIndexChanged.connect(self.set_ui_data)
        self.ui.ln_search.textChanged.connect(self.set_ui_data)

        self.ui.cb_asset_step.clear()
        self.ui.cb_asset_step.addItems(["Rig", "Texture", "Model"])
        self.ui.cb_asset_step.currentIndexChanged.connect(self.set_ui_data)
        #self.ui.cb_asset_step.setVisible(False)
        # update UI data
        #self.set_ui_data()


    def set_ui_data(self, event_name=None):

        all_filtered_publishes = self.tonic_filter_publishes()

        self.tables_tasks = []

        # initialize a table somehow
        table = self.ui.tbl_tasks
        table.setColumnCount(1)
        table.setRowCount(0)

        if all_filtered_publishes:
            for t in range(len(all_filtered_publishes)):
                table.setRowCount(t + 1)
                # example instance a task

                new_task = qTask()

                # fill the task class
                # print prjTasks[t]
                #print all_publishes[t]
                new_task.entity = '   ' + str(all_filtered_publishes[t]['asset_name'])
                new_task.step = '   ' + str(all_filtered_publishes[t]['step_name'])
                new_task.version = str(all_filtered_publishes[t]['version_nb'])
                new_task.filepath = str(all_filtered_publishes[t]['filepath'])

                # create the widget
                new_task.create()

                # create a second task with a different way
                table.setCellWidget(t, 0, new_task)

                # set a fix size for the grid to be sure the label fit in it
                #table.setRowHeight(t, 90)
                #table.setColumnWidth(t, 401)
                table.setRowHeight(t, 25)
                table.setColumnWidth(t, 320)

                self.tables_tasks.append(new_task)

            self.ui.tbl_tasks.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            #self.ui.tbl_tasks.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            #self.ui.tbl_tasks.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)


    def tonic_buildProjectPublishesList(self):
        all_publishes = []
        published_file_type_name = '.abc'
        sgtask = None  # Get published file of everything, not attached to a specific task

        all_published_files = sg_utils.tonic_get_publish_files(self.sg, task_dict=sgtask, file_type=published_file_type_name,
                                                      approved_only=True)

        if all_published_files:
            for pf in all_published_files:
                a = {}

                #print(pf)
                #Get info on the asset

                sg_asset = sg_utils.get_sg_entity_by_id(self.sg, pf['entity']['type'], pf['entity']['id'], ['sg_asset_type'])
                sg_task = sg_utils.get_sg_entity_by_id(self.sg, 'Task', pf['task']['id'], ['step'])

                #print(sg_asset)
                #print(sg_task)
                a['asset_type'] = sg_asset['sg_asset_type']
                a['asset_name'] = pf['entity']['name']
                a['step_name'] = sg_task['step']['name']
                a['task_id'] = sg_task['id']
                a['version_nb'] = pf['version_number']
                a['filepath'] = pf['path_cache']
                a['publish_file_id'] = pf['id']
                a['date'] = pf['created_at']
                all_publishes.append(a)

        return all_publishes

    def tonic_filter_publishes(self):
        if DEBUG:
            print('in tonic_filter_publishes')

        currFilterStr = str(self.ui.cb_filter.currentText())
        stepToSearch = str(self.ui.cb_asset_step.currentText())
        searchStr = str(self.ui.ln_search.text())


        allValidTypes = ['Character', 'Prop', 'Set', 'Lightrig']
        all_good_publishes = []

        if self.all_publishes:
            for t in self.all_publishes:

                sibling_versions = sorted([s for s in self.all_publishes if s.get('task_id') == t['task_id']], key=lambda k: k['version_nb'], reverse=True)
                latest_published_version_nb= sibling_versions[0]['version_nb']

                if t['version_nb'] == latest_published_version_nb:
                    #This is the latest publish of the task
                    if ((currFilterStr == 'All' and t['asset_type'] in allValidTypes)  or currFilterStr == t['asset_type']) and stepToSearch == t['step_name']:
                        if len(searchStr):
                            if searchStr.startswith('*'):
                                if searchStr.lstrip('*') in t['asset_name']:
                                    all_good_publishes.append(t)
                            else:
                                if t['asset_name'].startswith(searchStr):
                                    all_good_publishes.append(t)
                        else:
                            all_good_publishes.append(t)

        sorted_publishes = sorted(all_good_publishes, key=lambda x: x['asset_name'])
        return sorted_publishes

