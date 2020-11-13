``` 
 ____  _____    _    ____  __  __ _____ 
|  _ \| ____|  / \  |  _ \|  \/  | ____|
| |_) |  _|   / _ \ | | | | |\/| |  _|  
|  _ <| |___ / ___ \| |_| | |  | | |___ 
|_| \_\_____/_/   \_\____/|_|  |_|_____|
```

# Usage

Simply run command from command line:

    $python3 MAIN.py

# Installation

1.  Windows 10 system (can be portable on Linux too)
2.  Create virtual environment (anaconda or venv)
    <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>
3.  Python + pip \> 3.7.x <https://anaconda.org/anaconda/python>
4.  Tesseract: <https://github.com/tesseract-ocr/tesseract>
5.  Realsense2: <https://www.intelrealsense.com/sdk-2/>
6.  Add Czech voice engine as an option:
    <https://www.ghacks.net/2018/08/11/unlock-all-windows-10-tts-voices-system-wide-to-get-more-of-them/>
7.  Build OpenCV with CUDA support:
    <https://medium.com/@mhfateen/build-opencv-4-4-0-with-cuda-gpu-support-on-windows-10-without-tears-aa85d470bcd0>
8.  Install python packages from pip by following command:

<!-- end list -->

    $pip install -r packages2install.txt

# Files

| Directory/File | Description                         |
| -------------- | ----------------------------------- |
| arduino\_files | Arduino code and examples           |
| btns           | Buttons graphics                    |
| doc            | Documentation                       |
| json           | Texts for voice in json format      |
| models         | Pretrained NN models                |
| playground     | Debugging sandbox                   |
| robohlava      | Core module                         |
| sound          | Sound .mp3 formats                  |
| txt, txt\_file | txt files: RUR, robohlava.txt       |
| MAIN.py        | Qt implementation and main function |

# Robohlava module description

| File                    | Description                                                        |
| ----------------------- | ------------------------------------------------------------------ |
| arduino.py              | Arduino communication                                              |
| camera.py               | Basic camera functions                                             |
| person\_class.py        | Person tracking algorithm                                          |
| detected\_objects.py    | Collecting information about detected objects                      |
| image\_class.py         | Image processing logic and functions                               |
| image\_processing.py    | Image processing by neural networks                                |
| robot\_class.py         | Wrapper to arduino.py and voice.py                                 |
| text\_processing.py     | Return texts to actual state                                       |
| tools.py                | Some useful tools: translate, Locker, Counter                      |
| config.py               | Config file with all parameters (timers, counters)                 |
| voice.py                | Voice, providing threading voice command                           |
| TTS.py                  | Voice backend                                                      |
| state\_machine\_base.py | State machine base classes and functions                           |
| state\_machine.py       | State machine implementation and states                            |
| core.py                 | Core backend file with all functions and classes combined together |

# Contacts

  - Author: Artyom Voronin
  - Contact: <artemvoronin95@gmail.com>
  - Date: 2020, Brno
