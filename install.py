#!/usr/bin/env python3
import os
import pathlib
import urllib.request
import stat

# Paths
HOME = pathlib.Path.home()
LOCAL_APPS_DIR = HOME / ".local" / "share" / "applications"
LOCAL_APPS_DIR.mkdir(parents=True, exist_ok=True)

DESKTOP_FILE = LOCAL_APPS_DIR / "ClassiCube.desktop"
GAME_DIR = pathlib.Path.cwd()
ICON_FILE = GAME_DIR / "CCicon.png"

# Remove existing desktop file if it exists
if DESKTOP_FILE.exists():
    print(f"Removing existing {DESKTOP_FILE}")
    DESKTOP_FILE.unlink()

# Download icon if missing
if ICON_FILE.exists():
    print(f"{ICON_FILE.name} exists already. Skipping download.")
else:
    print(f"{ICON_FILE.name} doesn't exist. Downloading...")
    url = "https://raw.githubusercontent.com/ClassiCube/classicube/master/misc/CCicon.png"
    urllib.request.urlretrieve(url, ICON_FILE)
    print(f"Downloaded {ICON_FILE.name}")

# Create the desktop entry content
desktop_entry = f"""[Desktop Entry]
Type=Application
Comment=Minecraft Classic inspired sandbox game
Name=ClassiCube
Exec={GAME_DIR}/ClassiCube
Icon={ICON_FILE}
Path={GAME_DIR}
Terminal=false
Categories=Game;
Actions=singleplayer;resume;

[Desktop Action singleplayer]
Name=Start singleplayer
Exec={GAME_DIR}/ClassiCube --singleplayer

[Desktop Action resume]
Name=Resume last server
Exec={GAME_DIR}/ClassiCube --resume
"""

# Write the desktop entry
with open(DESKTOP_FILE, "w") as f:
    f.write(desktop_entry)

# Make it executable
DESKTOP_FILE.chmod(DESKTOP_FILE.stat().st_mode | stat.S_IEXEC)
EXEC = GAME_DIR / "ClassiCube"
EXEC.chmod(EXEC.stat().st_mode | stat.S_IEXEC)

print(f"{DESKTOP_FILE} created and installed in your local applications directory.")

# Optional: update local desktop database (refresh menu)
os.system("update-desktop-database ~/.local/share/applications")