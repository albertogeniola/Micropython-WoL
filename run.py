from conf import files


def main():
    files.run("src/main.py", wait_output=False, stream_output=False)


if __name__ == '__main__':
    main()
