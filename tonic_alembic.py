import shutil
import os
import maya.cmds as cmds
import tempfile
import ctypes

DEBUG = True
def ton_legacy_export_sel_abc(full_temp_dir=None):
    #An alembic exporter for legacy scenes

    print('Exporting Abc')

    scene_path = cmds.file(query=True, sceneName=True)

    print(scene_path)
    file_name = os.path.basename(scene_path)  # Get the base name with extension
    file_name_without_extension = os.path.splitext(file_name)[0]  # Remove the extension

    print(file_name_without_extension)



    temp_dir = tempfile.gettempdir()
    full_temp_dir = ctypes.create_unicode_buffer(512)
    ctypes.windll.kernel32.GetLongPathNameW(temp_dir, full_temp_dir, ctypes.sizeof(full_temp_dir))

    tmpDir = (full_temp_dir.value).replace("\\", "/")


    abcExportPathDir = getExportPath(scene_path) + '/' + file_name_without_extension

    startFrame = cmds.playbackOptions(query=True, min=True)
    endFrame = cmds.playbackOptions(query=True, max=True)

    selNodes = cmds.ls(sl=True, l=True)
    allSelReferenceNodes = find_referenced_nodes(selNodes)

    if allSelReferenceNodes:
        for refNode in allSelReferenceNodes:
            referenced_nodes = cmds.referenceQuery(refNode, nodes=True)

            if referenced_nodes:

                nodeToExport = referenced_nodes[0]
                for currRefNode in referenced_nodes:
                    if currRefNode.endswith(':renderGeo_grp'):
                        nodeToExport = currRefNode

                #Add currscene attr to root node
                cmds.addAttr(nodeToExport, ln="source", dt="string")
                cmds.setAttr(nodeToExport + ".source", scene_path, type="string")

                refNS = cmds.referenceQuery(refNode, namespace=True)[1:]

                abcPath = abcExportPathDir + '/' + refNS + '.abc'
                tmpout = tmpDir + '/' + refNS + '.abc'

                options = '-attr source -uvWrite -ro -worldSpace -writeCreases -writeUVSets -writeVisibility -dataFormat ogawa'

                command = '-frameRange ' + str(startFrame) + ' ' + str(endFrame) + ' ' + options
                command += ' -root ' + nodeToExport
                command += ' -file ' + tmpout
                print(command)

                cmds.AbcExport(v=True, j=command)

                #Delete the extra attribute
                cmds.deleteAttr(nodeToExport, attribute='source')

                print('Saving ' + abcPath)
                if not os.path.exists(abcExportPathDir):
                    os.makedirs(abcExportPathDir)
                shutil.move(tmpout, abcPath)
    else:
        for node in selNodes:
            nodeToExport = node
            allDesc = list_hierarchy(node)
            for currRefNode in allDesc:
                if currRefNode.endswith(':renderGeo_grp'):
                    nodeToExport = currRefNode

            # Add currscene attr to root node
            cmds.addAttr(nodeToExport, ln="source", dt="string")
            cmds.setAttr(nodeToExport + ".source", scene_path, type="string")

            refNS = node.split(':')[0].lstrip('|')

            abcPath = abcExportPathDir + '/' + refNS + '.abc'
            tmpout = tmpDir + '/' + refNS + '.abc'

            options = '-attr source -uvWrite -ro -worldSpace -writeCreases -writeUVSets -writeVisibility -dataFormat ogawa'

            command = '-frameRange ' + str(startFrame) + ' ' + str(endFrame) + ' ' + options
            command += ' -root ' + nodeToExport
            command += ' -file ' + tmpout
            print(command)

            cmds.AbcExport(v=True, j=command)

            # Delete the extra attribute
            cmds.deleteAttr(nodeToExport, attribute='source')

            print('Saving ' + abcPath)
            if not os.path.exists(abcExportPathDir):
                os.makedirs(abcExportPathDir)
            shutil.move(tmpout, abcPath)

    print('Done')
7
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



