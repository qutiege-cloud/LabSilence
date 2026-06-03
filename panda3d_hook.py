import os
import sys

if hasattr(sys, '_MEIPASS'):
    panda3d_dir = os.path.join(sys._MEIPASS, 'panda3d')
    if os.path.isdir(panda3d_dir):
        os.add_dll_directory(panda3d_dir)
    os.add_dll_directory(sys._MEIPASS)
