DEBUG = True


def tonic_create_dependent(tonic_node, outfile):
    import tonic_nodeUtil
    import maya.cmds as cmds
    import os

    if DEBUG:
        print('*** in tonic_create_dependent')

    #Load the appropriate plugin
    filetype = (os.path.splitext(outfile)[1])[1:]
    if filetype == 'fbx':
        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
            cmds.loadPlugin('fbxmaya')
    elif filetype == 'abc':
        if not cmds.pluginInfo('AbcExport', query=True, loaded=True):
            cmds.loadPlugin('AbcExport')

    # Check if the directory exists, if not, create it
    output_dir = os.path.dirname(outfile)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    #Get the shotgrid step
    if cmds.attributeQuery('tonicStepName', node=tonic_node, exists=True):
        sg_step = cmds.getAttr(tonic_node + '.tonicStepName')

    if 'odel' in sg_step:
        #Is a modelling task
        #Get the geo grp
        geo_grp = tonic_nodeUtil.tonic_get_tonicNode_subGroup(tonic_node, 'tonicIsGEO_GRP')
        if DEBUG:
            print('### geo_grp')
            print(geo_grp)

        if geo_grp:
            if filetype == 'fbx':
                cmds.select(geo_grp)
                cmds.file(outfile, force=True, options="v = 0", type="FBX export", exportSelected=True)
                if os.path.isfile(outfile):
                    #Export worked
                    return outfile

            elif filetype == 'abc':
                command = '-dataFormat ogawa -attrPrefix tonic -writeVisibility -uvWrite -worldSpace -root %s -file %s' % (geo_grp[0], outfile)
                if DEBUG:
                    print('### abc export command')
                    print(command)
                cmds.AbcExport(j=command)
                if os.path.isfile(outfile):
                    # Export worked
                    return outfile

    return None

