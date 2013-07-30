#!/usr/bin/python
from __future__ import print_function
from datetime import datetime
import os

# Main entry point for the application

build_details = {}

# Configure details of build
def init(build_details = {}):
    build_details['bootsize'] = "64M" # Boot partition size on RPI.
    build_details['size'] = "1000" # Size of image to create in MB. You will need to set this higher if you want a larger selection.
    t = datetime.utcnow()
    build_details['mydate'] = t.strftime("%Y%m%d")  
    build_details['image'] = "placeholder.img"
    build_details['password'] = "raspberry"
    build_details['device'] = "" # Build image
    print ("Starting build on " + build_details['mydate'] + ".") 
    return build_details

# Let the user type in the location to use as a buildroot. This should be an (empty) directory where you want the new system to be populated. This directory will reflect the root filesystem of the new system. Note that the host system is not affected in any way, and all modifications are restricted to the directory you have chosen.
def getBuildroot(build_details = {},buildenv = None):   

    if not buildenv:
        build_details['buildenv'] = "/root/build"
    else:
        build_details['buildenv'] = buildenv
        
    build_details['rootfs'] = build_details['buildenv'] + "/rootfs"
    build_details['bootfs'] = build_details['rootfs'] + "/boot"

    if build_details['buildenv']:
        print ("Working in build root: " + build_details['buildenv'] + "...")
    return build_details

# Debian armel, or raspbian armhf.
def getType(build_details = {}, arch = None, suite = None,dist=None):

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
        build_details['dist'] = suite

    if build_details['arch'] == "armhf" and build_details['dist'] == "raspbian" and build_details['suite'] == "wheezy":
        build_details['deb_mirror'] = "http://archive.raspbian.org/raspbian"
    elif build_details['arch'] == "armel" and build_details['dist'] == "debian" and build_details['suite'] == "wheezy":
        build_details['deb_mirror'] = "http://http.debian.net/debian"
    else:
        print("WARNING: Unsupported dist/arch/suite combination selected!")

    print ("Setting up for " + build_details['arch'] + "....")
    return build_details

# Let the user type in the chosen target hostname
def getHostname(build_details = {}, hostname = None):

    if not hostname:
        build_details['hostname'] = "raspberry"
    else:
        build_details['hostname'] = hostname
        
    print ("Setting hostname: " + build_details['hostname'] +"...")
    return build_details

# Let the user type in the chosen root password
def getPassword(build_details = {}, password = None):
    if not password:
        build_details['password'] = "raspberry"
    else:
         build_details['password'] = password
         
    print ("Setting root password: " + build_details['password'] + "...") 
    return build_details

def processBuild(build_details = {}):

    print ("You are bootstrapping " + build_details['hostname'] + " with " + build_details['suite'] + " (" + build_details['arch'] + "), from " + build_details['deb_mirror'] + " into " + build_details['buildenv'] + ".")
    
    build_details['image'] = build_details['buildenv'] + "/pistrap_" + build_details['suite'] + "_"+ build_details['arch'] + "_" + build_details['mydate'] + ".img"
    
    print ("\nSummary:\n")
    for k in build_details:
        print(str(k) + " : " + str(build_details[k]))
        
    # TODO: Call bash script with args?
    
    """
    $hostname=$1
    $dist=$2
    $deb_mirror=$3
    $image=$4
    $bootsize=$5
    $mydate=$6
    $buildenv=$7
    $bootfs=$8
    $rootfs=$9
    $suite=$10
    $password=$11
    $arch=$12
    $size=$13
    """
    
    build_details['command'] = "sudo ./pistrap.sh" + " " + build_details['hostname'] + " " + build_details['dist'] + " " + build_details['deb_mirror'] + " " + build_details['image'] + " " + build_details['bootsize'] + " " + build_details['mydate'] + " " + build_details['buildenv'] + " " + build_details['bootfs'] + " " + build_details['rootfs'] + " " + build_details['suite'] + " " + build_details['password'] + " " + build_details['arch'] + " " + build_details['size'] + " " + build_details['device']

    print ("\nResulting Command:\n")
    print(build_details['command'])

    os.system(build_details['command'])
    
    return build_details
    
def checkRequirements():
    # Check if root user
    if os.geteuid() != 0:
        print("ERROR: This tool must be run with superuser rights!") # Because debootstrap will create device nodes (using mknod) as well as chroot into the newly created system
        return True # TODO: True for now to test.
    else:
        return True

if __name__ == "__main__":
    if checkRequirements():
        build_details = init(build_details)
        build_details = getBuildroot(build_details)
        build_details = getType(build_details)
        build_details = getHostname(build_details)
        build_details = getPassword(build_details)
        build_details = processBuild(build_details)
