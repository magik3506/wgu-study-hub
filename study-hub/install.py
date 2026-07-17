#!/usr/bin/env python3
"""Optional one-time setup: put a "WGU Study Hub" shortcut on your desktop.

Run it once:    python3 install.py      (or double-click on Windows)

Standard library only — it just creates a shortcut that launches the hub
from wherever this folder lives. You can also skip this entirely and
double-click the launcher in this folder instead:

    Windows   Start Study Hub.bat
    macOS     Start Study Hub.command
    Linux     start-study-hub.sh
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")


def _desktop():
    if os.path.isdir(DESKTOP):
        return DESKTOP
    # some Linux distros localize the desktop dir
    try:
        out = subprocess.run(["xdg-user-dir", "DESKTOP"],
                             capture_output=True, text=True, timeout=5)
        d = out.stdout.strip()
        if d and os.path.isdir(d):
            return d
    except Exception:
        pass
    return None


def install_windows():
    bat = os.path.join(HERE, "Start Study Hub.bat")
    icon = os.path.join(HERE, "core", "webdist", "favicon.ico")
    lnk = os.path.join(DESKTOP, "WGU Study Hub.lnk")
    ps = (
        "$W = New-Object -ComObject WScript.Shell; "
        "$S = $W.CreateShortcut('{lnk}'); "
        "$S.TargetPath = '{bat}'; "
        "$S.WorkingDirectory = '{cwd}'; "
        "$S.Description = 'WGU Study Hub'; "
        "{icon_line}"
        "$S.Save()"
    ).format(
        lnk=lnk.replace("'", "''"),
        bat=bat.replace("'", "''"),
        cwd=HERE.replace("'", "''"),
        icon_line=("$S.IconLocation = '%s'; " % icon.replace("'", "''"))
        if os.path.exists(icon) else "",
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-Command", ps],
        check=True)
    return lnk


def install_macos():
    src = os.path.join(HERE, "Start Study Hub.command")
    dst = os.path.join(DESKTOP, "WGU Study Hub.command")
    shutil.copyfile(src, dst)
    os.chmod(dst, 0o755)
    return dst


def install_linux():
    launcher = os.path.join(HERE, "start-study-hub.sh")
    os.chmod(launcher, 0o755)
    entry = "\n".join([
        "[Desktop Entry]",
        "Type=Application",
        "Name=WGU Study Hub",
        "Comment=Local study drills, playgrounds and guides",
        'Exec="%s"' % launcher,
        'Path=%s' % HERE,
        "Terminal=true",
        "Categories=Education;",
        "",
    ])
    made = []
    appdir = os.path.join(os.path.expanduser("~"), ".local", "share",
                          "applications")
    os.makedirs(appdir, exist_ok=True)
    app = os.path.join(appdir, "wgu-study-hub.desktop")
    with open(app, "w") as f:
        f.write(entry)
    os.chmod(app, 0o755)
    made.append(app)
    d = _desktop()
    if d:
        dfile = os.path.join(d, "wgu-study-hub.desktop")
        with open(dfile, "w") as f:
            f.write(entry)
        os.chmod(dfile, 0o755)
        made.append(dfile)
    return " and ".join(made)


def main():
    print("WGU Study Hub — desktop shortcut setup\n")
    try:
        if sys.platform.startswith("win"):
            where = install_windows()
        elif sys.platform == "darwin":
            where = install_macos()
        else:
            where = install_linux()
    except Exception as e:
        print("Couldn't create the shortcut automatically (%s)." % e)
        print("No problem — just double-click the launcher in this folder:")
        print('  Windows: "Start Study Hub.bat"')
        print('  macOS:   "Start Study Hub.command"')
        print("  Linux:   start-study-hub.sh")
        sys.exit(1)
    print("Done! Shortcut created at:\n  %s" % where)
    print("\nDouble-click it any time to open the Study Hub.")
    if sys.platform.startswith("linux"):
        print("(If your desktop asks, choose 'Allow launching' / "
              "'Trust and launch'.)")


if __name__ == "__main__":
    main()
