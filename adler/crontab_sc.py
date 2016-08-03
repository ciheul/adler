#!/usr/bin/python

import subprocess
import os


# LOCAL DEVELOPMENT
#os.chdir("/home/ciheul/Projects/inetscada/app/adler/hawk/water/images")
#subprocess.call(["wget","-P","/home/ciheul/Projects/inetscada/app/adler/hawk/water/images","http://10.212.0.10/CCTV/GLM/SWRO_001/CCTV1.jpg","-O","cctv.jpg"])

# PRODUCTION
os.chdir("/home/smartadmin/inetscada/app/glm/static/water/images")                
subprocess.call(["wget","-P","/home/smartadmin/inetscada/app/glm/static/water/images","http://10.212.0.10/CCTV/GLM/SWRO_001/CCTV1.jpg","-O","cctv.jpg"])
