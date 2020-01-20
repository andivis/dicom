# dicom

## Installation

1. Make sure Python 3.6 or higher and git are installed.

    Windows:

    https://www.python.org/downloads/windows/

    If the installer asks to add Python to the path, check yes.

    https://git-scm.com/download/win

    MacOS:

    Open Spotlight search by clicking the magnifying glass icon in the top right of your screen. Search for `Terminal`. Open it. Paste the following commands and press enter.

    ```
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    echo 'export PATH="/usr/local/opt/python/libexec/bin:$PATH"' >> ~/.profile
    brew install python
    ```

    Linux:

    Open a terminal window. Paste the following commands and press enter.

    ```
    sudo apt install -y python3
    sudo apt install -y python3-pip
    sudo apt install -y git
    ```

2. Open a terminal/command prompt window

3. Run the commands below. Depending on your system you may need replace `pip3` instead of `pip`.

    ```
    git clone https://github.com/andivis/dicom.git
    cd dicom
    pip3 install lxml
    ```

## Instructions

1. Open a terminal/command prompt window. Cd to the directory containing `main.py`. It's where you cloned the repository before.
2. Put the json files from https://github.com/innolitics/dicom-standard/tree/master/standard into a directory called `input` next to `main.py`
8. Run `python3 main.py`. Depending on your system you may need run `python main.py` instead.

## Options file

- `inputDirectory`: directory where the DICOM json files are store. Default `input`.