import os
import sg_utils
def tonic_create_tonic_node_for_task_id(task_id):
    import maya.cmds as cmds

    server = os.environ["TONIC_SERVER"]
    if server:
        sg = sg_utils.get_sg(server)

        task_dict = sg_utils.get_task_from_id(sg, task_id)
        tonic_createTonicNode(task_dict)


def tonic_createTonicNode(d):
    import maya.cmds as cmds
    import tonic_translator

    nodeTaskName = d['entity']['name'] + '_' + d['step']['name'] + '_' + tonic_translator.tonic_clean_special_characters(d['content'])

    if d['entity']['type'] == 'Shot':
        nodeTaskName = 'shot_' + nodeTaskName

    if not cmds.pluginInfo('tonic_node', query=True, loaded=True):
        cmds.loadPlugin('tonic_node')

    origNN = cmds.createNode('tonicNode', n=nodeTaskName+'Shape')
    origNNt = cmds.listRelatives(origNN, p=True, f=True)

    tonic_createCustomAttr(origNN, d)

    attr_to_lock = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']

    if d['entity']['type'] == 'Asset':
        group_names = ["GEO_GRP", "RIG_GRP", "CTR_GRP", "DATA_GRP"]
        group_nodes = []

        for name in group_names:
            group_node = cmds.group(empty=True, name=name)
            group_nodes.append(group_node)

        # Add attributes to the groups
        for group_node, group_name in zip(group_nodes, group_names):
            # Add a boolean attribute to represent if the group is of this type
            attribute_name = "tonicIs" + group_name
            cmds.addAttr(group_node, longName=attribute_name, attributeType="bool")
            cmds.setAttr(f"{group_node}.{attribute_name}", True)

            for attr in attr_to_lock:
                cmds.setAttr(group_node + '.' + attr, lock=True)

            tonic_createCustomAttr(group_node, d)

            cmds.parent(group_node, origNNt)


        # Create cameras
        allAssetCams = tonic_createAssetCameras(d, nodeTaskName)
        camGrp = cmds.group(allAssetCams, n='CAMERA_GRP', p=origNNt[0])
        cmds.addAttr(camGrp, longName='tonicIsCAMERA_GRP', attributeType="bool")
        cmds.setAttr(camGrp+'.tonicIsCAMERA_GRP', True)
        for attr in attr_to_lock:
            cmds.setAttr(camGrp + '.' + attr, lock=True)

        #Lock all groups inside
        all_grp_nodes = cmds.listRelatives(origNNt, c=True, f=True )
        for grp in all_grp_nodes:
            cmds.lockNode(grp, lock=True)

        cmds.lockNode(origNNt, lock=True)

    return origNN



def tonic_createAssetCameras(d, camBasename):
    import maya.cmds as cmds
    allCams = []

    for i in range(3):  #Do 3 cams
        newCam = cmds.camera(horizontalFilmAperture=1, verticalFilmAperture=1, displayFilmGate=True, displayGateMask=True)
        tonic_createCustomAttr(newCam[1], d, assetCam=i+1)
        camRenamed = cmds.rename(newCam[0], camBasename+'_camera'+str(i+1))
        allCams.append(camRenamed)
    return allCams

def tonic_createCustomAttr(nn ,d, assetCam=0):
    import maya.cmds as cmds
    tonicAttrDict = {}

    tonicAttrDict['tonicProjectName'] = d['project']['name']
    tonicAttrDict['tonicProjectId'] = d['project']['id']
    tonicAttrDict['tonicEntityType'] = d['entity']['type']
    tonicAttrDict['tonicEntityId'] = d['entity']['id']
    tonicAttrDict['tonicEntityName'] = d['entity']['name']
    tonicAttrDict['tonicStepName'] = d['step']['name']
    tonicAttrDict['tonicTaskName'] = d['content']
    tonicAttrDict['tonicTaskId'] = d['id']

    if d['entity']['type'] == 'Asset':
        tonicAttrDict['tonicAssetType'] = d['entity.Asset.sg_asset_type']
        tonicAttrDict['tonicShotType'] = ''
    elif d['entity']['type'] == 'Shot':
        tonicAttrDict['tonicAssetType'] = ''
        tonicAttrDict['tonicShotType'] = d['entity.Shot.sg_shot_type']
    else:
        tonicAttrDict['tonicAssetType'] = ''
        tonicAttrDict['tonicShotType'] = ''

    if assetCam:
        tonicAttrDict['tonicIsAssetCam'] = str(assetCam)

    for a in sorted(tonicAttrDict):
        if tonicAttrDict[a]:
            if cmds.attributeQuery(a, node=nn, exists=True):
                cmds.setAttr('%s.%s' % (nn, a), lock=False)
            else:
                cmds.addAttr(nn, ln=a, dt='string')
            cmds.setAttr(nn + '.' + a, tonicAttrDict[a], type='string')

def tonic_get_all_tonic_nodes():
    import maya.cmds as cmds
    all_tonic_nodes = cmds.ls(type='tonicNode', l=True)
    return all_tonic_nodes

def tonic_get_current_sgtask(sg):
    import maya.cmds as cmds

    all_tonic_nodes = tonic_get_all_tonic_nodes()
    for tonic_node in all_tonic_nodes:
        task_id = int(cmds.getAttr(tonic_node + '.tonicTaskId'))
        task_dict = sg_utils.get_task_from_id(sg, task_id)
        return task_dict
    return None

def tonic_get_tonicNode_subGroup(tonic_node, grp):
    import maya.cmds as cmds
    all_with_grp = []
    tonic_node_transform = cmds.listRelatives(tonic_node, p=True, f=True)
    all_descendants = cmds.listRelatives(tonic_node_transform, type='transform', ad=True, f=True)
    for desc in all_descendants:
        #print(desc)
        if cmds.attributeQuery(grp, node=desc, exists=True):
            all_with_grp.append(desc)
    return all_with_grp


