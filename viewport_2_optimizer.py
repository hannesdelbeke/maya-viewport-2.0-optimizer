import sys
import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel


# this plugin menu setup creates a single menu entry
# to create a menu under Windows/my-tool

# The below sample will create a new menu and menu-item: ToolsMenu/My cool tool
# MENU_NAME is the name maya assigns to a menu, this is not always the same as the visible label
# e.g. to parent to the default Maya menu 'Windows', use MENU_NAME="mainWindowMenu"
MENU_NAME = "mainDisplayMenu"  # no spaces in names, use CamelCase. Used to find and parent to a menu.
# MENU_LABEL = "Display"  # spaces are allowed in labels, only used when we create a new menu
MENU_ENABLE_LABEL = "Optimize Viewport 2.0"
MENU_DISABLE_LABEL = "Reset Viewport 2.0"

MENU_PARENT = "MayaWindow"  # do not change

# Store generated menu items, used when unregister
__menu_entry_name1 = ""
__menu_entry_name2 = ""


def maya_useNewAPI():  # noqa
    """dummy method to tell Maya this plugin uses the Maya Python API 2.0"""
    pass


def optimize_viewport(*args, **kwargs):
    # Performance
    cmds.setAttr("hardwareRenderingGlobals.maxHardwareLights", 1)
    cmds.setAttr("hardwareRenderingGlobals.transparencyAlgorithm", 0)

    cmds.setAttr("hardwareRenderingGlobals.enableTextureMaxRes", 1)
    cmds.setAttr("hardwareRenderingGlobals.textureMaxResMode", 1)
    cmds.setAttr("hardwareRenderingGlobals.textureMaxResolution", 256)
    mel.eval("source AEhardwareRenderingGlobalsTemplate;")
    mel.eval("AEReloadAllTextures;")

    cmds.setAttr("hardwareRenderingGlobals.colorBakeResolution", 16)
    cmds.setAttr("hardwareRenderingGlobals.bumpBakeResolution", 16)

    # Ambient Occlusion
    cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 0)
    cmds.setAttr("hardwareRenderingGlobals.ssaoSamples", 8)

    # Motion Blur
    cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable", 0)
    cmds.setAttr("hardwareRenderingGlobals.motionBlurSampleCount", 4)

    # Anti Aliasing
    cmds.setAttr("hardwareRenderingGlobals.lineAAEnable", 0)
    cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 0)

    # May result in banding but has a big impact on speed
    cmds.setAttr("hardwareRenderingGlobals.floatingPointRTEnable", 0)

    # Animation caching
    cmds.setAttr("hardwareRenderingGlobals.vertexAnimationCache", 2)

    # Optimise SkinClusters
    for skin_cluster in cmds.ls(type='skinCluster', l=True):
        cmds.setAttr(skin_cluster + ".deformUserNormals", 0)

    cmds.confirmDialog(title="Viewport Optimisation", message="Optimisation Complete")


def reset_viewport(*args, **kwargs):
    # Reset performance settings to original values
    cmds.setAttr("hardwareRenderingGlobals.maxHardwareLights", 8)
    cmds.setAttr("hardwareRenderingGlobals.transparencyAlgorithm", 1)

    cmds.setAttr("hardwareRenderingGlobals.enableTextureMaxRes", 1)
    cmds.setAttr("hardwareRenderingGlobals.textureMaxResMode", 0)
    cmds.setAttr("hardwareRenderingGlobals.textureMaxResolution", 2048)
    mel.eval("source AEhardwareRenderingGlobalsTemplate;")
    mel.eval("AEReloadAllTextures;")

    cmds.setAttr("hardwareRenderingGlobals.colorBakeResolution", 64)
    cmds.setAttr("hardwareRenderingGlobals.bumpBakeResolution", 64)

    # Reset Ambient Occlusion
    cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 0)
    cmds.setAttr("hardwareRenderingGlobals.ssaoSamples", 16)

    # Reset Motion Blur
    cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable", 0)
    cmds.setAttr("hardwareRenderingGlobals.motionBlurSampleCount", 8)

    # Reset Anti Aliasing
    cmds.setAttr("hardwareRenderingGlobals.lineAAEnable", 0)
    cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 0)

    # Reset floating point render target
    cmds.setAttr("hardwareRenderingGlobals.floatingPointRTEnable", 1)

    # Reset Animation caching
    cmds.setAttr("hardwareRenderingGlobals.vertexAnimationCache", 0)

    # Reset SkinClusters
    for skin_cluster in cmds.ls(type='skinCluster', l=True):
        cmds.setAttr(skin_cluster + ".deformUserNormals", 1)  # Assuming reset to 1 for deformUserNormals

    cmds.confirmDialog(title="Viewport Reset", message="Viewport settings reset to default values")


def loadMenu():
    """Setup the Maya menu, runs on plugin enable"""
    global __menu_entry_name1
    global __menu_entry_name2

    # Maya builds its menus dynamically upon being accessed, so they don't exist if not yet accessed.
    # We force a menu build to allow parenting any new menu under a default Maya menu
    mel.eval("evalDeferred buildFileMenu")  # delete this if not parenting menus to a default Maya Menu

    # if not cmds.menu(f"{MENU_PARENT}|{MENU_NAME}", exists=True):
    #     cmds.menu(MENU_NAME, label=MENU_LABEL, parent=MENU_PARENT)
    __menu_entry_name1 = cmds.menuItem(label=MENU_ENABLE_LABEL, command=optimize_viewport, parent=MENU_NAME)
    __menu_entry_name2 = cmds.menuItem(label=MENU_DISABLE_LABEL, command=reset_viewport, parent=MENU_NAME)


def unloadMenuItem():
    """Remove the created Maya menu entry, runs on plugin disable"""
    if cmds.menu(f"{MENU_PARENT}|{MENU_NAME}", exists=True):
        menu_long_name = f"{MENU_PARENT}|{MENU_NAME}"
        # Check if the menu item exists; if it does, delete it
        if cmds.menuItem(__menu_entry_name1, exists=True):
            cmds.deleteUI(__menu_entry_name1, menuItem=True)
        if cmds.menuItem(__menu_entry_name2, exists=True):
            cmds.deleteUI(__menu_entry_name2, menuItem=True)
        # Check if the menu is now empty; if it is, delete the menu
        if not cmds.menu(menu_long_name, query=True, itemArray=True):
            cmds.deleteUI(menu_long_name, menu=True)


# =============================== Plugin (un)load ===========================================
def initializePlugin(plugin):
    """Code to run when the Maya plugin is enabled, this can be manual or during Maya startup"""
    # register_command(plugin)
    loadMenu()


def uninitializePlugin(plugin):
    """Code to run when the Maya plugin is disabled."""
    # to allow the user to enable and disable your plugin on the fly without any issues
    # anything created or setup during initializePlugin should be cleaned up in this method.
    # however if you don't, a user can instead disable the plugin & then restart Maya.

    # unregister_command(plugin)
    unloadMenuItem()
    
