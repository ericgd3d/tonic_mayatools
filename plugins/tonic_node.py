import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender

nodeTypeName = "tonicNode"
nodeTypeId = OpenMaya.MTypeId(0x87922)

glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()

class myNode(OpenMayaMPx.MPxLocatorNode):
    def __init__(self):
        OpenMayaMPx.MPxLocatorNode.__init__(self)

    def draw(self, view, path, style, status):
        view.beginGL()

        glFT.glBegin(OpenMayaRender.MGL_LINES)
        glFT.glVertex3f(0.0, -0.5, 0.0)
        glFT.glVertex3f(0.0, 0.5, 0.0)
        glFT.glEnd()

        view.endGL()


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(myNode())


def nodeInitializer():
    #return OpenMaya.MStatusCode.kSuccess
    return

def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, "EricGD", "1.0", "Any")
    try:
        plugin.registerNode(nodeTypeName, nodeTypeId, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kLocatorNode)
    except:
        sys.stderr.write("Failed to register node: %s" % nodeTypeName)


def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(nodeTypeId)
    except:
        sys.stderr.write("Failed to deregister node: %s" % nodeTypeName)