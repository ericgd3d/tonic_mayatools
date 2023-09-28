import sys
DO_IT = True

def ton_build_dict_of_textures():
    import maya.cmds as cmds

    out_dict = {}
    all_file_nodes = cmds.ls(type='file', l=True)
    if all_file_nodes:
        for file_node in all_file_nodes:
            filenode_dict = {}
            texture_path = cmds.getAttr(file_node+'.fileTextureName')
            filenode_dict['texture_path'] = texture_path

            color_space = cmds.getAttr(file_node+'.colorSpace')
            filenode_dict['colorSpace'] = color_space

            out_dict[file_node] = filenode_dict
    return out_dict

def ton_execute_file_conversion(options):
    import subprocess

    command = 'C:/ProgramData/redshift/bin/redshiftTextureProcessor.exe'

    # Construct the full command line
    #full_command = [command, options, '&']
    full_command = [command]
    for single_option in options:
        full_command.append(single_option)
    full_command.append('&')
    #print(full_command)

    # Execute the shell command without affecting Maya's display
    if DO_IT:
        try:
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide the console window
            )
            process.communicate()  # Wait for the process to finish
        except Exception as e:
            print("Error executing the shell command:", str(e))


def create_pb_window():
    import maya.cmds as cmds
    window_name = "TextureConversionWindow"

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title="RsTexBin Texture Conversion")
    cmds.columnLayout(adjustableColumn=True)

    # Add a label to display the current file
    cmds.text(label="\n")
    label_converting = cmds.text(label="Converting")
    label_filename = cmds.text(label="Filename")
    cmds.text(label="\n")
    progress_control = cmds.progressBar(maxValue=100, width=375)

    # Show the UI window
    cmds.showWindow(window_name)

    return label_converting, label_filename, progress_control


def close_pb_window():
    import maya.cmds as cmds
    window_name = "TextureConversionWindow"

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)


# Function to replace the extension of a file
def replace_extension(file_path, new_extension):
    import os
    # Get the file's base name (name without path)
    base_name = os.path.basename(file_path)

    # Remove the current extension
    root_name, _ = os.path.splitext(base_name)

    # Combine the root name and the new extension
    new_file_name = root_name + new_extension

    # Create the new file path by joining the original directory path and the new file name
    new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)

    return new_file_path


def last_word_key(s):
    words = s.split()
    return words[-1]
def ngs_convertSelFileNodeTextureToRedshiftTexture():
    import maya.cmds as cmds
    import os
    import glob
    import subprocess
    import time

    rsTextureConverter = r'C:\ProgramData\redshift\bin\redshiftTextureProcessor.exe'

    all_file_nodes = cmds.ls(type='file', l=True)

    textureList = []

    if all_file_nodes:
        for file_node in all_file_nodes:
            bitmapFile = cmds.getAttr(file_node + '.fileTextureName')
            colorSpace = cmds.getAttr(file_node + '.colorSpace')

            colorSpaceOption = ' -l '
            if colorSpace == 'sRGB':
                colorSpaceOption = ' -s '



            if os.path.exists(bitmapFile):
                baseName = os.path.basename(bitmapFile)
                dirName = os.path.dirname(bitmapFile)

                baseNameNoExt = os.path.splitext(baseName)[0]
                extension = os.path.splitext(baseName)[1]
                splitBaseName = baseNameNoExt.split('.')
                if len(splitBaseName) > 1 and splitBaseName[len(splitBaseName) - 1].isdigit():
                    globPath = dirName + '/' + baseName.replace(splitBaseName[len(splitBaseName) - 1], '*')
                    allSiblingsTexture = glob.glob(globPath)
                    for st in allSiblingsTexture:
                        textureList.append(colorSpaceOption + ' ' + st)
                elif '_u' in baseNameNoExt and '_v' in baseNameNoExt:
                    # Is Udim
                    uIndex = baseNameNoExt.rfind('_u')
                    globPath = dirName + '/' + baseNameNoExt[:uIndex] + '_u*' + extension
                    allSiblingsTexture = glob.glob(globPath)
                    for st in allSiblingsTexture:
                        textureList.append(colorSpaceOption + ' ' + st)
                else:
                    # No Udim
                    textureList.append(colorSpaceOption + ' ' + bitmapFile)

    if textureList:
        allTextureFiles = sorted(textureList, key=last_word_key)

        num_files = len(allTextureFiles)
        id = 1

        label_converting, label_filename, progress_control = create_pb_window()

        for tf in allTextureFiles:

            converting_nb = 'Converting ' + str(id) + ' of ' + str(num_files)
            split_tf = tf.split()
            file_name_orig = split_tf[len(split_tf)-1]

            info_txt = (converting_nb + ': ' + file_name_orig)
            print(info_txt)

            # Update the progress bar
            cmds.text(label_converting, edit=True, label=converting_nb)
            cmds.text(label_filename, edit=True, label=file_name_orig)
            cmds.progressBar(progress_control, edit=True, progress=((id-1)/num_files * 100))
            cmds.refresh()

            #file_name_rstexbin = replace_extension(file_name_orig, '.rstexbin')
            #if not os.path.isfile(file_name_rstexbin):
            # Perform your texture conversion here
            ton_execute_file_conversion(tf.split())

            id += 1

        close_pb_window()
        print('Done converting. OMG! It\'s gonna be soooo fast now!!!')

    else:
        print("No textures to convert.")



