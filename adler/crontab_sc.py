#!/usr/bin/python

import subprocess
import os

os.chdir("/home/ciheul/Downloads/wget_p_hour")
subprocess.call(["wget","-P","/home/ciheul/Downloads/wget_p_hour","https://i.ytimg.com/vi/s5y-4EpmfRQ/maxresdefault.jpg","-O","cctv.jpg"])


os.chdir("/home/ciheul/Downloads/wget_p_hour")
subprocess.call(["wget","-P","/home/ciheul/Downloads/wget_p_hour/tamplates","https://i.ytimg.com/vi/s5y-4EpmfRQ/maxresdefault.jpg","-O","cctv.jpg"])

#subprocess.call(["wget","-P","~/Projects/inetscada/app/adler/hawk/water/images","http://10.212.0.10/CCTV/GLM/SWRO_001/CCTV1.jpg","-O","cctv.jpg"])
