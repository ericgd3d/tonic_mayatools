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
                  label='Export Selected to Alembic',
                  #command='import tonic_exportAbcGUI;mainwindow=tonic_exportAbcGUI.MainWindow()',
                  command='import tonic_alembic;tonic_alembic.ton_legacy_export_sel_abc()',
                  imageOverlayLabel='ExportAbc')

    tonic_asset_menu = cmds.menuItem(subMenu=True, tearOff=True, parent=menu, label='Assets')
    cmds.menuItem(parent=tonic_asset_menu,
                  label='Convert All Textures into Rstexbin',
                  command='import tonic_rstexbin;tonic_rstexbin.ngs_convertFileNodeTextureToRedshiftTexture()',
                  imageOverlayLabel='Convert2Rstexbin')

    cmds.menuItem(parent=tonic_asset_menu,
                  label='Import Asset',
                  command='import tonic_importAssetGUI;mainwindow=tonic_importAssetGUI.MainWindow()',
                  imageOverlayLabel='Import Asset')


