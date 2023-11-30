import maya.cmds as cmds
import os
#import sg_utils
import tonic_nodeUtil

def tonic_openerMaya():

    if 'TONIC_TASK_ID' in os.environ and len(os.environ['TONIC_TASK_ID']) > 0:
        if not cmds.pluginInfo('tonic_node', query=True, loaded=True):
            cmds.loadPlugin('tonic_node')

        #Hijack some default Maya Menus
        tonic_hijackSaveAs()
        #tonic_hijackOpen()

        task_id = os.environ['TONIC_TASK_ID']

        #If it doesn't have a tonic_node, create one
        all_existing_tonicnodes = tonic_nodeUtil.tonic_get_all_tonic_nodes()
        if all_existing_tonicnodes:
            print('all_existing_tonicnodes')
            print(all_existing_tonicnodes)
            pass
        else:
            tonic_nodeUtil.tonic_create_tonic_node_for_task_id(int(task_id))


def tonic_hijackSaveAs(enable=True):
    import maya.mel as mel
    if enable:
        # no install if in batch mode
        if cmds.about(batch=True):
            return
        # hijack save button
        cmds.iconTextButton(u"saveSceneButton", edit=True, command='python("import tonic_saveGUI;tonic_saveGUI.main()")', sourceType="mel")
        # hijack save menu item
        mel.eval("buildFileMenu();")  # new in Maya 2009, we have to explicitly create the file menu before modifying it
        cmds.setParent(u"mainFileMenu", menu=True)
        cmds.menuItem(u"saveAsItem", edit=True, label="Save Scene As...", command='import tonic_saveGUI;tonic_saveGUI.main()')
        cmds.menuItem(u"saveAsOptions", edit=True, command='import tonic_saveGUI;tonic_saveGUI.main()')
        cmds.nameCommand(u"NameComSave_File_As", annotation="nGenious Save As", command='python(\"import tonic_saveGUI;tonic_saveGUI.main()\")')

def tonic_hijackOpen(enable=True):
    import maya.mel as mel
    if enable:
        # no install if in batch mode
        if cmds.about(batch=True):
            return

        #Check what python version is running and run the right ngsBrowser
        import sys

        # hijack open button
        cmds.iconTextButton(u"openSceneButton", edit=True, command="python(\"import tonic_browserGUI;mainwindow=tonic_browserGUI.MainWindow(\'InsideApp:True;OpenTask:True;Inspector:False\')\")", sourceType="mel")
        # hijack open menu item
        mel.eval("buildFileMenu();")  # new in Maya 2009, we have to explicitly create the file menu before modifying it
        cmds.setParent(u"mainFileMenu", menu=True)
        cmds.menuItem(u"openProject", edit=True, label="Open Scene...", command='import tonic_browserGUI;mainwindow=tonic_browserGUI.MainWindow(\'InsideApp:True;OpenTask:True;Inspector:False\')')
        cmds.menuItem(u"openFileOptions", edit=True, command='import tonic_browserGUI;mainwindow=tonic_browserGUI.MainWindow(\"InsideApp:True;OpenTask:True;Inspector:False\")')
        # hijack CTRL-O named command
        cmds.nameCommand(u"NameComOpen_File", annotation="Tonic Open File", command='python(\"import tonic_browserGUI;mainwindow=tonic_browserGUI.MainWindow(\'InsideApp:True;OpenTask:True;Inspector:False\')\")')

