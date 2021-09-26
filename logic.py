import sys
import time
import atomacos
import subprocess

bundleID = "com.apple.logic10"
logic = None


def open(project):
    project_name = project.split("/")[-1].replace(".logicx", "")
    print(f"Opening {project_name}...")
    subprocess.call(["open", project])

    print("Activating Logic Pro X...")
    global logic
    logic = atomacos.getAppRefByBundleId(bundleID)
    logic.activate()

    print("Waiting for project to load...")
    opening = True
    while opening:
        try:
            logic.windows()
            opening = False
        except Exception:
            opening = True

    while (
        len(
            [
                window
                for window in logic.windows()
                if "AXTitle" in window.getAttributes()
                and project_name in window.AXTitle
            ]
        )
        == 0
    ):
        time.sleep(0.1)

    # Wait a bit extra for the window to load
    time.sleep(1)

    print(
        "Closing any popups (in particular the one for not having the audio interface)..."
    )
    for popup in [x for x in logic.windows() if x.AXRoleDescription == "dialog"]:
        popup.buttons("OK")[0].Press()

    print("Project opened")


def __toggle_open__(key, should_open):
    num_children = len(logic.windows()[0].AXChildren)
    logic.activate()
    logic.sendGlobalKey(key)
    # If we're supposed to open and the number of panes decreased, reopen it
    new_num_children = len(logic.windows()[0].AXChildren)
    if (should_open and new_num_children < num_children) or (
        not should_open and new_num_children > num_children
    ):
        logic.sendGlobalKey(key)


def closeMixer():
    print("Closing mixer...")
    __toggle_open__("x", False)
    print("Mixer closed")


def closeLibrary():
    print("Closing library...")
    __toggle_open__("x", False)
    print("Library closed")


def selectAllRegions():
    closeMixer()
    # Note that while selecting, we close the mixer (if open)
    print("Selecting all regions...")
    logic.sendGlobalKeyWithModifiers("a", ["command"])
    print("Regions selected")


def transpose(interval):
    print("Opening the inspector...")
    logic.activate()

    inspectors = [
        x
        for x in logic.windows()[0].AXChildren
        if "AXDescription" in x.getAttributes()
        and x.findFirstR(AXValue="Transpose:") != None
    ]
    if len(inspectors) == 0:
        logic.sendGlobalKey("i")
        inspectors = [
            x
            for x in logic.windows()[0].AXChildren
            if "AXDescription" in x.getAttributes()
            and x.findFirstR(AXValue="Transpose:") != None
        ]

    print("Transposing the regions...")
    inspectors[0].findFirstR(AXValue="Transpose:").AXParent.findFirst(
        AXRole="AXSlider"
    ).AXValue = interval
    print("Regions transposed")


def bounce(filepath, bounce_format="MP3"):
    # Adapted from https://gist.github.com/psobot/81635e6cbc933b7e8862
    print("Opening bounce window...")
    logic.activate()
    time.sleep(0.1)  # To make sure the command works
    logic.sendGlobalKeyWithModifiers("b", ["command"])

    windows = []
    while len(windows) == 0:
        time.sleep(0.1)
        windows = [
            window
            for window in logic.windows()
            if ("Output 1-2" in window.AXTitle) or ("Bounce" in window.AXTitle)
        ]
    bounce_window = windows[0]

    print("Selecting output formats...")
    quality_table = bounce_window.findFirst(AXRole="AXScrollArea").findFirst(
        AXRole="AXTable"
    )
    for row in quality_table.findAll(AXRole="AXRow"):
        row_name = row.findFirst(AXRole="AXTextField").AXValue
        checkbox = row.findFirst(AXRole="AXCheckBox")
        if row_name == bounce_format:
            if checkbox.AXValue == 0:
                print(f"Selecting {bounce_format} output format...")
                checkbox.Press()
            else:
                print(f"{bounce_format} format already selected.")
        elif checkbox.AXValue == 1:
            print(f"Deselecting {row_name} format...")

    print("Pressing bounce...")
    bounce_window.findFirst(AXRole="AXButton", AXTitle="OK").Press()

    print("Waiting for save window...")
    windows = []
    while len(windows) == 0:
        time.sleep(0.1)
        windows = [
            window
            for window in logic.windows()
            if ("Output 1-2" in window.AXTitle) or ("Bounce" in window.AXTitle)
        ]
    save_window = windows[0]

    print("Entering file path...")
    logic.activate()
    logic.sendGlobalKeyWithModifiers("g", ["command", "shift"])
    logic.sendKeys(f"{filepath}\n")

    print("Waiting for file path window to close...")
    logic.activate()
    windows = []
    while len(windows) != 1:
        time.sleep(0.1)
        windows = [
            window
            for window in logic.windows()
            if ("Output 1-2" in window.AXTitle) or ("Bounce" in window.AXTitle)
        ]
    save_window = windows[0]

    print("Pressing bounce on save window...")
    try:
        save_window.buttons("Bounce")[0].Press()
    except atomacos.errors.AXErrorAttributeUnsupported as e:
        print(f"Error when clicking bounce: {str(e)}")

    time.sleep(0.1)

    # Deal with case where file already exists
    for dialog in [
        window for window in logic.windows() if window.AXRoleDescription == "dialog"
    ]:
        print("Overwriting previous file...")
        btns = dialog.AXChildren[-1].buttons("Replace")
        for btn in btns:
            btn.Press()
            time.sleep(0.1)
            # Deal with extra messages that could pop up
            dialogs = [
                window
                for window in logic.windows()
                if window.AXRoleDescription == "dialog"
            ]
            while len(dialogs) > 0:
                replace_btn = dialogs[0].buttons("Replace")
                if len(replace_btn) == 0:
                    break
                replace_btn[0].Press()
                time.sleep(0.1)
                dialogs = [
                    window
                    for window in logic.windows()
                    if window.AXRoleDescription == "dialog"
                ]

    print("Bouncing...")
    # time.sleep(2)

    logic.activate()  # Required for some reason
    still_going = True
    while still_going:
        try:
            still_going = len(logic.windows()) > 1
        except atomacos.errors.AXErrorInvalidUIElement:
            still_going = True
        time.sleep(0.1)

    print("File saved")


def close():
    print("Closing project...")
    logic.sendGlobalKeyWithModifiers("w", ["command"])

    print("Waiting for the save changes window...")
    windows = []
    for _ in range(20):
        time.sleep(0.1)
        windows = [
            window
            for window in logic.windows()
            if "AXDescription" in window.getAttributes()
            and window.AXDescription == "alert"
        ]
        if len(windows) > 0:
            break

    if len(windows) > 0:
        windows[0].buttons("Don’t Save")[0].Press()

    while len(logic.windows()) > 0:
        time.sleep(0.1)

    print("Project closed")


def importMidi(midiFile):
    print(midiFile)
    selectLastTrack()

    print("Opening up midi selection window...")
    logic.menuItem("File", "Import", "MIDI File…").Press()
    windows = []
    while len(windows) == 0:
        time.sleep(0.1)
        windows = [
            window
            for window in logic.windows()
            if "AXTitle" in window.getAttributes() and window.AXTitle == "Import"
        ]
    import_window = windows[0]

    print("Navigating to folder...")
    logic.activate()
    logic.sendGlobalKeyWithModifiers("g", ["command", "shift"])
    logic.sendKeys(midiFile)
    logic.sendKeys("\n")

    print("Pressing import...")
    time.sleep(0.1)
    import_window.buttons("Import")[0].Press()

    print("Waiting for tempo import message...")
    windows = []
    while len(windows) == 0:
        time.sleep(0.1)
        windows = [
            window
            for window in logic.windows()
            if "AXDescription" in window.getAttributes()
            and window.AXDescription == "alert"
        ]
    alert = windows[0]

    print("Importing tempo...")
    alert.buttons("Import Tempo")[0].Press()

    print("Midi file imported")


"""
old_instrument is the old instrument's name (like 'Sampler')
new_instrument_arr is an array like ['AU Instruments', 'Native Instruments', 'Kontakt', 'Stereo']
(it has the hierarchy of items to find in the menu).
"""


def selectInstrument(new_instrument_arr):
    print("Opening the appropriate window...")
    window = [
        window
        for window in logic.windows()
        if "AXTitle" in window.getAttributes() and "Tracks" in window.AXTitle
    ][0]

    print("Finding the instrument to change...")
    # It's at window.AXChildren[-2].AXChildren[0].AXChildren[-1].AXChildren[0].AXChildren[0]...
    # The one below could be used if we know the name of the instrument
    # strip = window.findFirstR(AXRoleDescription='channel strip group').findFirstR(AXDescription=old_instrument).AXChildren[-1]
    strip = (
        window.findFirstR(AXRoleDescription="channel strip group")
        .findAllR(AXDescription="open")[-1]
        .AXParent.AXChildren[-1]
    )

    # Manually click because Press() throws errors
    time.sleep(0.1)
    atomacos.mouse.click(x=strip.AXPosition.x + 1, y=strip.AXPosition.y + 1)

    print("Walking through the menu items...")
    menuitem = window
    for item in new_instrument_arr:
        if menuitem.AXChildren[0].AXRole == "AXMenu":
            menuitem = menuitem.AXChildren[0]
        menuitem = menuitem.findFirstR(AXRole="AXMenu*Item", AXTitle=item)
        while menuitem.AXPosition.x == 0:
            time.sleep(0.1)
        atomacos.mouse.moveTo(x=menuitem.AXPosition.x + 1, y=menuitem.AXPosition.y + 1)

    print("Clicking the instrument name...")
    atomacos.mouse.click(x=menuitem.AXPosition.x + 1, y=menuitem.AXPosition.y + 1)

    print("Waiting for the instrument screen...")
    windows = []
    i = 0
    while len(windows) < 1 and i < 20:
        time.sleep(0.1)
        i += 1
        windows = [
            window
            for window in logic.windows()
            if "AXTitle" not in window.getAttributes() or "Tracks" not in window.AXTitle
        ]

    if i >= 20:
        print("Failed to open instrument screen")
        raise Exception("Failed to open instrument screen")

    print("Closing the instrument screen...")
    for window in windows:
        window.AXChildren[0].Press()

    print("Done selecting instrument")


def selectPresetSound(sound):
    print("Opening the appropriate window...")
    window = [
        window
        for window in logic.windows()
        if "AXTitle" in window.getAttributes() and "Tracks" in window.AXTitle
    ][0]

    closeLibrary()
    strip = (
        window.findFirstR(AXRoleDescription="channel strip group")
        .findAllR(AXDescription="open")[-1]
        .AXParent.AXChildren[0]
    )
    print("Opening the presets for the instrument")
    atomacos.mouse.click(x=strip.AXPosition.x - 20, y=strip.AXPosition.y + 1)

    print("Waiting for search text field to appear...")
    fields = []
    while len(fields) == 0:
        time.sleep(0.1)
        try:
            fields = window.findAllR(
                AXRole="AXTextField", AXRoleDescription="search text field"
            )
        except Exception:
            print("Error finding search library field")
            fields = []
    search_field = fields[0]

    row = window.findFirstR(AXValue=sound)

    print("Double clicking the sound")
    logic.activate()
    atomacos.mouse.click(
        x=row.AXPosition.x + 30, y=row.AXPosition.y + 10, clicks=1, interval=0.1
    )
    time.sleep(0.05)
    atomacos.mouse.click(
        x=row.AXPosition.x + 30, y=row.AXPosition.y + 10, clicks=2, interval=0.01
    )


def selectLastTrack():
    closeMixer()

    print("Moving selection down by 5")
    logic.activate()
    for i in range(5):
        logic.sendGlobalKey("down")


def deleteLastTrack():
    selectLastTrack()

    print("Entering delete keyboard shortcut...")
    logic.sendGlobalKeyWithModifiers("del", ["command"])

    print("Confirming deletion...")
    windows = []
    while len(windows) == 0:
        time.sleep(0.1)
        windows = [x for x in logic.windows() if x.AXRoleDescription == "dialog"]
    delete_popup = windows[0]
    delete_popup.buttons("Delete")[0].Press()
