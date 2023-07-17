import shutil

import maya.cmds as cmds
import tempfile
import ctypes

DEBUG = True
def ton_legacy_export_sel_abc(full_temp_dir=None):
    #An alembic exporter for legacy scenes

    print('Exporting Abc')

    scene_path = cmds.file(query=True, sceneName=True)

    temp_dir = tempfile.gettempdir()
    full_temp_dir = ctypes.create_unicode_buffer(512)
    ctypes.windll.kernel32.GetLongPathNameW(temp_dir, full_temp_dir, ctypes.sizeof(full_temp_dir))

    tmpDir = (full_temp_dir.value).replace("\\", "/")


    abcExportPath = getExportPath(scene_path)




    startFrame = cmds.playbackOptions(query=True, min=True)
    endFrame = cmds.playbackOptions(query=True, max=True)

    selNodes = cmds.ls(sl=True, l=True)
    allSelReferenceNodes = find_referenced_nodes(selNodes)
    #print(allSelReferenceNodes)

    for refNode in allSelReferenceNodes:
        referenced_nodes = cmds.referenceQuery(refNode, nodes=True)

        if referenced_nodes:
            refNS = cmds.referenceQuery(refNode, namespace=True)[1:]

            #print(refNS)
            abcPath = abcExportPath + '/' + refNS + '.abc'
            tmpout = tmpDir + '/' + refNS + '.abc'

            options = '-uvWrite -ro -worldSpace -writeCreases -writeUVSets -writeVisibility -dataFormat ogawa'

            command = '-frameRange ' + str(startFrame) + ' ' + str(endFrame) + ' ' + options
            command += ' -root ' + referenced_nodes[0]
            command += ' -file ' + tmpout
            print(command)
            cmds.AbcExport(v=True, j=command)

            #shutil.move(tmpout, abcPath)
    print('Done')

def getExportPath(scene_path):
    import os
    input_file_dir = scene_path

    cache_path = None
    for _ in range(20):  # Adjust the range to cover the maximum expected levels
        parent_dir = os.path.dirname(input_file_dir)
        cache_path = os.path.normpath(os.path.join(parent_dir, '50_EXPORT')).replace("\\", "/")
        if os.path.exists(cache_path):
            break
        input_file_dir = parent_dir

    if len(cache_path.split('/')) < 3:
        return None

    return cache_path


def find_referenced_nodes(selected_nodes):
    referenced_nodes = []
    for node in selected_nodes:
        hierNodes = list_hierarchy(node)
        for hierNode in hierNodes:
            if cmds.referenceQuery(hierNode, isNodeReferenced=True):
                reference = cmds.referenceQuery(hierNode, referenceNode=True, topReference=True)
                if reference and reference not in referenced_nodes:
                    referenced_nodes.append(reference)
    return referenced_nodes

def list_hierarchy(node):
    hierarchy = [node]
    allRel = cmds.listRelatives(node, ad=True, type='transform', f=True)
    for rel in allRel:
        hierarchy.append(rel)
    return hierarchy



