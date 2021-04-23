import sys
import time
import atomacos
import subprocess

bundleID = 'com.apple.logic10'
logic = None

def open(project):
    project_name = project.split('/')[-1].replace('.logicx', '')
    print(f'Opening {project_name}...')
    subprocess.call(['open', project])
    
    print('Activating Logic Pro X...')
    global logic
    logic = atomacos.getAppRefByBundleId(bundleID)
    logic.activate()
    
    print('Waiting for project to load...')
    while len([window for window in logic.windows() if project_name in window.AXTitle]) == 0:
        time.sleep(0.1)
    
    # Wait a bit extra for the window to load
    time.sleep(1)
    
    print('Closing any popups (in particular the one for not having the audio interface)...')
    for popup in [x for x in logic.windows() if x.AXRoleDescription == 'dialog']:
        popup.buttons('OK')[0].Press()

    print('Project opened')

def selectAllRegions():
    # Note that while selecting, we close the mixer (if open)
    print('Selecting all regions...')
    numChildren = len(logic.windows()[0].AXChildren)
    logic.activate()
    logic.sendGlobalKey('x')
    # If clicking x added another pane (i.e., the mixer), close it again!
    if len(logic.windows()[0].AXChildren) > numChildren:
        logic.sendGlobalKey('x')
    logic.sendGlobalKeyWithModifiers('a', ['command'])

    print('Regions selected')

def transpose(interval):
    print('Opening the inspector...')
    logic.activate()
    inspector = [x for x in logic.windows()[0].AXChildren if 'AXDescription' in x.getAttributes() and x.AXDescription == 'Inspector']
    if len(inspector) == 0:
        logic.sendGlobalKey('i')
        inspector = [x for x in logic.windows()[0].AXChildren if 'AXDescription' in x.getAttributes() and x.AXDescription == 'Inspector']

    print('Transposing the regions...')
    # This is far down the tree. Further than inspector.AXChildren[0].AXChildren[0].AXChildren[0].AXChildren[0].AXChildren [...]
    inspector[0].findFirstR(AXValue='Transpose:').AXParent.findFirst(AXRole='AXSlider').AXValue = interval

    print('Regions transposed')
    # sliderCoors = (transposeSlider.AXPosition.x + 1, transposeSlider.AXPosition.y + 1)
    # logic.doubleClickMouse(sliderCoors)
    # logic.sendKeys(f'{interval}\n') # Change to the amount of transposition

def bounce(filename, bounce_format = 'MP3'):
    # Adapted from https://gist.github.com/psobot/81635e6cbc933b7e8862
    print('Opening bounce window...')
    logic.activate()
    logic.sendGlobalKeyWithModifiers('b', ['command'])

    windows = [];
    while len(windows) == 0:
        time.sleep(0.1)
        windows = [window for window in logic.windows() if ('Output 1-2' in window.AXTitle) or ('Bounce' in window.AXTitle)]
    bounce_window = windows[0]

    print('Selecting output formats...')
    quality_table = bounce_window.findFirst(AXRole='AXScrollArea').findFirst(AXRole='AXTable')
    for row in quality_table.findAll(AXRole='AXRow'):
        row_name = row.findFirst(AXRole='AXTextField').AXValue
        checkbox = row.findFirst(AXRole='AXCheckBox')
        if row_name == bounce_format:
            if checkbox.AXValue is 0:
                print(f'Selecting {bounce_format} output format...')
                checkbox.Press()
            else:
                print(f'{bounce_format} format already selected.')
        elif checkbox.AXValue is 1:
            print(f'Deselecting {row_name} format...')

    print('Pressing bounce...')
    bounce_window.findFirst(AXRole='AXButton', AXTitle='OK').Press()

    print('Waiting for save window...')
    windows = []
    while len(windows) == 0:
        time.sleep(0.1)
        windows = [window for window in logic.windows() if ('Output 1-2' in window.AXTitle) or ('Bounce' in window.AXTitle)]
    save_window = windows[0]

    print('Entering filename...')
    save_window.findFirst(AXRole="AXTextField").AXValue = filename

    print('Pressing bounce on save window...')
    save_window.findFirst(AXRole="AXButton", AXTitle="Bounce").Press()

    # Deal with case where file already exists
    for popup in [window for window in logic.windows() if 'AXDescription' in window.getAttributes() and window.AXDescription == 'alert']:
        print('Overwriting previous file...')
        popup.findFirst(AXTitle='Replace').Press()

    print('Bouncing...')

    logic.activate() # Required for some reason
    while len(logic.windows()) > 1:
        time.sleep(0.1)
    time.sleep(2)

    print('File saved')

def close():
    print('Closing project...')
    logic.sendGlobalKeyWithModifiers('w', ['command'])

    print('Waiting for the save changes window...')
    windows = []
    for _ in range(20):
        time.sleep(0.1)
        windows = [window for window in logic.windows() if 'AXDescription' in window.getAttributes() and window.AXDescription == 'alert']
        if len(windows) > 0:
            break

    if len(windows) > 0:
        windows[0].buttons('Don’t Save')[0].Press()

    while len(logic.windows()) > 0:
        time.sleep(0.1)

    print('Project closed')
