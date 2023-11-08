import maya.cmds as cmds
import subprocess
import os

# Create tonic_menu
print ('* * * loading oldest pipeline tools * * * ')
import tonic_menu
cmds.evalDeferred("tonic_menu.create_menu()")

try:
    import tonic_openerMaya
    cmds.evalDeferred("tonic_openerMaya.tonic_openerMaya()")
except ImportError:
    pass

    
