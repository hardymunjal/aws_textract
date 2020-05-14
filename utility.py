###################
# Developer: Hardik Munjal
###################
# Package Imports
import os
import pathlib

# Variables Declarations
BASE_PATH = str(pathlib.Path(__file__).parent)
print("Base path of project:", BASE_PATH)

if os.name == "nt":
    IMG_PATH = BASE_PATH+"\\data\\"
else:
    IMG_PATH = BASE_PATH+"/data/"
