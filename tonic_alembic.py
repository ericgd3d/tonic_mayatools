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

    all_locked_vis_node = get_all_node_with_locked_vis()


    if allSelReferenceNodes:
        for refNode in allSelReferenceNodes:
            referenced_nodes = cmds.referenceQuery(refNode, nodes=True)

            if referenced_nodes:

                nodes_we_unlocked = []

                nodeToExport = referenced_nodes[0]
                for currRefNode in referenced_nodes:
                    if currRefNode.endswith(':renderGeo_grp'):
                        nodeToExport = currRefNode

                # Temporary hide visible non meshes for the export
                all_non_mesh_shapes = get_all_non_mesh_shape_descendant(nodeToExport)
                for non_mesh_shape in all_non_mesh_shapes:
                    if non_mesh_shape in all_locked_vis_node:
                        #Unlock it first
                        cmds.setAttr(non_mesh_shape+'.visibility',lock=False)
                        nodes_we_unlocked.append(non_mesh_shape)
                    cmds.setAttr(non_mesh_shape+'.visibility', 0)

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

                #Restore visibility of non mesh shapes
                for non_mesh_shape in all_non_mesh_shapes:
                    cmds.setAttr(non_mesh_shape+'.visibility', 1)

                # Restore locked visibility of non mesh shapes
                for unlocked_vis_node in nodes_we_unlocked:
                    cmds.setAttr(unlocked_vis_node + '.visibility', lock=True)

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

            nodes_we_unlocked = []

            # Temporary hide visible non meshes for the export
            all_non_mesh_shapes = get_all_non_mesh_shape_descendant(nodeToExport)
            for non_mesh_shape in all_non_mesh_shapes:
                if non_mesh_shape in all_locked_vis_node:
                    # Unlock it first
                    cmds.setAttr(non_mesh_shape + '.visibility', lock=False)
                    nodes_we_unlocked.append(non_mesh_shape)
                cmds.setAttr(non_mesh_shape + '.visibility', 0)

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

            # Restore visibility of non mesh shapes
            for non_mesh_shape in all_non_mesh_shapes:
                cmds.setAttr(non_mesh_shape + '.visibility', 1)

            # Restore locked visibility of non mesh shapes
            for unlocked_vis_node in nodes_we_unlocked:
                cmds.setAttr(unlocked_vis_node + '.visibility', lock=True)

            print('Saving ' + abcPath)
            if not os.path.exists(abcExportPathDir):
                os.makedirs(abcExportPathDir)
            shutil.move(tmpout, abcPath)

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

def get_all_non_mesh_shape_descendant(node):

    allRelWithShapes = cmds.listRelatives(node, ad=True, f=True)
    non_mesh = []
    for rel in allRelWithShapes:
        curr_visibility = cmds.getAttr(rel+'.visibility')
        if curr_visibility:
            objType = cmds.objectType(rel)
            if objType != 'transform' and objType != 'mesh' and objType != 'camera':
                non_mesh.append(rel)

    return non_mesh


def get_all_node_with_locked_vis():
    all_locked_visibility_nodes = []
    all_nodes = cmds.ls(l=True)
    for n in all_nodes:
        if cmds.attributeQuery('visibility', node=n, exists=True):
            if cmds.getAttr(n+'.visibility', lock=True):
                all_locked_visibility_nodes.append(n)
    return all_locked_visibility_nodes
