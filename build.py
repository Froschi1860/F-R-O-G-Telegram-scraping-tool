import os
import PyInstaller.__main__


def main():
    PyInstaller.__main__.run(
        [
            "-n",
            "F-R-O-G",
            "--onefile",
            "--noconsole",
            "--add-data",
            f"frog/frontend{os.pathsep}frog/frontend",
            os.path.join(os.curdir, "frog", "backend", "start_build.py"),
        ]
    )


if __name__ == "__main__":
    main()
