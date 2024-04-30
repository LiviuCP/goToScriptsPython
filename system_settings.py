import os
from os.path import expanduser

home_dir = expanduser("~") + "/"
fallback_dir = home_dir #directory used as fallback in case the current directory becomes unavailable (e.g. deleted externally)

assert os.path.isdir(fallback_dir), "Invalid fallback directory!"
