DEBUG = True

def tonic_mayaModel_to_fbx(out_fbx):
    import tonic_nodeUtil
    import maya.cmds as cmds
    import os

    if DEBUG:
        print('*** in tonic_mayaModel_to_fbx')

    if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
        cmds.loadPlugin('fbxmaya')

    all_tonic_nodes  = tonic_nodeUtil.tonic_get_all_tonic_nodes()
    if DEBUG:
        print('### all_tonic_nodes')
        print(all_tonic_nodes)

    if all_tonic_nodes:
        geo_grp = tonic_nodeUtil.tonic_get_tonicNode_subGroup(all_tonic_nodes[0], 'tonicIsGEO_GRP')
        if DEBUG:
            print('### geo_grp')
            print(geo_grp)

        if geo_grp:

            output_dir = os.path.dirname(out_fbx)
            # Check if the directory exists, if not, create it
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            cmds.select(geo_grp)
            cmds.file(out_fbx, force=True, options="v = 0", type="FBX export", exportSelected=True)

            if DEBUG:
                print('### output')
                print(out_fbx)


def tonic_mayaModel_to_abc(out_abc):
    import tonic_nodeUtil
    import maya.cmds as cmds
    import os

    if DEBUG:
        print('*** in tonic_mayaModel_to_abc')

    if not cmds.pluginInfo('AbcExport', query=True, loaded=True):
        cmds.loadPlugin('AbcExport')

    all_tonic_nodes  = tonic_nodeUtil.tonic_get_all_tonic_nodes()
    if DEBUG:
        print('### all_tonic_nodes')
        print(all_tonic_nodes)

    if all_tonic_nodes:
        geo_grp = tonic_nodeUtil.tonic_get_tonicNode_subGroup(all_tonic_nodes[0], 'tonicIsGEO_GRP')
        if DEBUG:
            print('### geo_grp')
            print(geo_grp)

        if geo_grp:

            output_dir = os.path.dirname(out_abc)
            # Check if the directory exists, if not, create it
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            #cmds.select(geo_grp)

            command = '-dataFormat ogawa -attrPrefix tonic -writeVisibility -uvWrite -worldSpace -root %s -file %s' % ( geo_grp[0], out_abc)
            if DEBUG:
                print('### abc export command')
                print(command)
            cmds.AbcExport(j=command)

            if DEBUG:
                print('### output')
                print(out_abc)
