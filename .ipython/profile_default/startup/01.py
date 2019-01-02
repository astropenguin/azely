# standard library
import re
import os
import sys
import time
import toml
from pathlib import Path
from datetime import datetime

# dependent packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy.coordinates import AltAz, EarthLocation
from dateutil.parser import parse

# azely
import azely