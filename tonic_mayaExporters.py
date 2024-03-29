import shutil

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
    elif filetype == 'usd':
        if not cmds.pluginInfo('mayaUsdPlugin', query=True, loaded=True):
            cmds.loadPlugin('mayaUsdPlugin')

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
                cmds.select(geo_grp, replace=True)
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

            elif filetype == 'usd':
                cmds.select(geo_grp, replace=True)

                # Set the frame range to the current frame
                current_frame = cmds.currentTime(query=True)
                options = ";exportUVs=1;exportSkels=none;exportSkin=none;exportBlendShapes=0;exportColorSets=1;defaultMeshScheme=catmullClark;defaultUSDFormat=usdc;animation=0;eulerFilter=0;staticSingleSample=0;startTime=1;endTime=1;frameStride=1;frameSample=0.0;parentScope=;exportDisplayColor=0;shadingMode=useRegistry;convertMaterialsTo=UsdPreviewSurface;exportInstances=1;exportVisibility=1;mergeTransformAndShape=0;stripNamespaces=1"

                #Creating a temp file for export since it seems to have difficulties saving on QSync directly
                import tempfile
                tmpDir = tempfile.gettempdir()
                tmp_outfile = tmpDir + '/' + os.path.basename(outfile)
                cmds.file(
                    tmp_outfile, force=True, exportSelected=True, preserveReferences=True, type='USD Export',
                    options=options
                )

                if os.path.isfile(tmp_outfile):
                    # Export worked
                    shutil.move(tmp_outfile, outfile)
                    return outfile

    return None

