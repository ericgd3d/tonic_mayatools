"""
Contains the menu creation functions as wells as any other functions the menus rely on.
"""

import maya.cmds as cmds
import maya.mel as mel

GC_PROTECT = []

def create_menu():
    import sys

    """Creates the CMT menu."""
    gmainwindow = mel.eval('$tmp = $gMainWindow;')
    menu = cmds.menu(parent=gmainwindow, tearOff=True, label='TonicDNA')

    tonic_anim_menu = cmds.menuItem(subMenu=True, tearOff=True, parent=menu, label='Animation')

    cmds.menuItem(parent=tonic_anim_menu,
                  label='Export to Alembic',
                  #command='import tonic_exportAbcGUI;mainwindow=tonic_exportAbcGUI.MainWindow()',
                  command='import tonic_alembic; tonic_alembic.exportAbc())',
                  imageOverlayLabel='ExportAbc')

