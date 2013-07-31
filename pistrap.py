#!/usr/bin/python
from __future__ import print_function
from datetime import datetime
import os
import glob
import bottle
from bottle import Bottle, route, run, request, abort, view, template

app = Bottle()

# Configure details of build
def init(build_details = {}):
    try:
        if not 'bootsize' in build_details:
            build_details['bootsize'] = "64M" # Boot partition size on RPI.
        if not 'size' in build_details:    
            build_details['size'] = "1000" # Size of image to create in MB. You will need to set this higher if you want a larger selection.
        if not 'password' in build_details:
            build_details['password'] = "raspberry"
            
        t = datetime.now()
        build_details['mydate'] = t.strftime("%Y%m%d")  
        build_details['mytime'] = t.strftime("%H%M")
        build_details['image'] = "placeholder.img"
        build_details['device'] = "" # Build image
        
        print ("Starting build on " + build_details['mydate'] + " at " + build_details['mytime'] + ".") 
        return build_details
    except Exception as e:
        print("Error setting up build! : " + str(e))
        exit(1)
        
# Let the user type in the location to use as a buildroot. This should be an (empty) directory where you want the new system to be populated. This directory will reflect the root filesystem of the new system. Note that the host system is not affected in any way, and all modifications are restricted to the directory you have chosen.
def getBuildroot(build_details = {},buildenv = None):   
    try:
        if not buildenv:
            build_details['buildenv'] = "/root/build"
        else:
            build_details['buildenv'] = buildenv
            
        build_details['rootfs'] = build_details['buildenv'] + "/rootfs"
        build_details['bootfs'] = build_details['rootfs'] + "/boot"

        return build_details
    except Exception as e:
        print("Error setting buildroot! : " + str(e))
        exit(1)
        
# Debian armel, or raspbian armhf.
def getType(build_details = {}, arch = None, suite = None,dist=None):
    try:
        if not arch:
            build_details['arch'] = "armhf"
        else:
            build_details['arch'] = arch
            
        if not suite:
            build_details['suite'] = "wheezy"
        else:
            build_details['suite'] = suite

        if not dist:
            build_details['dist'] = "raspbian"
        else:
            build_details['dist'] = dist

        if build_details['arch'] == "armhf" and build_details['dist'] == "raspbian" and build_details['suite'] == "wheezy":
            build_details['deb_mirror'] = "http://archive.raspbian.org/raspbian"
        elif build_details['arch'] == "armel" and build_details['dist'] == "debian" and build_details['suite'] == "wheezy":
            build_details['deb_mirror'] = "http://http.debian.net/debian"
        else:
            print("FATAL: Unsupported dist/arch/suite combination selected!")
            exit(1)
        return build_details
    except Exception as e:
        print("Error setting build type! : " + str(e))
        exit(1)
        
# Let the user type in the chosen target hostname
def getHostname(build_details = {}, hostname = None):
    try:
        if not hostname:
            build_details['hostname'] = "raspberry"
        else:
            build_details['hostname'] = hostname
            
        return build_details
    except Exception as e:
        print("Error setting hostname! : " + str(e))
        exit(1)
        
# Let the user type in the chosen root password
def getPassword(build_details = {}, password = None):
    if not password:
        build_details['password'] = "raspberry"
    else:
         build_details['password'] = password
         
    return build_details

def processBuild(build_details = {}):
    try:
        print ("You are bootstrapping " + build_details['hostname'] + " with " + build_details['suite'] + " (" + build_details['arch'] + "), from " + build_details['deb_mirror'] + " into " + build_details['buildenv'] + ".")
        
        build_details['image'] = build_details['buildenv'] + "/pistrap_" + build_details['suite'] + "_"+ build_details['arch'] + "_" + build_details['mydate'] + "_" + build_details['mytime'] + ".img"
                    
        # Call bash script with args
            
        build_details['command'] = "sudo ./pistrap_mini.sh" + " " + build_details['hostname'] + " " + build_details['dist'] + " " + build_details['deb_mirror'] + " " + build_details['bootsize'] + " " + build_details['buildenv'] + " "  + build_details['suite'] + " " + build_details['password'] + " " + build_details['arch'] + " " + build_details['size'] + " 2>&1 | tee -a /var/log/pistrap.log"

        print ("\nResulting Command:\n")
        print(build_details['command'])

        os.system(build_details['command'])
        
        return build_details
    except Exception as e:
        print("Error processing build! : " + str(e))
        exit(1)

def checkRequirements():
    try:
        # Check if root user
        if os.geteuid() != 0:
            print("ERROR: This tool must be run with superuser rights.") # Because debootstrap will create device nodes (using mknod) as well as chroot into the newly created system
            return False
        else:
            return True
    except Exception as e:
        print("ERROR: This tool must be run with superuser rights.")
        return False
        
@app.route('/', method='GET')
@view('submit')
def index():
    builds = {}
    
    try:
        for files in os.listdir("/root/build"):
            if files.startswith("pistrap_") and files.endswith(".img"):
                builds[files] = "/root/build/" + files
    except Exception as e:
        print ("Exception while listing image files: " + str (e))
        
    return template('submit', builds=builds)

@app.route('/build', method='POST')
def build():
    
    build_details = {}
    
    try:
        if request.forms.get('arch'):
            arch = request.forms.get('arch')
            build_details['arch'] = arch
        else:
            return bottle.HTTPResponse(status=400, body="Missing arch paramater")
        if request.forms.get('suite'):
            suite = request.forms.get('suite')
            build_details['suite'] = suite
        else:
            return bottle.HTTPResponse(status=400, body="Missing suite paramater")
        if request.forms.get('dist'):
            dist = request.forms.get('dist')
            build_details['dist'] = dist
        else:
            return bottle.HTTPResponse(status=400, body="Missing dist paramater")
        if request.forms.get('hostname'):
            hostname = request.forms.get('hostname')
            build_details['hostname'] = hostname
        else:
            return bottle.HTTPResponse(status=400, body="Missing hostname paramater")
        if request.forms.get('password'):
            password = request.forms.get('password')
            build_details['password'] = password
        else:
            return bottle.HTTPResponse(status=400, body="Missing password paramater")
    except Exception as e:
        return bottle.HTTPResponse(status=400, body="Error when processing paramaters: " + str(e))
        
    try:
        if checkRequirements():
            build_details = init(build_details)
            build_details = getBuildroot(build_details,None)
            build_details = getType(build_details,arch,suite,dist)
            build_details = getHostname(build_details,hostname)
            build_details = getPassword(build_details,password)
            build_details = processBuild(build_details)
            return "Image at: " + build_details['image'] + " created by running: " + build_details['command']
        else:
            return bottle.HTTPResponse(status=401, body="ERROR: This tool must be run with superuser rights.")
    except Exception as e:
        return bottle.HTTPResponse(status=500, body=str(e))

# Main entry point for the application
if __name__ == "__main__":
    try:
        run(app,host='localhost', port=8080, debug=True)
    except Exception as e:
        print("Error running app! : " + str(e))
