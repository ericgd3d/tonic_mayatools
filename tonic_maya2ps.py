import maya.cmds as cmds


def build_model_list():

    all_assets = []
    all_meshes = cmds.ls(type='mesh', l=True)

    for mesh in all_meshes:
        mesh_transform = cmds.listRelatives(mesh, p=True, f=True)
        print(mesh_transform)


def create_layer_attr_on_all_transforms():

    all_transform_nodes = cmds.ls(type='transform', l=True)
    for transform_node in all_transform_nodes:
        if not cmds.attributeQuery('psLayer', node=transform_node, exists=True):
            cmds.addAttr(transform_node, ln="psLayer", attributeType='bool')
        cmds.setAttr(transform_node + ".psLayer", False)


def tonic_maya2ps():
    print(tonic_maya2ps)
    create_layer_attr_on_all_transforms()
