import os
import sys
from board import _board
import shutil
import mpy_cross
import minify_html
import time


_DIST = ".dist"


def clean_up():
    """Deletes all the files except boot.py"""
    for file in _board.files.ls(recursive=True):
        fname = file.split(" - ")[0]
        fname = fname.replace("\r","\\r")
        if fname == "/boot.py":
            continue
        print(f"Deleting: {fname}")
        _board.files.rm(fname)


def upload():
    os.chdir(_DIST)
    for curdir, dirs, lfiles in os.walk(".", topdown=True):
        print(f"Handling folder: {curdir}")
        rdir = curdir.lstrip(".\\").replace("\\", "/")
        if curdir != ".":
            _board.files.mkdir(rdir, exists_okay=True)
        for f in lfiles:
            local_path = os.path.join(curdir, f)
            print(f"Uploading {local_path}")
            with open(local_path, "rb") as bf:
                _board.files.put(rdir + "/" + f, bf.read())


def minify():
    os.chdir("src")
    for curdir, dirs, lfiles in os.walk(".", topdown=True):
        rdir = os.path.join("..",_DIST,curdir.lstrip(".\\").replace("\\", "/"))
        if os.path.basename(curdir) == "__pycache__":
            continue
        if curdir != ".":
            os.makedirs(os.path.join(rdir),exist_ok=True)
        for f in lfiles:
            local_path = os.path.abspath(os.path.join(curdir, f))
            target_path =  os.path.abspath(os.path.join(rdir,f))

            # If we are handling a python file, compile it.
            if local_path.endswith(".py") and not local_path.endswith("boot.py") and not local_path.endswith("main.py"):
                target_path = target_path.replace(".py", ".mpy")
                print(f"Pre-compiling \"{local_path}\" to \"{target_path}\"")
                mpy_cross.run("-o", target_path, local_path)
                continue
            
            if local_path.endswith(".css") or local_path.endswith(".html") or local_path.endswith(".js"):
                with open(local_path, "r") as i:
                    minified = minify_html.minify(i.read(), minify_js=True, minify_css=True, remove_processing_instructions=True)
                    with open(target_path, "w") as o:
                        o.write(minified)

    os.chdir("..")

def main():
    # Check args
    if len(sys.argv) != 2:
        print("Missing required argument: Serial PORT")
        exit(1)
    port = sys.argv[1]

    # Prepare the DIST folder
    if os.path.isdir(_DIST):
        print(f"Removing {_DIST}")
        shutil.rmtree(_DIST)
    os.makedirs(_DIST)

    # precompile and minify
    minify()

    # copy the boot.py & hw.json
    print("Uploading boot.py, main.py and hw.json")
    shutil.copyfile("src/boot.py", os.path.join(_DIST, "boot.py"))
    shutil.copyfile("src/main.py", os.path.join(_DIST, "main.py"))
    
    if os.path.isfile("hw.json"):
        shutil.copyfile("hw.json", os.path.join(_DIST, "hw.json"))

    if os.path.isfile("config.json"):
        shutil.copyfile("config.json", os.path.join(_DIST, "config.json"))

    # Initialize device configuration
    _board.initialize(port)

    # Run the upload script
    clean_up()
    upload()

    _board.reset(seconds=1.0)

if __name__ == '__main__':
    main()
