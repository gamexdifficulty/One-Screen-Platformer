import os
import sys
import time
import json
import glob
import shutil
import pygame
import datetime
import argparse
from cryptography.fernet import Fernet

class Builder:
    def __init__(self,engine) -> None:

        """
        Initialise the engines input system.

        The build system packs the engine files if a release is planed and converts the game to an exe file.

        Args:
        
        - engine (Engine): The engine to access specific variables.

        !!!This is only used internally by the engine and should not be called in a game!!!
        """

        # Engine variable
        self._engine = engine

    def _setup_game(self,name:str="New Game"):

        """
        Created the initial game folder structure

        Args:

        - name (str): Not implemented yet, for naming the game files

        !!!This is only used internally by the engine and should not be called in a game!!!
        """

        self._update_modules()

        # Create engine tree
        directories_created = 0
        files_created = 0
        directories_to_create = ["data","screenshots",os.path.join("data","classes"),os.path.join("data","saves"),os.path.join("data","saves","backup"),os.path.join("data","sprites")]

        # Creating directories
        for directory in directories_to_create:
            try:
                os.mkdir(directory)
                directories_created += 1
            except FileExistsError:
                self._engine.logger.warning(f"Skipping creation of directory {directory}, it already exist.")

        # Create main code file
        if not os.path.exists("main.py"):
            with open("main.py","+wt") as file:
                file.write("from frostlight_engine import *\n")
                file.write("\n")
                file.write("class Game(Engine):\n")
                file.write("    def __init__(self):\n")
                file.write("        super().__init__() # Engine options go here\n")
                file.write("\n")
                file.write("    def update(self):\n")
                file.write('        if self.game_state == "intro":\n')
                file.write("            pass\n")
                file.write("\n")
                file.write('        if self.game_state == "menu":\n')
                file.write("            pass\n")
                file.write("\n")
                file.write('        if self.game_state == "game":\n')
                file.write("            pass\n")
                file.write("\n")
                file.write("    def draw(self):\n")
                file.write('        if self.game_state == "intro":\n')
                file.write("            pass\n")
                file.write("\n")
                file.write('        if self.game_state == "menu":\n')
                file.write("            pass\n")
                file.write("\n")
                file.write('        if self.game_state == "game":\n')
                file.write("            pass\n")
                file.write("\n")
                file.write("\n")
                file.write('if __name__ == "__main__":\n')
                file.write("    game = Game()\n")
                file.write("    game.run()\n")
            files_created += 1
        else:
            self._engine.logger.warning("Skipping creation of main file, already exist.")

        # Log creation process
        if files_created == 0 and directories_created == 0:
            self._engine.logger.info("No new files or directories where created.")
        else:
            self._engine.logger.info(f"Created game files structure with {files_created} files and {directories_created} directories")

    def _update_modules(self):

        """
        Updates required python modules

        Args:

        - no args are required

        !!!This is only used internally by the engine and should not be called in a game!!!
        """

        import sys
        import ast
        import subprocess

        # collecting modules to update
        
        modules = []
        with open(os.path.basename(__file__), 'r') as f:
            content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        module_name = module_name.split('.')[0]
                        if not module_name in sys.stdlib_module_names:
                            modules.append(module_name)

                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module
                    module_name = module_name.split('.')[0]
                    if not module_name in sys.stdlib_module_names:
                        modules.append(module_name)

        # updating modules

        for module_name in modules:
            print(f"\n\033[94m[Info] Updating module: \033[0m{module_name}\n")
            try:
                subprocess.check_call(['pip', 'install', module_name])
                print(f"\n\033[92m[Info] Successfully updated \033[0m{module_name}\n")
            except subprocess.CalledProcessError:
                print(f"\n\033[91m [Error] Failed to updated \033[0m{module_name}\n")
            print('-'*50)

    def _create_exe(self,name:str="game"):

        """
        Builds the game into exe file and zips all dependencies

        Args:

        - name (str): Not implemented yet, for naming the game files

        !!!This is only used internally by the engine and should not be called in a game!!!
        """

        # Import Modules
        import subprocess
        import shutil
        import sys

        # Install pyinstaller
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            import PyInstaller.__main__
        except:
            print("Pyinstaller cannot be installed!")
        else:

            # Packing game in exe
            PyInstaller.__main__.run([
                'main.py',
                '--onefile',
                '--noconsole',
                '--clean'
            ])

            # Removing build files
            if os.path.isfile("main.spec"):
                os.remove("main.spec")
            if os.path.isdir("build"):
                shutil.rmtree("build")
            if os.path.isdir("dist"):
                if os.path.isdir("export"):
                    shutil.rmtree("export")
                os.rename("dist","export")

            # Create Export DIR
            if os.path.isdir("data"):
                shutil.copytree("data",os.path.join("export","data"))
            if os.path.isdir("screenshots"):
                shutil.copytree("screenshots",os.path.join("export","screenshots"))

            # Zip Export
            if os.path.isdir("export"):
                shutil.make_archive("export","zip","export")
                shutil.rmtree("export")

    def _pack_release(self):

        """
        Packs engine for release into single file

        Args:

        - no args are required

        !!!This is only used internally by the engine and should not be called in a game!!!
        """

        # Relevent paths
        class_path = "./classes"
        export_file = "engine_export.py"
        main_file = "frostlight_engine.py"
        imported_modules = []
        class_contents = []
        within_class = False

        # Read class folder 
        for pathname, _, files in os.walk(class_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(pathname, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        for line in content.split("\n"):
                            unstriped_line = line
                            line = line.strip()
                            if unstriped_line.startswith("class "):
                                within_class = True
                            elif unstriped_line and not unstriped_line.startswith(" ") and within_class:
                                within_class = False
                            if (line.startswith("import ") or line.startswith("from "))  and not "PyInstaller.__main__" in line and not within_class:
                                if not line.startswith("from classes."):
                                    imported_modules.append(line)
                                    content = content.replace(unstriped_line, "",1)
                        class_contents.append(content)

        imported_modules = sorted(set(imported_modules),key=len)

        # Read main file
        with open(main_file, "r", encoding="utf-8") as main_handle:
            main_content = main_handle.read()
            for line in main_content.split("\n"):
                line = line.strip()
                if line.startswith("import ") or line.startswith("from "):
                    if not line.startswith("from classes."):
                        imported_modules.append(line)

        imported_modules = sorted(set(imported_modules),key=len)

        # Creating export file
        with open(export_file, "w", encoding="utf-8") as f:
            # write imports
            for importlines in imported_modules:
                f.write(f"{importlines}\n")
            f.write("\n")

            # Write classes content
            for content in class_contents:
                content = "\n".join(line for line in content.split("\n") if not line.strip().startswith("from classes."))
                f.write(content.strip())
                f.write("\n\n")

            # Write main content
            main_content = "\n".join(line for line in main_content.split("\n") if not line.strip().startswith("from classes.") and not line.strip().startswith("import "))
            f.write(main_content)

# Input types
_KEYBOARD = 0
_MOUSE = 1
_JOYSTICK = 2

# Input method
CLICKED = 0
PRESSED = 1
RELEASE = 2

# Keyboard input index
KEY_A = [pygame.K_a,_KEYBOARD]
KEY_B = [pygame.K_b,_KEYBOARD]
KEY_C = [pygame.K_c,_KEYBOARD]
KEY_D = [pygame.K_d,_KEYBOARD]
KEY_E = [pygame.K_e,_KEYBOARD]
KEY_F = [pygame.K_f,_KEYBOARD]
KEY_G = [pygame.K_g,_KEYBOARD]
KEY_H = [pygame.K_h,_KEYBOARD]
KEY_I = [pygame.K_i,_KEYBOARD]
KEY_J = [pygame.K_j,_KEYBOARD]
KEY_K = [pygame.K_k,_KEYBOARD]
KEY_L = [pygame.K_l,_KEYBOARD]
KEY_M = [pygame.K_m,_KEYBOARD]
KEY_N = [pygame.K_n,_KEYBOARD]
KEY_O = [pygame.K_o,_KEYBOARD]
KEY_P = [pygame.K_p,_KEYBOARD]
KEY_Q = [pygame.K_q,_KEYBOARD]
KEY_R = [pygame.K_r,_KEYBOARD]
KEY_S = [pygame.K_s,_KEYBOARD]
KEY_T = [pygame.K_t,_KEYBOARD]
KEY_U = [pygame.K_u,_KEYBOARD]
KEY_V = [pygame.K_v,_KEYBOARD]
KEY_W = [pygame.K_w,_KEYBOARD]
KEY_X = [pygame.K_x,_KEYBOARD]
KEY_Y = [pygame.K_y,_KEYBOARD]
KEY_Z = [pygame.K_z,_KEYBOARD]
KEY_0 = [pygame.K_0,_KEYBOARD]
KEY_1 = [pygame.K_1,_KEYBOARD]
KEY_2 = [pygame.K_2,_KEYBOARD]
KEY_3 = [pygame.K_3,_KEYBOARD]
KEY_4 = [pygame.K_4,_KEYBOARD]
KEY_5 = [pygame.K_5,_KEYBOARD]
KEY_6 = [pygame.K_6,_KEYBOARD]
KEY_7 = [pygame.K_7,_KEYBOARD]
KEY_8 = [pygame.K_8,_KEYBOARD]
KEY_9 = [pygame.K_9,_KEYBOARD]
KEY_F1 = [pygame.K_F1,_KEYBOARD]
KEY_F2 = [pygame.K_F2,_KEYBOARD]
KEY_F3 = [pygame.K_F3,_KEYBOARD]
KEY_F4 = [pygame.K_F4,_KEYBOARD]
KEY_F5 = [pygame.K_F5,_KEYBOARD]
KEY_F6 = [pygame.K_F6,_KEYBOARD]
KEY_F7 = [pygame.K_F7,_KEYBOARD]
KEY_F8 = [pygame.K_F8,_KEYBOARD]
KEY_F9 = [pygame.K_F9,_KEYBOARD]
KEY_F10 = [pygame.K_F10,_KEYBOARD]
KEY_F11 = [pygame.K_F11,_KEYBOARD]
KEY_F12 = [pygame.K_F12,_KEYBOARD]
KEY_LCTRL = [pygame.K_LCTRL,_KEYBOARD]
KEY_RCTRL = [pygame.K_RCTRL,_KEYBOARD]
KEY_LSHIFT = [pygame.K_LSHIFT,_KEYBOARD]
KEY_RSHIFT = [pygame.K_RSHIFT,_KEYBOARD]
KEY_RETURN = [pygame.K_RETURN,_KEYBOARD]
KEY_SPACE = [pygame.K_SPACE,_KEYBOARD]
KEY_ESCAPE = [pygame.K_ESCAPE,_KEYBOARD]
KEY_BACKSPACE = [pygame.K_BACKSPACE,_KEYBOARD]
KEY_TAB = [pygame.K_TAB,_KEYBOARD]
KEY_HOME = [pygame.K_HOME,_KEYBOARD]
KEY_ARROW_LEFT = [pygame.K_LEFT,_KEYBOARD]
KEY_ARROW_RIGHT = [pygame.K_RIGHT,_KEYBOARD]
KEY_ARROW_UP = [pygame.K_UP,_KEYBOARD]
KEY_ARROW_DOWN = [pygame.K_DOWN,_KEYBOARD]

# Mouse input index
MOUSE_LEFTCLICK = [0,_MOUSE]
MOUSE_MIDDLECLICK = [1,_MOUSE]
MOUSE_RIGHTCLICK = [2,_MOUSE]

# Joystick input index
JOYSTICK_BUTTON_DOWN = [0,_JOYSTICK]
JOYSTICK_BUTTON_RIGHT = [1,_JOYSTICK]
JOYSTICK_BUTTON_UP = [2,_JOYSTICK]
JOYSTICK_BUTTON_LEFT = [3,_JOYSTICK]
JOYSTICK_DPAD_DOWN = [4,_JOYSTICK]
JOYSTICK_DPAD_RIGHT = [5,_JOYSTICK]
JOYSTICK_DPAD_UP = [6,_JOYSTICK]
JOYSTICK_DPAD_LEFT = [7,_JOYSTICK]
JOYSTICK_RIGHT_STICK_VERTICAL = [8,_JOYSTICK]
JOYSTICK_RIGHT_STICK_HORIZONTAL = [9,_JOYSTICK]
JOYSTICK_RIGHT_STICK = [10,_JOYSTICK]
JOYSTICK_LEFT_STICK_VERTICAL = [11,_JOYSTICK]
JOYSTICK_LEFT_STICK_HORIZONTAL = [12,_JOYSTICK]
JOYSTICK_LEFT_STICK = [13,_JOYSTICK]
JOYSTICK_BUTTON_SPECIAL_1 = [14,_JOYSTICK]
JOYSTICK_BUTTON_SPECIAL_2 = [15,_JOYSTICK]
JOYSTICK_RIGHT_BUMPER = [16,_JOYSTICK]
JOYSTICK_LEFT_BUMPER = [17,_JOYSTICK]
JOYSTICK_TRIGGER_R2 = [18,_JOYSTICK]
JOYSTICK_TRIGGER_L2 = [19,_JOYSTICK]
JOYSTICK_LEFT_STICK_UP = [20,_JOYSTICK]
JOYSTICK_LEFT_STICK_DOWN = [21,_JOYSTICK]
JOYSTICK_LEFT_STICK_LEFT = [22,_JOYSTICK]
JOYSTICK_LEFT_STICK_RIGHT = [23,_JOYSTICK]
JOYSTICK_RIGHT_STICK_UP = [24,_JOYSTICK]
JOYSTICK_RIGHT_STICK_DOWN = [25,_JOYSTICK]
JOYSTICK_RIGHT_STICK_LEFT = [26,_JOYSTICK]
JOYSTICK_RIGHT_STICK_RIGHT = [27,_JOYSTICK]

# Joystick types
_XBOX_360_CONTROLLER = 0
_PLAYSTATION_4_CONTROLLER = 1
_PLAYSTATION_5_CONTROLLER = 2
_NINTENDO_SWITCH_PRO_CONTROLLER = 3
_NINTENDO_SWITCH_JOYCON_CONTROLLER_L = 4
_NINTENDO_SWITCH_JOYCON_CONTROLLER_R = 5
_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_R = 6

# Joystick button maps
_JOYSTICK_XBOX_360_BUTTON_MAP = [
    [JOYSTICK_BUTTON_DOWN],         # A BUTTON
    [JOYSTICK_BUTTON_RIGHT],        # B BUTTON
    [JOYSTICK_BUTTON_LEFT],         # X BUTTON
    [JOYSTICK_BUTTON_UP],           # Y BUTTON
    [JOYSTICK_LEFT_BUMPER],         # LEFT BUMPER
    [JOYSTICK_RIGHT_BUMPER],        # RIGHT BUMPER
    [JOYSTICK_BUTTON_SPECIAL_1],    # BACK BUTTON 
    [JOYSTICK_BUTTON_SPECIAL_2],    # START BUTTON
    [JOYSTICK_LEFT_STICK],          # LEFT STICK
    [JOYSTICK_RIGHT_STICK],         # RIGHT STICK
    [JOYSTICK_BUTTON_SPECIAL_1],    # PS BUTTON
]

_JOYSTICK_PLAYSTATION_BUTTON_MAP = [
    [JOYSTICK_BUTTON_DOWN],         # CROSS BUTTON
    [JOYSTICK_BUTTON_RIGHT],        # CIRCLE BUTTON
    [JOYSTICK_BUTTON_UP],           # TRIANGLE BUTTON
    [JOYSTICK_BUTTON_LEFT],         # SQUARE BUTTON
    [JOYSTICK_BUTTON_SPECIAL_1],    # SHARE BUTTON  
    [JOYSTICK_BUTTON_SPECIAL_1],    # PS BUTTON
    [JOYSTICK_BUTTON_SPECIAL_2],    # OPTIONS BUTTON
    [JOYSTICK_LEFT_STICK],          # LEFT STICK
    [JOYSTICK_RIGHT_STICK],         # RIGHT STICK
    [JOYSTICK_LEFT_BUMPER],         # LEFT BUMPER
    [JOYSTICK_RIGHT_BUMPER],        # RIGHT BUMPER
    [JOYSTICK_DPAD_UP],             # DPAD UP
    [JOYSTICK_DPAD_DOWN],           # DPAD DOWN
    [JOYSTICK_DPAD_LEFT],           # DPAD LEFT
    [JOYSTICK_DPAD_RIGHT],          # DPAD RIGHT
    [JOYSTICK_BUTTON_SPECIAL_2],    # TOUCH PAD
]

_JOYSTICK_NINTENDO_SWITCH_PRO_CONTROLLER_BUTTON_MAP = [
    [JOYSTICK_BUTTON_RIGHT],        # A BUTTON
    [JOYSTICK_BUTTON_DOWN],         # B BUTTON
    [JOYSTICK_BUTTON_UP],           # X BUTTON
    [JOYSTICK_BUTTON_LEFT],         # Y BUTTON
    [JOYSTICK_BUTTON_SPECIAL_1],    # - BUTTON  
    [JOYSTICK_BUTTON_SPECIAL_1],    # HOME BUTTON
    [JOYSTICK_BUTTON_SPECIAL_2],    # + BUTTON
    [JOYSTICK_LEFT_STICK],          # LEFT STICK
    [JOYSTICK_RIGHT_STICK],         # RIGHT STICK
    [JOYSTICK_LEFT_BUMPER],         # LEFT BUMPER
    [JOYSTICK_RIGHT_BUMPER],        # RIGHT BUMPER
    [JOYSTICK_DPAD_UP],             # DPAD UP
    [JOYSTICK_DPAD_DOWN],           # DPAD DOWN
    [JOYSTICK_DPAD_LEFT],           # DPAD LEFT
    [JOYSTICK_DPAD_RIGHT],          # DPAD RIGHT
    [JOYSTICK_BUTTON_SPECIAL_2],    # CAPTURE BUTTON
]

_JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_BUTTON_MAP = [
    [JOYSTICK_BUTTON_RIGHT],        # DPAD RIGHT
    [JOYSTICK_BUTTON_DOWN],         # DPAD DOWN
    [JOYSTICK_BUTTON_UP],           # DPAD UP
    [JOYSTICK_BUTTON_LEFT],         # DPAD LEFT
    [None],
    [JOYSTICK_BUTTON_SPECIAL_2],    # CAPTURE BUTTON
    [JOYSTICK_BUTTON_SPECIAL_1],    # - BUTTON
    [JOYSTICK_LEFT_STICK],          # LEFT STICK
    [None],
    [JOYSTICK_LEFT_BUMPER],         # SL
    [JOYSTICK_RIGHT_BUMPER],        # SR
    [None],
    [None],
    [None],
    [None],
    [None],
    [None],
    [JOYSTICK_TRIGGER_L2],          # L 
    [None],
    [JOYSTICK_TRIGGER_L2],          # ZL
]

_JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_R_BUTTON_MAP = [
    [JOYSTICK_BUTTON_UP],           # X BUTTON
    [JOYSTICK_BUTTON_RIGHT],        # A BUTTON
    [JOYSTICK_BUTTON_LEFT],         # Y BUTTON
    [JOYSTICK_BUTTON_DOWN],         # B BUTTON
    [None],
    [JOYSTICK_BUTTON_SPECIAL_1],    # HOME BUTTON
    [JOYSTICK_BUTTON_SPECIAL_2],    # + BUTTON
    [JOYSTICK_RIGHT_STICK],         # RIGHT STICK
    [None],
    [JOYSTICK_LEFT_BUMPER],         # SL
    [JOYSTICK_RIGHT_BUMPER],        # SR
    [None],
    [None],
    [None],
    [None],
    [None],
    [JOYSTICK_TRIGGER_R2],          # R
    [None],
    [JOYSTICK_TRIGGER_R2],          # ZR
    [None],
]

_JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_R_BUTTON_MAP = [
    [JOYSTICK_BUTTON_RIGHT],        # A BUTTON
    [JOYSTICK_BUTTON_DOWN],         # B BUTTON
    [JOYSTICK_BUTTON_UP],           # X BUTTON
    [JOYSTICK_BUTTON_LEFT],         # Y BUTTON
    [JOYSTICK_BUTTON_SPECIAL_1],    # - BUTTON  
    [JOYSTICK_BUTTON_SPECIAL_1],    # HOME BUTTON
    [JOYSTICK_BUTTON_SPECIAL_2],    # + BUTTON
    [JOYSTICK_LEFT_STICK],          # LEFT STICK
    [JOYSTICK_RIGHT_STICK],         # RIGHT STICK
    [JOYSTICK_LEFT_BUMPER],         # LEFT BUMPER
    [JOYSTICK_RIGHT_BUMPER],        # RIGHT BUMPER
    [JOYSTICK_DPAD_UP],             # DPAD UP
    [JOYSTICK_DPAD_DOWN],           # DPAD DOWN
    [JOYSTICK_DPAD_LEFT],           # DPAD LEFT
    [JOYSTICK_DPAD_RIGHT],          # DPAD RIGHT
    [JOYSTICK_BUTTON_SPECIAL_2],    # CAPTURE BUTTON
]

_JOYSTICK_BUTTON_MAP = [
    _JOYSTICK_XBOX_360_BUTTON_MAP,
    _JOYSTICK_PLAYSTATION_BUTTON_MAP,
    _JOYSTICK_PLAYSTATION_BUTTON_MAP,
    _JOYSTICK_NINTENDO_SWITCH_PRO_CONTROLLER_BUTTON_MAP,
    _JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_BUTTON_MAP,
    _JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_R_BUTTON_MAP,
    _JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_R_BUTTON_MAP,
]

# Joystick axis map

_JOYSTICK_GENERIC_AXIS_MAP = [
    JOYSTICK_LEFT_STICK_HORIZONTAL,
    JOYSTICK_LEFT_STICK_VERTICAL,
    JOYSTICK_RIGHT_STICK_HORIZONTAL,
    JOYSTICK_RIGHT_STICK_VERTICAL,
    JOYSTICK_TRIGGER_L2,
    JOYSTICK_TRIGGER_R2,
]

_JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_AXIS_MAP = [
    JOYSTICK_LEFT_STICK_VERTICAL,
    JOYSTICK_LEFT_STICK_HORIZONTAL,
]

_JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_R_AXIS_MAP = [
    JOYSTICK_RIGHT_STICK_VERTICAL,
    JOYSTICK_RIGHT_STICK_HORIZONTAL,
]

_JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_R_AXIS_MAP = [
    JOYSTICK_LEFT_STICK_HORIZONTAL,
    JOYSTICK_LEFT_STICK_VERTICAL,
    JOYSTICK_RIGHT_STICK_HORIZONTAL,
    JOYSTICK_RIGHT_STICK_VERTICAL,
]

_JOYSTICK_AXIS_MAP = [
    _JOYSTICK_GENERIC_AXIS_MAP,
    _JOYSTICK_GENERIC_AXIS_MAP,
    _JOYSTICK_GENERIC_AXIS_MAP,
    _JOYSTICK_GENERIC_AXIS_MAP,
    _JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_AXIS_MAP,
    _JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_R_AXIS_MAP,
    _JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_R_AXIS_MAP,
]

_JOYSTICK_GENERIC_DIRECTION_AXIS_MAP = [
    [JOYSTICK_LEFT_STICK_LEFT,JOYSTICK_LEFT_STICK_RIGHT],
    [JOYSTICK_LEFT_STICK_UP,JOYSTICK_LEFT_STICK_DOWN],
    [JOYSTICK_RIGHT_STICK_LEFT,JOYSTICK_RIGHT_STICK_RIGHT],
    [JOYSTICK_RIGHT_STICK_UP,JOYSTICK_RIGHT_STICK_DOWN],
    [JOYSTICK_TRIGGER_L2,JOYSTICK_TRIGGER_L2],
    [JOYSTICK_TRIGGER_R2,JOYSTICK_TRIGGER_R2],
]

_JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_DIRECTION_AXIS_MAP = [
    [JOYSTICK_LEFT_STICK_LEFT,JOYSTICK_LEFT_STICK_RIGHT],
    [JOYSTICK_LEFT_STICK_UP,JOYSTICK_LEFT_STICK_DOWN],
]

_JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_R_DIRECTION_AXIS_MAP = [
    [JOYSTICK_RIGHT_STICK_LEFT,JOYSTICK_RIGHT_STICK_RIGHT],
    [JOYSTICK_RIGHT_STICK_UP,JOYSTICK_RIGHT_STICK_DOWN],
]

_JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_R_DIRECTION_AXIS_MAP = [
    [JOYSTICK_LEFT_STICK_LEFT,JOYSTICK_LEFT_STICK_RIGHT],
    [JOYSTICK_LEFT_STICK_UP,JOYSTICK_LEFT_STICK_DOWN],
    [JOYSTICK_RIGHT_STICK_LEFT,JOYSTICK_RIGHT_STICK_RIGHT],
    [JOYSTICK_RIGHT_STICK_UP,JOYSTICK_RIGHT_STICK_DOWN],
]

_JOYSTICK_DIRECTION_AXIS_MAP = [
    _JOYSTICK_GENERIC_DIRECTION_AXIS_MAP,
    _JOYSTICK_GENERIC_DIRECTION_AXIS_MAP,
    _JOYSTICK_GENERIC_DIRECTION_AXIS_MAP,
    _JOYSTICK_GENERIC_DIRECTION_AXIS_MAP,
    _JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_DIRECTION_AXIS_MAP,
    _JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_R_DIRECTION_AXIS_MAP,
    _JOYSTICK_NINTENDO_SWITCH_JOYCON_CONTROLLER_L_R_DIRECTION_AXIS_MAP,
]

class Input:
    def __init__(self, engine, joystick_dead_zone:int=0.15) -> None:

        """
        Initialise the engines input system.

        The input system should help collect and read out many inputs by a specified key.

        Args:

        - engine (Engine): The engine to access specific variables.
        - joystick_dead_zone (int)=0.15: Default controller stick deadzone.

        !!!This is only used internally by the engine and should not be called in a game!!!
        """

        # Engine variable
        self._engine = engine

        # Mouse variables        
        self.mouse = self._Mouse()

        # Keyboard variables
        self._keys = {}
        self._reset_keys = []

        # Joystick variables
        self.joystick_dead_zone = joystick_dead_zone
        self._joystick_devices = []
        self._reset_joy = []

        # Input variables
        self.autosave = True
        self.save_path = os.path.join("data","saves","input")
        self._registered_input = {
            "accept":[[MOUSE_LEFTCLICK,CLICKED],[KEY_SPACE,CLICKED],[KEY_RETURN,CLICKED],[JOYSTICK_BUTTON_DOWN,CLICKED]],
            "cancel":[[KEY_ESCAPE,CLICKED],[KEY_BACKSPACE,CLICKED],[JOYSTICK_BUTTON_RIGHT,CLICKED]],
            "right":[[KEY_D,PRESSED],[KEY_L,PRESSED],[KEY_ARROW_RIGHT,PRESSED],[JOYSTICK_DPAD_RIGHT,PRESSED],[JOYSTICK_LEFT_STICK_RIGHT,PRESSED],[JOYSTICK_RIGHT_STICK_RIGHT,PRESSED]],
            "left":[[KEY_A,PRESSED],[KEY_J,PRESSED],[KEY_ARROW_LEFT,PRESSED],[JOYSTICK_DPAD_LEFT,PRESSED],[JOYSTICK_LEFT_STICK_LEFT,PRESSED],[JOYSTICK_RIGHT_STICK_LEFT,PRESSED]],
            "up":[[KEY_W,PRESSED],[KEY_I,PRESSED],[KEY_ARROW_UP,PRESSED],[JOYSTICK_DPAD_UP,PRESSED],[JOYSTICK_LEFT_STICK_UP,PRESSED],[JOYSTICK_RIGHT_STICK_UP,PRESSED]],
            "down":[[KEY_S,PRESSED],[KEY_K,PRESSED],[KEY_ARROW_DOWN,PRESSED],[JOYSTICK_DPAD_DOWN,PRESSED],[JOYSTICK_LEFT_STICK_DOWN,PRESSED],[JOYSTICK_RIGHT_STICK_DOWN,PRESSED]],
            "screenshot":[[KEY_P,CLICKED],[KEY_F6,CLICKED]]
        }

        # Setting default value for keys
        for i in self._registered_input:
            for key in self._registered_input[i]:
                if key[0][1] == _KEYBOARD:
                    self._keys[key[0][0]] = [False,False,False]

    def new(self, name:str, key:list[int,int], method:int=1) -> bool:

        """
        Register or add a new input for read out later.

        Args:
        - name (str): The name of the input to register.
        - key: The input key which will be monitored.
        - method: The way the input is pressed: [CLICKED, PRESSED, RELEASE].

        Returns:
        - True if registration was successful.
        - False if input is already registered or something went wrong.

        If the variable autosave is True the new input is automatically saved and loaded.

        Example:
        ```
        self.input.new("move_left",KEY_ARROW_LEFT,PRESSED)
        ```
        """

        # Register/add new input
        try:
            if name not in self._registered_input:
                self._registered_input[name] = [[key,method]]
            else:
                if [key,method] not in self.registered_input[name]:
                    self._registered_input[name].append([key,method])
                else:
                    return False

            self._keys[key[0]] = [False,False,False]
            if self.autosave:
                self.save()
                self.load()
            return True
        except:
            return False

        
    def remove(self, inputname:str) -> bool:

        """ 
        Removes registered input.

        Args:
        - inputname (str): the name of the registered input to remove.

        Returns:
        - True if removal was successful.
        - False if something went wrong.

        If the variable autosave is True the removal of the input is automatically saved.

        Example:

        ```
        self.input.remove("move_left")
        ```
        registered inputs 

        - before removal:
        {"accept","cancel","right","left","up","down","screenshot","move_left"}

        - after removal:
        {"accept","cancel","right","left","up","down","screenshot"}
        """

        # Remove registered input
        try:
            del self._registered_input[inputname]
            if self.autosave:
                self.save()
                self.load()
            return True
        except:
            return False

    def reset(self, name:str, controller_index:int=-1):

        """
        Resets input to default value.

        Args:
        - name (str): The name of the input value to reset.
        - controller_index (int): Index or joystick id of the controller to reset.

        Returns:
        - True if reset was successful.
        - False if controller_index is out of range or something went wrong.

        Example:

        ```
        print(self.input.get("move_left"))
        >>> 1
        self.input.reset("move_left")
        print(self.input.get("move_left"))
        >>> 0
        ```
        """

        # Resets value of registered input to default

        try:
            for key in self._registered_input[name]:
                if key[0][1] == _KEYBOARD:
                    self._keys[key[0][0]] = [False,False,False]
                    
                # Mouse values
                elif key[0][1] == _MOUSE:
                    self.mouse.buttons[key[0][0]] = [False,False,False]
                    
                # Joystick values
                elif key[0][1] == _JOYSTICK:
                    if controller_index == -1:

                        # Resets value from all joysticks
                        for i in range(len(self._joystick_devices)):
                            self._joystick_devices[controller_index].inputs[key[0][0]] = [False,False,False]
                    else:

                        # Resets value from specified joystick
                        if controller_index < len(self._joystick_devices):
                            self._joystick_devices[controller_index].inputs[key[0][0]] = [False,False,False]
                        else:
                            return False
            return True
        except:
            return False

    def get(self, name:str, controller_index:int=-1) -> int|float:

        """
        Gets value of registered input.

        Args:
        - name (str): The name of the registered input to get a value from.
        - controller_index (int): Index or joystick id of the controller to get a value from.
        
        Returns:
        - Axis return value between -1.0 and 1.0.
        - Keys and buttons return either 0 or 1.
        - If return is 0 either the inputname or joystick dose not exist or input is on default value.

        Example:

        ```
        print(self.input.get("move_left"))
        >>> 1
        ```
        """

        # Get input value from registered input
        try:
            for key in self._registered_input[name]:

                # Keyboard values
                if key[0][1] == _KEYBOARD:
                    if self._keys[key[0][0]][key[1]]:
                        return 1

                # Mouse values
                elif key[0][1] == _MOUSE:
                    if self.mouse.buttons[key[0][0]][key[1]]:
                        return 1

                # Joystick values
                elif key[0][1] == _JOYSTICK:
                    if controller_index == -1:

                        # Get value from not specified joystick
                        for i in range(len(self._joystick_devices)):
                            input_value = self._joystick_devices[i]._get_input(key[0][0],key[1])
                            if input_value != False or input_value != 0.0:
                                return input_value
                    else:

                        # Get value from specified joystick
                        if controller_index < len(self._joystick_devices):
                            input_value = self._joystick_devices[controller_index]._get_input(key[0][0],key[1])
                        else:
                            return 0

                        # Filter joystick input value
                        if input_value != False or input_value != 0.0:
                            return input_value
        except:
            return 0

        return 0
    
    def set(self, name:str, keys:list[int,int]):

        """
        Register or add a new input to read out later.

        Args:
        - name (str): The name of the input to overwrite.
        - keys (list): Is a list of [key, method].
        - method: The way the input is pressed: [CLICKED, PRESSED, RELEASE].

        Returns:
        - True if registration was successful.
        - False if something went wrong.

        If the variable autosave is True the new input is automatically saved and loaded.

        Example:
        ```
        self.input.set("move_left",[[KEY_D,PRESSED],[KEY_ARROW_LEFT,PRESSED]])
        ```
        """

        # Sets key to new inputs
        try:
            self._registered_input[name] = key
            for key in self._registered_input[name]:
                if key[0][1] == _KEYBOARD:
                    self._keys[key[0][0]] = [False,False,False]

            if self.autosave:
                self.save()
                self.load()

            return True
        except:
            return False

    def save(self):

        """
        Saves registered inputs to file.

        Args:
        - no args are required.

        Returns:
        - True if save was successful.
        - False if something went wrong.

        Example:
        ```
        self.input.save()
        ```
        """

        # Save registered input in file
        try:
            with open(self.save_path,"w+") as f:
                json.dump(self._registered_input,f)
            return True
        except:
            return False

    def load(self):

        """
        Load registered inputs from file.

        Args:
        - no args are required.

        Returns:
        - True if load was successful.
        - False if something went wrong.

        Example:
        ```
        self.input.load()
        ```
        """

        # Load registered input in file
        try:
            with open(self.save_path,"r+") as f:
                self._registered_input = json.load(f)

                # Setting default value for keys
                for i in self._registered_input:
                    for key in self._registered_input[i]:
                        if key[0][1] == _KEYBOARD:
                            self._keys[key[0][0]] = [False,False,False]
            return True
        except:
            return False

    def _update(self) -> None:

        # Update all input devices
        for key in self._reset_keys.copy():
            self._keys[key][0] = False
            self._keys[key][2] = False
            self._reset_keys.remove(key)

        self.mouse._update()

        for joystick in self._reset_joy.copy():
            joystick._reset()
            self._reset_joy.remove(joystick)

    def _handle_key_event(self, event:pygame.Event):

        # Handel joystick button down event
        if event.type == pygame.KEYDOWN:
            self._keys[event.key] = [True,True,False]
            self._reset_keys.append(event.key)

        # Handel mouse button release event
        elif event.type == pygame.KEYUP:
            self._keys[event.key] = [False,False,True]
            self._reset_keys.append(event.key)

    def _handle_mouse_event(self, event:pygame.Event):
        # Handel joystick button down event
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.mouse.buttons[event.button-1] = [True,True,False]

        # Handel mouse button release event
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouse.buttons[event.button-1] = [False,False,True]

    def _handle_joy_event(self, event:pygame.Event):

        # joystick specification
        joy_index = event.joy
        joy_type = self._joystick_devices[joy_index].type
        
        # Handel joystick button click event
        if event.type == pygame.JOYBUTTONDOWN:
            button_index = event.button
            self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][button_index][0][0]] = [True,True,False]
            self._reset_joy.append(self._joystick_devices[joy_index])

        # Handel joystick button release event
        elif event.type == pygame.JOYBUTTONUP:
            button_index = event.button
            self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][button_index][0][0]] = [False,False,True]
            self._reset_joy.append(self._joystick_devices[joy_index])

        # Handel joystick axis movement event
        elif event.type == pygame.JOYAXISMOTION:
            axis_index = event.axis
            value = 0.0

            # Detect deadzone
            if abs(event.value) > self.joystick_dead_zone:
                value = max(min(event.value,1),-1)
            self._joystick_devices[joy_index].inputs[_JOYSTICK_AXIS_MAP[joy_type][axis_index][0]] = value

            # Direction inputs

            self._joystick_devices[joy_index].inputs[_JOYSTICK_DIRECTION_AXIS_MAP[joy_type][axis_index][0][0]] = -min(value,0.0)
            self._joystick_devices[joy_index].inputs[_JOYSTICK_DIRECTION_AXIS_MAP[joy_type][axis_index][1][0]] = max(value,0.0)

        elif event.type == pygame.JOYHATMOTION:

            # Xbox dpad hat event

            # DPAD LEFT
            if event.value[0] == -1:
                self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_LEFT[0]][0][0]] = [True,True,False]
                self._reset_joy.append(self._joystick_devices[joy_index])

            # DPAD RIGHT
            elif event.value[0] == 1:
                self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_RIGHT[0]][0][0]] = [True,True,False]
                self._reset_joy.append(self._joystick_devices[joy_index])

            # DPAD resets to default
            else:
                if self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_RIGHT[0]][0][0]][1] == True:
                    self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_RIGHT[0]][0][0]] = [False,False,True]
                elif self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_LEFT[0]][0][0]][1] == True:
                    self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_LEFT[0]][0][0]] = [False,False,True]
                self._reset_joy.append(self._joystick_devices[joy_index])

            # DPAD DOWN
            if event.value[1] == -1:
                self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_DOWN[0]][0][0]] = [True,True,False]
                self._reset_joy.append(self._joystick_devices[joy_index])

            # DPAD UP
            elif event.value[1] == 1:
                self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_UP[0]][0][0]] = [True,True,False]
                self._reset_joy.append(self._joystick_devices[joy_index])

            # DPAD resets to default
            else:
                if self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_UP[0]][0][0]][1] == True:
                    self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_UP[0]][0][0]] = [False,False,True]
                elif self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_DOWN[0]][0][0]][1] == True:
                    self._joystick_devices[joy_index].inputs[_JOYSTICK_BUTTON_MAP[joy_type][JOYSTICK_DPAD_DOWN[0]][0][0]] = [False,False,True]
                self._reset_joy.append(self._joystick_devices[joy_index])

    def _init_joysticks(self) -> None:

        # Creates joystick device to be used
        self._joystick_devices = []
        for joystick in range(pygame.joystick.get_count()):
            self._joystick_devices.append(self._Joystick(pygame.joystick.Joystick(joystick)))

    class _Mouse:
        def __init__(self) -> None:

            # Mouse variables
            self.position = [0,0]
            self.buttons = [
                [False,False,False],
                [False,False,False],
                [False,False,False],
                [False,False,False],
                [False,False,False]
            ]

        def _update(self) -> None:

            # Reset mouse input values
            self.buttons[0][0] = False
            self.buttons[0][2] = False
            self.buttons[1][0] = False
            self.buttons[1][2] = False
            self.buttons[2][0] = False
            self.buttons[2][2] = False

            # Get mouse values
            self.position = [pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]]
            mouse_pressed = pygame.mouse.get_pressed()
            self.buttons[0][1] = mouse_pressed[0]
            self.buttons[1][1] = mouse_pressed[1]
            self.buttons[2][1] = mouse_pressed[2]

        def get_pos(self) -> list[int,int]:

            """
            Returns mouse position relative to main window.

            Args:
            - no args are required.

            Returns:
            - List of [x mouse position (int), y mouse position (int)].

            Example:
            ```
            mouse_pos = self.input.mouse.get_pos()
            ```
            """

            # Getting mouse position
            return self.position

    class _Joystick:
        def __init__(self, joystick:pygame.joystick.JoystickType) -> None:

            # Joystick variables
            self.joystick = joystick
            self.name = joystick.get_name()
            if self.name == "Xbox 360 Controller":
                self.type = _XBOX_360_CONTROLLER
            elif self.name == "PS4 Controller":
                self.type = _PLAYSTATION_4_CONTROLLER
            elif self.name == "Sony Interactive Entertainment Wireless Controller":
                self.type = _PLAYSTATION_5_CONTROLLER
            elif self.name == "Nintendo Switch Pro Controller":
                self.type = _NINTENDO_SWITCH_PRO_CONTROLLER
            elif self.name == "Nintendo Switch Joy-Con (L)":
                self.type = _NINTENDO_SWITCH_JOYCON_CONTROLLER_L
            elif self.name == "Nintendo Switch Joy-Con (R)":
                self.type = _NINTENDO_SWITCH_JOYCON_CONTROLLER_R
            elif self.name == "Nintendo Switch Joy-Con (L/R)":
                self.type = _NINTENDO_SWITCH_JOYCON_CONTROLLER_L_R
            else:
                self.type = _XBOX_360_CONTROLLER
            self.battery = joystick.get_power_level()
            self.device_id = joystick.get_id()
            self.instance_id = joystick.get_instance_id()
            self.guid = joystick.get_guid()
            self.inputs = [
                [False,False,False],    # JOYSTICK_BUTTON_DOWN
                [False,False,False],    # JOYSTICK_BUTTON_RIGHT
                [False,False,False],    # JOYSTICK_BUTTON_UP
                [False,False,False],    # JOYSTICK_BUTTON_LEFT
                [False,False,False],    # JOYSTICK_DPAD_DOWN
                [False,False,False],    # JOYSTICK_DPAD_RIGHT
                [False,False,False],    # JOYSTICK_DPAD_UP
                [False,False,False],    # JOYSTICK_DPAD_LEFT
                0.0,                    # JOYSTICK_RIGHT_STICK_VERTICAL 
                0.0,                    # JOYSTICK_RIGHT_STICK_HORIZONTAL
                [False,False,False],    # JOYSTICK_RIGHT_STICK_CLICKED
                0.0,                    # JOYSTICK_LEFT_STICK_VERTICAL 
                0.0,                    # JOYSTICK_LEFT_STICK_HORIZONTAL
                [False,False,False],    # JOYSTICK_LEFT_STICK_CLICKED
                [False,False,False],    # JOYSTICK_BUTTON_SPEC_1
                [False,False,False],    # JOYSTICK_BUTTON_SPEC_2
                [False,False,False],    # JOYSTICK_RIGHT_BUMPER
                [False,False,False],    # JOYSTICK_LEFT_BUMPER
                0.0,                    # JOYSTICK_TRIGGER_R2
                0.0,                    # JOYSTICK_TRIGGER_L2
                0.0,                    # JOYSTICK_LEFT_STICK_UP
                0.0,                    # JOYSTICK_LEFT_STICK_DOWN
                0.0,                    # JOYSTICK_LEFT_STICK_LEFT
                0.0,                    # JOYSTICK_LEFT_STICK_RIGHT
                0.0,                    # JOYSTICK_RIGHT_STICK_UP
                0.0,                    # JOYSTICK_RIGHT_STICK_DOWN
                0.0,                    # JOYSTICK_RIGHT_STICK_LEFT
                0.0,                    # JOYSTICK_RIGHT_STICK_RIGHT
            ]

        def _reset(self) -> None:

            # Reset joystick button click and release values
            self.inputs[JOYSTICK_BUTTON_DOWN[0]][0] = False
            self.inputs[JOYSTICK_BUTTON_DOWN[0]][2] = False
            self.inputs[JOYSTICK_BUTTON_RIGHT[0]][0] = False
            self.inputs[JOYSTICK_BUTTON_RIGHT[0]][2] = False
            self.inputs[JOYSTICK_BUTTON_UP[0]][0] = False
            self.inputs[JOYSTICK_BUTTON_UP[0]][2] = False
            self.inputs[JOYSTICK_BUTTON_LEFT[0]][0] = False
            self.inputs[JOYSTICK_BUTTON_LEFT[0]][2] = False
            self.inputs[JOYSTICK_DPAD_DOWN[0]][0] = False
            self.inputs[JOYSTICK_DPAD_DOWN[0]][2] = False
            self.inputs[JOYSTICK_DPAD_RIGHT[0]][0] = False
            self.inputs[JOYSTICK_DPAD_RIGHT[0]][2] = False
            self.inputs[JOYSTICK_DPAD_UP[0]][0] = False
            self.inputs[JOYSTICK_DPAD_UP[0]][2] = False
            self.inputs[JOYSTICK_DPAD_LEFT[0]][0] = False
            self.inputs[JOYSTICK_DPAD_LEFT[0]][2] = False
            self.inputs[JOYSTICK_RIGHT_STICK[0]][0] = False
            self.inputs[JOYSTICK_RIGHT_STICK[0]][2] = False
            self.inputs[JOYSTICK_LEFT_STICK[0]][0] = False
            self.inputs[JOYSTICK_LEFT_STICK[0]][2] = False
            self.inputs[JOYSTICK_BUTTON_SPECIAL_1[0]][0] = False
            self.inputs[JOYSTICK_BUTTON_SPECIAL_1[0]][2] = False
            self.inputs[JOYSTICK_BUTTON_SPECIAL_2[0]][0] = False
            self.inputs[JOYSTICK_BUTTON_SPECIAL_2[0]][2] = False
            self.inputs[JOYSTICK_RIGHT_BUMPER[0]][0] = False
            self.inputs[JOYSTICK_RIGHT_BUMPER[0]][2] = False
            self.inputs[JOYSTICK_LEFT_BUMPER[0]][0] = False
            self.inputs[JOYSTICK_LEFT_BUMPER[0]][2] = False

        def _get_input(self, button:int, method:int) -> int|float:

            # Get joystick button value
            if type(self.inputs[button]) == list:
                return self.inputs[button][method]
            else:
                return self.inputs[button]

class Logger:
    def __init__(self,engine,delete_old_logs:bool=False) -> None:

        """
        Initialise the engines logging system.

        The logging system helps to log important information and collects error messages.

        Args:
        
        - engine (Engine): The engine to access specific variables.
        - delete_old_logs (bool)=False: If true there will only be the newest logfile.

        !!!This is only used internally by the engine and should not be called in a game!!!
        """

        # Engine variable
        self.engine = engine

        # Setting starting variables
        self.logpath = os.path.join("logs",f"{datetime.datetime.now().strftime('%d.%m.%y %H-%M-%S')}.log")
        self.last_logged_second = 0
        self.last_logged_message = ""
        self.repeat_log_times = 1
        self.time_format = "%d.%m.%y %H:%M:%S:%f"

        if self.engine.logging:
            # Trying to create logfile
            try:

                # Create empty file
                if not os.path.exists(self.logpath):
                    if not os.path.exists("logs"):
                        os.mkdir("logs")
                    if delete_old_logs:
                        for filename in glob.glob("logs/*.log"):
                            os.remove(filename)
                    with open(self.logpath,"+w") as file:
                        file.write("")
            except Exception as e:

                # Creating logfile failed, printing instead
                print(f"[Engine {datetime.datetime.now().strftime(self.time_format)[:-4]}]: Could not create logfile ({e})")

    # Different log variants
    def error(self,message:str):

        """
        Logs an error.

        Args:

        - message (str): Content to log.

        Mostly used by the engine internally but can also be used for logging other error messages

        Example:
        ```
        self.logger.error("The Exception")
        ```
        """

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        self._log("Error",f"{message} in [{fname} line: {exc_tb.tb_lineno}]")

    def warning(self,message:str):

        """
        Logs a warning.

        Args:

        - message (str): Content to log.

        Example:
        ```
        self.logger.warning("Memory almost 80% filled!")
        ```
        """

        self._log("Warning",str(message))

    def info(self,message:str):

        """
        Logs an info.

        Args:

        - message (str): Content to log.

        Example:
        ```
        self.logger.info("I am a duck)
        ```
        """

        self._log("Info",str(message))

    def _log(self,prefix:str,message:str):

        """
        Writes logged content to file.

        Args:

        - prefix (str): Importance of content 
        - message (str): Content to write to logfile.

        !!!This is only used internally by the engine and should not be called in a game!!!
        """

        if self.engine.logging:
            caller = "Engine"
            try:
                if self.last_logged_message == message:

                    # Message is repeating
                    if self.last_logged_second != datetime.datetime.now().second:
                        self.last_logged_second = datetime.datetime.now().second

                        # Writing to logfile: caller + time + repeating count + log type + message
                        with open(self.logpath,"+at") as file:
                            self.repeat_log_times += 1
                            file.write(f"[{caller} {datetime.datetime.now().strftime(self.time_format)[:-4]}]: {prefix} | x{self.repeat_log_times} | {message}\n")
                else:

                    # Storing last message and timestamp
                    self.last_logged_second = datetime.datetime.now().second
                    self.last_logged_message = message
                    self.repeat_log_times = 1

                    # Writing to logfile: caller + time + log type + message
                    with open(self.logpath,"+at") as file:
                        file.write(f"[{caller} {datetime.datetime.now().strftime(self.time_format)[:-4]}]: {prefix} | {message}\n")
            except Exception as e:
                print(f"[Engine {datetime.datetime.now().strftime(self.file_name_option)[:-4]}]: Could not log message ({message}) | ({e})")

class SaveManager():

    """A class for managing encrypted storage data."""

    def __init__(self,engine,path="data/saves/save") -> None:

        """
        Initialize the SaveManager object.

        Args:

        - engine: Engine instance.
        - path (str): Path to the file to be managed. Defaults to "data/saves/save".
        """

        self.engine = engine
        self.path = path
        self.encryption_key = b"z8IwBgA-gFs66DrrM7JHtXe0fl9OVtL3A8Q-xU1nmAA="

    def set_encryption_key(self,encryption_key:bytes) -> None:

        """
        Set the encryption key for the SaveManager.

        Args:

        - encryption_key (bytes): New encryption key to be set.
        """

        self.encryption_key = encryption_key

    def generate_encryption_key(self) -> bytes:

        """
        Generate a new encryption key using Fernet.

        Returns:

        - bytes: Generated encryption key.
        """

        return Fernet.generate_key()

    def set_save_path(self,path:str) -> None:

        """
        Set the save path for the SaveManager.

        Args:

        - path (str): New path to be set for saving data.
        """

        self.path = path

    def _encrypt(self,data:dict) -> bool:

        """
        !Used for internal functionality!
        Encrypt the provided data using Fernet encryption.

        Args:

        - data (dict): Data to be encrypted (as a dictionary).

        Returns:

        - bool: True if encryption is successful, False otherwise.
        """

        try:
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(bytes(json.dumps(data,ensure_ascii=True).encode("utf-8")))

            with open(self.path, 'wb') as file:
                file.write(encrypted_data)
        except Exception as e:
            self.engine.logger.error(e)

    def _decrypt(self) -> bool|dict:

        """
        !Used for internal functionality!
        Decrypt the data in the file specified by the path using Fernet decryption.

        Returns:

        - bool | dict: Decrypted data as a dictionary if successful, False otherwise.
        """

        try:
            with open(self.path, 'rb') as file:
                data = file.read()
            if data != b'':
                fernet = Fernet(self.encryption_key)
                return json.loads(fernet.decrypt(data))
            
        except Exception as e:
            self.engine.logger.error(e)

        return False

    def save(self,key,value) -> bool:

        """
        Save data to the file using a specified key-value pair.

        Args:

        - key: Key for the data.
        - value: Value to be saved corresponding to the key.

        Returns:

        - bool: True if saving is successful, False otherwise.
        """

        try:
            data = self._decrypt()
            if data != False:
                data[key] = value
            else:
                data = {}
            self._encrypt(data)
            return True
        except Exception as e:
            self.engine.logger.error(e)

        return False

    def load(self,key,default=None) -> any:

        """
        Load data from the file using the specified key.

        Args:

        - key: Key to retrieve data.
        - default: If key is not found, default will be returned instead.

        Returns:

        - any: Retrieved value corresponding to the key, or default value if not found.
        """

        if os.path.exists(self.path):
            try:
                data = self._decrypt()
                if data != False:
                    if key in data:
                        return data[key]
                    else:
                        return default
            except Exception as e:
                self.engine.logger.error(e)
        else:
            return default

    def backup(self,backup_path:str="data/saves/backup"):

        """
        Create a backup of the current save file.

        Args:

        - backup_path (str): Path to store the backup file. Defaults to "data/saves/backup".
        """

        shutil.copyfile(
            self.path,
            os.path.join(backup_path,f'{os.path.split(self.path)[-1]}-{datetime.datetime.now().strftime("%d.%m.%y %H-%M-%S")}')
            )

class Window:
    def __init__(self,engine,set_window_size=None,fullscreen=False,resizable=True,windowless=False,window_centered=True,vsync=False,window_name="Frostlight Engine",mouse_visible=True,color_depth=24) -> None:

        """
        Initialise the engines window system.

        The window system manages all window events and rendering.

        Args:

        - engine (Engine): The engine to access specific variables.
        - set_window_size (list)=None: Size of window.
        - fullscreen (bool)=False: Sets windows fullscreen mode.
        - resizable (bool)=True: Sets windows resizability.
        - windowless (bool)=False: Removes window interaction menu at the top.
        - window_centered (bool)=True: Sets window centered state.
        - vsync (bool)=False: Sets vsync state.
        - window_name (str)="Frostlight Engine": Default name to display.
        - mouse_visible (bool)=True: mouses visibility state.
        - color_depth (int)=24: Window color depth.

        !!!This is only used internally by the engine and should not be called in a game!!!
        """

        # Engine Variable
        self.engine = engine

        # Setting startup variables
        self.windowless = windowless
        self.window_centered = window_centered
        self.vsync = vsync
        self.color_depth = color_depth
        self.fullscreen = fullscreen
        self.window_name = window_name
        self.mouse_visible = mouse_visible
        self.window_size = set_window_size
        self.resizable = resizable

    def _create(self):

        """
        Creates main window instance.

        Args:

        - no args are required.

        !!!This is only used internally by the engine and should not be called in a game!!!
        """

        if not self.windowless:
            pygame.display.init()

            # Center window
            if self.window_centered:
                os.environ['SDL_VIDEO_CENTERED'] = '1'
            else:
                os.environ['SDL_VIDEO_CENTERED'] = '0'

            # Create window
            display_size = [int(pygame.display.Info().current_w),int(pygame.display.Info().current_h)]
            if self.fullscreen: 

                # Fullscreen window
                self.main_surface = pygame.display.set_mode(display_size,pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN,vsync=self.vsync,depth=self.color_depth)
            else:

                # Calculate fitting window size
                if self.window_size == None:
                    self.window_size = [display_size[0],display_size[1]*0.94]

                if self.resizable:

                    # Resizable window
                    self.main_surface = pygame.display.set_mode(self.window_size,pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE,vsync=self.vsync,depth=self.color_depth)
                else: 

                    # Fixed size window
                    self.main_surface = pygame.display.set_mode(self.window_size,pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.NOFRAME,vsync=self.vsync,depth=self.color_depth)

            # Change window attributes
            pygame.display.set_caption(self.window_name)
            pygame.mouse.set_visible(self.mouse_visible)

    def render(self,sprite:pygame.Surface,pos:list[int,int] | pygame.Rect):

        """
        Renders a sprite to the main window.

        Args:

        - sprite (pygame.Surface): The sprite to render.
        - pos (list[int,int]): The position to render the sprite to.

        Example:
        ```
        self.window.render(player_sprite,player_pos)
        ```
        """

        # Renders sprite to main window
        self.main_surface.blit(sprite,pos)

    def resize(self,new_window_size:list[int,int]):

        """
        Resizes the main window.

        Args:

        - new_window_size (list[int,int]): The new window size.

        Example:
        ```
        self.window.resize([600,600])
        ```
        """

        # Resize window to specified size        
        self.window_size = new_window_size

        if self.resizable:

            # Resizable window 
            self.main_surface = pygame.display.set_mode(self.window_size,pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE,vsync=self.vsync,depth=self.color_depth)
        else: 

            # Fixed size window
            self.main_surface = pygame.display.set_mode(self.window_size,pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.NOFRAME,vsync=self.vsync,depth=self.color_depth)

    def set_fullscreen(self,fullscreen:bool):

        """
        Changes window fullscreen state.

        Args:

        - fullscreen (bool): Fullscreen state.

        Example:
        ```
        self.window.set_fullscreen(True)
        ```
        """

        # Set fullscreen variable
        self.fullscreen = fullscreen
        pygame.display.quit()
        self._create()

    def toggle_fullscreen(self):

        """
        Toggles window fullscreen state.

        Args:

        - no args are required.

        Example:
        ```
        self.window.toggle_fullscreen()
        ```
        """

        # Set Fullscreen variable to opposite truth value
        self.set_fullscreen(not(self.fullscreen))

    def set_name(self,name:str="") -> None:

        """
        Set a window name.

        Args:

        - name (str)="": New window name.

        Example:
        ```
        self.window.set_name("new game")
        ```
        """

        # Renaming the displayed window title
        pygame.display.set_caption(str(name))

    def get_fps(self) -> int:

        """
        Returns games fps value.

        Args:

        - no args are required.

        Returns:

        - FPS value as integer.

        Example:
        ```
        self.window.set_name(self.window.get_fps())
        ```
        """

        # Returning frames per second as integer
        return int(min(self.engine.clock.get_fps(),99999999))
    
    def fill(self,color:list[int,int,int]) -> None:

        """
        Fills window with a color.

        Args:

        - color (list[int,int,int]): Color the window is filled with.

        Example:
        ```
        self.window.fill([3,13,36])
        ```
        """

        # Fills the screen with a solid color
        self.main_surface.fill(color)
    
    def get_size(self) -> list[int,int]:

        """
        Returns window size as list.

        Args:

        - no args are required.

        Returns:

        - Window size as list of integers.

        Example:
        ```
        print(self.window.get_size())
        ```
        """

        # Returning window size as a list of integers
        return self.window_size


class Engine:
    def __init__(self,
                 catch_error:bool=True,
                 color_depth:int=16,
                 delete_old_logs:bool=False,
                 fps:int=0,
                 fullscreen:bool=False,
                 game_version:str="1.0",
                 language:str="en",
                 logging:bool=True,
                 mouse_visible:bool=True,
                 nowindow:bool=False,
                 resizable:bool=True,
                 sounds:bool=True,
                 vsync:bool=False,
                 window_centered:bool=True,
                 window_name:str="New Game",
                 window_size:list=None):

        # initialize all modules
        pygame.init()
        pygame.joystick.init()
        if sounds:
            pygame.mixer.pre_init(44100,-16,2,512)

        # Boolean variables go here
        self.catch_error = catch_error
        self.logging = logging
        self.run_game = True
        self.sounds = sounds

        # Integer and float variables go here
        self.fps = fps
        self.delta_time = 1
        self.last_time = time.time()

        # String variables go here
        self.engine_version = "1.1.1"
        self.game_state = "intro"
        self.game_version = game_version
        self.language = language

        # List variables go here
        self.display_update_rects = []

        # Object variables go here
        self.clock = pygame.time.Clock()
        self._builder = Builder(self)
        self.logger = Logger(self,delete_old_logs)
        self.input = Input(self)
        self.save_manager = SaveManager(self,os.path.join("data","saves","save"))
        self.window = Window(self,window_size,fullscreen,resizable,nowindow,window_centered,vsync,window_name,mouse_visible,color_depth)

        # Object processing go here
        self.window._create()
        pygame.event.set_allowed([pygame.QUIT,
                                  pygame.WINDOWMOVED, 
                                  pygame.VIDEORESIZE, 
                                  pygame.KEYDOWN,
                                  pygame.KEYUP,
                                  pygame.MOUSEBUTTONDOWN,
                                  pygame.MOUSEBUTTONUP, 
                                  pygame.MOUSEMOTION,
                                  pygame.JOYBUTTONUP, 
                                  pygame.JOYBUTTONDOWN, 
                                  pygame.JOYAXISMOTION, 
                                  pygame.JOYHATMOTION, 
                                  pygame.JOYDEVICEADDED, 
                                  pygame.JOYDEVICEREMOVED])

    def _get_events(self):
        self.clock.tick(self.fps)
        self.input._update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            # Window events
            elif event.type == pygame.WINDOWMOVED:
                self.last_time = time.time()
                self.delta_time = 0
                self.event_window_move([event.x,event.y])
                self.event_window_changed(event)
                self.event_event(event)

            elif event.type == pygame.VIDEORESIZE:
                if not self.window.fullscreen:
                    self.last_time = time.time()
                    self.delta_time = 0
                    self.window.resize([event.w,event.h])
                    self.event_window_resize([event.w,event.h])
                    self.event_window_changed(event)
                    self.event_event(event)

            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                self.input._handle_key_event(event)
                if event.key == pygame.K_F11:
                    self.window.toggle_fullscreen()
                    mode = "fullscreen"
                    if not self.window.fullscreen:
                        mode = "windowed"
                    self.event_window_mode_changed(mode)
                    self.event_window_changed(mode)
                self.event_keydown(event.key,event.unicode)
                self.event_event(event)

            elif event.type == pygame.KEYUP:
                self.input._handle_key_event(event)
                self.event_keyup(event.key,event.unicode)
                self.event_event(event)

            # Mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.input._handle_mouse_event(event)
                self.event_mouse_buttondown(event.button,event.pos)
                self.event_event(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.input._handle_mouse_event(event)
                self.event_mouse_buttonup(event.button,event.pos)
                self.event_event(event)

            # Mouse events
            elif event.type == pygame.MOUSEMOTION:
                self.event_event(event)

            # Joystick events
            elif event.type == pygame.JOYBUTTONDOWN:
                self.input._handle_joy_event(event)
                self.event_joystick_buttondown(event.button,event.joy,event.instance_id)
                self.event_event(event)

            elif event.type == pygame.JOYBUTTONUP:
                self.input._handle_joy_event(event)
                self.event_joystick_buttonup(event.button,event.joy,event.instance_id)
                self.event_event(event)

            elif event.type == pygame.JOYAXISMOTION:
                self.input._handle_joy_event(event)
                self.event_joystick_axismotion(event.joy,event.instance_id,event.axis,event.value)
                self.event_event(event)

            elif event.type == pygame.JOYHATMOTION:
                self.input._handle_joy_event(event)
                self.event_joystick_hatmotion(event.button)
                self.event_event(event)

            elif event.type == pygame.JOYDEVICEADDED:
                self.input._init_joysticks()
                self.event_joystick_added(event.device_index,event.guid)
                self.event_event(event)

            elif event.type == pygame.JOYDEVICEREMOVED:
                self.input._init_joysticks()
                self.event_joystick_removed(event.instance_id)
                self.event_event(event)

    def event_event(self,event):

        # Event function to overwrite on event
        """
        This function can be overwritten to react to every engine event.
        Event is called after the engine event.

        Args:

        - event: Data about the event.

        Example:
        ```
        def event_event(self,event):
            print(f"Engine event occurred: {event}")
        ```
        """


    def event_quit(self):

        # Event function to overwrite on quit
        """
        This function can be overwritten to react to the game quit event.
        Event is called before the game closes.

        Args:

        - No args are required.

        Example:
        ```
        def event_quit(self):
            print("game end")
        ```
        """

    def event_window_move(self,position:list[int,int]):

        # Event function to overwrite on window move
        """
        This function can be overwritten to react to the window move event.
        Event is called after the window moved.

        Args:

        - position (list[int,int]): Monitor position to where to window moved.

        Example:
        ```
        def event_window_move(self,position:list[int,int]):
            print(f"The window moved to: {position}")
        ```
        """

    def event_window_resize(self,size:list[int,int]):

        # Event function to overwrite on window resize
        """
        This function can be overwritten to react to the window resize event.
        Event is called after the window is resized.

        Args:

        - size (list[int,int]): New window size.

        Example:
        ```
        def event_window_resize(self,size:list[int,int]):
            print(f"The window was resized to: {size}")
        ```
        """

    def event_window_mode_changed(self,new_mode:str):

        # Event function to overwrite on window mode changed
        """
        This function can be overwritten to react to the mode change of the window.
        Event is called after the mode changed.

        Args:

        - new_mode (str): The window mode after the event

        Example:
        ```
        def event_window_mode_changed(self,new_mode:str):
            print(f"The window mode changed to: {new_mode}")
        ```
        """

    def event_window_changed(self,event):

        # Event function to overwrite on window changed
        """
        This function can be overwritten to react to a change of the window.
        Event is called after the change.

        Args:

        - event: Data about the event.

        Example:
        ```
        def event_window_changed(self,event):
            print(f"The window changed: {event}")
        ```
        """

    def event_keydown(self,key:int,unicode:str):

        # Event function to overwrite on keypress
        """
        This function can be overwritten to react to the keypress event.
        Event is called after a key is pressed.

        Args:

        - key (int): Index of pressed key.
        - unicode (str): Displayable unicode of key.

        Example:
        ```
        def event_keydown(self,key:int,unicode:str):
            print(f"Key {unicode} with id {key} was pressed")
        ```
        """

    def event_keyup(self,key:int,unicode:str):

        # Event function to overwrite on key release
        """
        This function can be overwritten to react to the key release event.
        Event is called after a key is released.

        Args:
        
        - key (int): Index of released key.
        - unicode (str): Displayable unicode of key.

        Example:
        ```
        def event_keyup(self,key:int,unicode:str):
            print(f"Key {unicode} with id {key} was released")
        ```
        """

    def event_mouse_buttondown(sefl,button:int,position:list[int,int]):

        # Event function to overwrite on mouse click
        """
        This function can be overwritten to react to a mouse click.
        Event is called after the mouse is clicked.

        Args:

        - button (int): Index of clicked button.
        - position (list[int,int]): Position the mouse was on when clicked.

        Example:
        ```
        def event_mouse_buttondown(sefl,button:int,position:list[int,int]):
            print(f"Mouse button {button} was pressed at position {position}}")
        ```
        """

    def event_mouse_buttonup(sefl,button:int,position:list[int,int]):

        # Event function to overwrite on mouse release
        """
        This function can be overwritten to react to a mouse button release.
        Event is called after the mouse button is released.

        Args:

        - button (int): Index of released button.
        - position (list[int,int]): Position the mouse was on when released.

        Example:
        ```
        def event_mouse_buttonup(sefl,button:int,position:list[int,int]):
            print(f"Mouse button {button} was released at position {position}}")
        ```
        """

    def event_joystick_buttondown(sefl,button:int,joystick_id:int,instance_id:int):

        # Event function to overwrite on joystick button click
        """
        This function can be overwritten to react to a joystick button press.
        Event is called after the joystick button press.

        Args:

        - button (int): Index of released button.
        - joystick_id (int): Index id of joystick object.
        - instance_id (int): Instance id of joystick object.

        Example:
        ```
        def event_joystick_buttondown(sefl,button:int,joystick_id:int,instance_id:int):
            print(f"Button {button} was pressed at joystick {joystick_id}")
        ```
        """

    def event_joystick_buttonup(sefl,button:int,joystick_id:int,instance_id:int):
        
        # Event function to overwrite on joystick button release
        """
        This function can be overwritten to react to a joystick button release.
        Event is called after the joystick button is released.

        Args:

        - button (int): Index of released button.
        - joystick_id (int): Index id of joystick object.
        - instance_id (int): Instance id of joystick object.

        Example:
        ```
        def event_joystick_buttonup(sefl,button:int,joystick_id:int,instance_id:int):
            print(f"Button {button} was released at joystick {joystick_id}")
        ```
        """
    
    def event_joystick_axismotion(sefl,joystick_id:int,instance_id:int,axis:int,value:float):
        
        # Event function to overwrite on joystick axis motion
        """
        This function can be overwritten to react to a joysticks axis motion.
        Event is called after the joystick axis motion.

        Args:

        - joystick_id (int): Index id of joystick object.
        - instance_id (int): Instance id of joystick object.
        - axis (int): Index of moved joystick axis.
        - value (float): Value of motion between -1.0 and 1.0.

        Example:
        ```
        def event_joystick_axismotion(sefl,joystick_id:int,instance_id:int,axis:int,value:int):
            print(f"Axis {axis} detected motion {value} at joystick {joystick_id}")
        ```
        """
    
    def event_joystick_hatmotion(self,joystick_id:int,instance_id:int,hat:int,value:int):
        
        # Event function to overwrite on joystick hat motion
        """
        This function can be overwritten to react to a joysticks hat motion.
        Event is called after the joystick hat motion.

        Args:

        - joystick_id (int): Index id of joystick object.
        - instance_id (int): Instance id of joystick object.
        - hat (int): Index of joystick hat.
        - value (int): Value of hat pressed: -1 or 0 or 1

        Example:
        ```
        def event_joystick_hatmotion(self,joystick_id:int,instance_id:int,hat:int,value:int):
            print(f"Hat {hat} detected motion {value} at joystick {joy_id}")
        ```
        """
    
    def event_joystick_added(self,device_index:int,guid:str):
        
        # Event function to overwrite on joystick connected
        """
        This function can be overwritten to react to a new joystick device registered.
        Event is called after the joystick is added.

        Args:

        - device_index (int): Index id of joystick object.
        - guid (int): Gamepad unique id.

        Example:
        ```
        def event_joystick_added(self,device_index:int,guid:str):
            print(f"Connected new joystick {guid} at {device_index}")
        ```
        """
    
    def event_joystick_removed(self,instance_id:int):
        
        # Event function to overwrite on joystick disconnected
        """
        This function can be overwritten to react to the removal of a registered joystick device.
        Event is called after the joystick is removed.

        Args:

        - instance_id (int): Instance id of joystick object.

        Example:
        ```
        def event_joystick_removed(self,instance_id:int):
            print(f"Joystick {instance_id} disconnected!!!")
        ```
        """

    def _engine_update(self):

        # Update that runs before normal update
        self.delta_time = time.time()-self.last_time
        self.last_time = time.time()

    def _engine_draw(self):

        # Draw that runs after normal draw
        pygame.display.update()

    def run(self):

        """
        This function starts the main game loop

        Args:

        - No args are required.

        Example:
        ```
        if __name__ == "__main__"
            game = Game()
            game.run()
        ```
        """

        # Starting game engine
        self.logger.info(f"Starting [Engine version {self.engine_version} | Game version {self.game_version}]")
        if self.catch_error:
            while self.run_game:

                # Main loop
                try:
                    self._get_events()
                    self._engine_update()
                    self.update()
                    self.draw()
                    self._engine_draw()
                except Exception as e:

                    # Error logging and catching
                    self.logger.error(e)
        else:
            while self.run_game:

                # Main loop
                self._get_events()
                self._engine_update()
                self.update()
                self.draw()
                self._engine_draw()

        # Ending game
        self.logger.info("Closed game")

    def quit(self):

        """
        This function closes the game loop

        Args:

        - No args are required.

        Example:
        ```
        i = 0
        while True:
            i += 1
            if i == 10:
                self.quit()
        ```
        """
        # trigger quit event
        self.event_quit()
        self.event_event(pygame.QUIT)
        
        # Quit game loop
        self.run_game = False
        

if __name__ == "__main__":

    # Parser arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pack", action="store_true")
    parser.add_argument("-b", "--build", action="store_true")
    parser.add_argument("-n", "--name", action="store_true")
    args = parser.parse_args()

    if args.pack:

        # Pack Engine for release
        engine = Engine(nowindow=True)
        engine._builder._pack_release()

    elif args.build:

        # Build game to EXE
        engine = Engine(nowindow=True)
        engine._builder._setup_game()
        engine._builder._create_exe()

    elif args.name: 

        # Setup new Project with name
        engine = Engine(nowindow=True)
        engine._builder._setup_game(args.name)

    else:

        # Setup new no name Project
        engine = Engine(nowindow=True)
        engine._builder._setup_game()