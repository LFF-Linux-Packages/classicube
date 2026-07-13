#!/usr/bin/env python3
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
    print("Icon file not found locally. Downloading asset...")
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
else:
    print(f"Warning: expected binary at {EXEC_BINARY} was not found after deployment.")

# 4b. Lock the deployed package directory down to be readable/executable but NOT
# writable by regular users. ClassiCube normally wants to write its data (options.txt,
# fontscache.txt, screenshots, downloaded texture packs, etc.) alongside its own
# executable -- but the launcher wrapper generated below redirects all of that to a
# per-user directory instead, so /opt/classicube itself never needs to be writable.
print(f"Locking down {SYS_GAME_DIR} to read-only for non-root users...")
subprocess.run(["sudo", "chown", "-R", "root:root", str(SYS_GAME_DIR)], check=True)
subprocess.run(["sudo", "find", str(SYS_GAME_DIR), "-type", "d", "-exec", "chmod", "755", "{}", "+"], check=True)
subprocess.run(["sudo", "find", str(SYS_GAME_DIR), "-type", "f", "-exec", "chmod", "644", "{}", "+"], check=True)
if EXEC_BINARY.exists():
    subprocess.run(["sudo", "chmod", "755", str(EXEC_BINARY)], check=True)

# 5. Handle global desktop icon mappings
if ICON_FILE.exists():
    subprocess.run(["sudo", "cp", str(ICON_FILE), str(SYS_ICON)], check=True)

# 6. Generate the execution script wrapper inside /usr/bin/ to execute contextually.
# The game itself only ever needs read access to GAME_DIR (for the binary and its
# bundled assets); all of its writable runtime data is redirected to a per-user
# directory that gets seeded from the read-only install on first launch.
# A raw string + placeholder substitution is used here (not an f-string) so that the
# shell's own "${...}" parameter-expansion syntax below isn't mistaken for a Python
# format field.
wrapper_script_content = r"""#!/bin/bash
set -e

GAME_DIR="__GAME_DIR__"
USER_DATA_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/classicube"

mkdir -p "$USER_DATA_DIR"

copy_all() {
    find "$GAME_DIR" -mindepth 1 -maxdepth 1 \
        -not -name "install.py" \
        -not -name "apt.txt" \
        -not -name "config.txt" \
        -exec cp -r {} "$USER_DATA_DIR"/ \;
}

if [ ! -f "$USER_DATA_DIR/ClassiCube" ]; then
    copy_all
fi

cd "$USER_DATA_DIR"
exec "$USER_DATA_DIR/ClassiCube" "$@"
""".replace("__GAME_DIR__", str(SYS_GAME_DIR))

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