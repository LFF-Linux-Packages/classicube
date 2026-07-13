#!/usr/bin/env python3
import os
import subprocess
import pathlib
import urllib.request

# Source setup directory structure mapping paths
GAME_DIR = pathlib.Path(__file__).parent.resolve()
ICON_FILE = GAME_DIR / "CCicon.png"

# Target system paths matching config.txt registration for complete lpm uninstallation tracking
SYS_GAME_DIR = pathlib.Path("/opt/classicube")
SYS_BINARY = pathlib.Path("/usr/bin/classicube")
SYS_ICON = pathlib.Path("/usr/share/pixmaps/classicube.png")
SYS_DESKTOP = pathlib.Path("/usr/share/applications/classicube.desktop")

print("Executing system-wide asset deployment for ClassiCube...")

# 1. Ensure the icon exists locally in source context
if not ICON_FILE.exists():
    print(f"Icon file not found locally. Downloading asset...")
    url = "https://raw.githubusercontent.com/ClassiCube/classicube/master/misc/CCicon.png"
    try:
        urllib.request.urlretrieve(url, ICON_FILE)
    except Exception as e:
        print(f"Warning: Could not fetch icon: {e}")

# 2. Build deployment target directories using elevated permissions
subprocess.run(["sudo", "mkdir", "-p", str(SYS_GAME_DIR)], check=True)

# 3. Copy game resource files safely to systemic destination
# Using standard cp -r logic, filtering out the created venv folder to stay light
print(f"Copying files to {SYS_GAME_DIR}...")
for item in GAME_DIR.iterdir():
    if item.name == "venv":
        continue
    subprocess.run(["sudo", "cp", "-r", str(item), str(SYS_GAME_DIR / item.name)], check=True)

# 4. Enforce structural execution flags on the compiled game engine binary
EXEC_BINARY = SYS_GAME_DIR / "ClassiCube"
if EXEC_BINARY.exists():
    subprocess.run(["sudo", "chmod", "+x", str(EXEC_BINARY)], check=True)

# 5. Handle global desktop icon mappings
if ICON_FILE.exists():
    subprocess.run(["sudo", "cp", str(ICON_FILE), str(SYS_ICON)], check=True)

# 6. Generate the execution script wrapper inside /usr/bin/ to execute contextually
wrapper_script_content = f"""#!/bin/bash
cd {SYS_GAME_DIR}
exec ./ClassiCube "$@"
"""
tmp_wrapper = GAME_DIR / "classicube_wrapper.tmp"
with open(tmp_wrapper, "w") as w:
    w.write(wrapper_script_content)

subprocess.run(["sudo", "mv", str(tmp_wrapper), str(SYS_BINARY)], check=True)
subprocess.run(["sudo", "chmod", "+x", str(SYS_BINARY)], check=True)

# 7. Generate global unified menu shortcuts
desktop_entry_content = f"""[Desktop Entry]
Type=Application
Comment=Minecraft Classic inspired sandbox game
Name=ClassiCube
Exec={SYS_BINARY}
Icon={SYS_ICON}
Path={SYS_GAME_DIR}
Terminal=false
Categories=Game;
Actions=singleplayer;resume;

[Desktop Action singleplayer]
Name=Start singleplayer
Exec={SYS_BINARY} --singleplayer

[Desktop Action resume]
Name=Resume last server
Exec={SYS_BINARY} --resume
"""

tmp_desktop = GAME_DIR / "classicube_desktop.tmp"
with open(tmp_desktop, "w") as d:
    d.write(desktop_entry_content)

subprocess.run(["sudo", "mv", str(tmp_desktop), str(SYS_DESKTOP)], check=True)
subprocess.run(["sudo", "chmod", "+x", str(SYS_DESKTOP)], check=True)

# 8. Trigger desktop application menu caching system updates
print("Refreshing platform global desktop integration databases...")
subprocess.run(["sudo", "update-desktop-database", "/usr/share/applications"], check=False)

print("ClassiCube configuration deployment completed successfully.")
