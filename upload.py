import os
import sys
from board import _board


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
    os.chdir("src")
    for curdir, dirs, lfiles in os.walk(".", topdown=True):
        print(f"Handling folder: {curdir}")
        rdir = curdir.lstrip(".\\").replace("\\", "/")
        if os.path.basename(curdir) == "__pycache__":
            continue
        if curdir != ".":
            _board.files.mkdir(rdir, exists_okay=True)
        for f in lfiles:
            local_path = os.path.join(curdir, f)
            print(f"Uploading {local_path}")
            with open(local_path, "rb") as bf:
                _board.files.put(rdir + "/" + f, bf.read())
    os.chdir("..")
    # copy the boot.py & hw.json
    print("Uploading optional files")
    for filename in ("hw.json", "config.json"):
        if os.path.isfile(filename):
            print(f"Uploading {filename}")
            with open(filename, "rb") as bf:
                _board.files.put(filename, bf.read())

def main():
    # Check args
    if len(sys.argv) != 2:
        print("Missing required argument: Serial PORT")
        exit(1)
    port = sys.argv[1]

    # Initialize device configuration
    _board.initialize(port)

    # Run the upload script
    clean_up()

    # Upload the rest of files
    upload()

    # Reset the board
    _board.reset(seconds=1.0)


if __name__ == '__main__':
    main()
