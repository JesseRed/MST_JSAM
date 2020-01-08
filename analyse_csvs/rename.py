
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from os import listdir, rename
from os.path import isfile, join


mypath = "./Data MST"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
for f in onlyfiles:
    rename(join(mypath,f),join(mypath,(f[0:6]+f[-4:])))