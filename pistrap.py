#!/usr/bin/python
from __future__ import print_function
from datetime import datetime
import os

# Main entry point for the application

build_details = {}

# Configure details of build
def init(build_details = {}):
    build_details['bootsize'] = "64M" # Boot partition size on RPI.
    build_details['size'] = 1000 # Size of image to create in MB. You will need to set this higher if you want a larger selection.
    t = datetime.utcnow()
    build_details['mydate'] = t.strftime("%Y%m%d")  
    build_details['image'] = "placeholder.img"
    build_details['password'] = "raspberry"
    build_details['choices'] = {}
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

def pickPackages(build_details = {}):
    # TODO - Pick choices from options.
    print ("Choose which of these packages you want installed")
    build_details['options'] = {}
    build_details['choices'] = {}
    
    build_details['options']['less'] = "A pager, you probably want this"
    build_details['options']['vim'] = "An editor, cooler than Nano"
    build_details['options']['screen'] = "Runs lots of stuff, in one terminal"
    build_details['options']['minicom'] = "A serial console"
    build_details['options']['zsh'] = "Probably the best shell ever"
    build_details['options']['htop'] = "A better system monitor"

    if build_details['choices'] != {}:
        print ("Selections Set. Installing additional software: " + build_details['choices'] + "...")
    else:
        print ("Installing default software set.") 
        
    print ("You are bootstrapping " + build_details['hostname'] + " with " + build_details['suite'] + " (" + build_details['arch'] + "), from " + build_details['deb_mirror'] + " into " + build_details['buildenv'] + ". Are you SURE you want to Continue?")
    
    build_details['image'] = build_details['buildenv'] + "/pistrap_" + build_details['suite'] + "_"+ build_details['arch'] + "_" + build_details['mydate'] + ".img"
    
    return build_details
    
def checkRequirements():
    # Check if root user
    if os.geteuid() != 0:
        print("ERROR: This tool must be run with superuser rights!") # Because debootstrap will create device nodes (using mknod) as well as chroot into the newly created system
        return True # TODO: True for now to test.
    else:
        return True
        
###############################################################################
#################TODO: CALL BASH SCRIPTS FROM OLD CODEBASE, EASIER#############
###############################################################################
###############################################################################
###############################################################################

def partitionDevice():
    print ("Partitioning...")
    # TODO: Implement
    return False
        
def mountDevice():
    print ("Mounting Partitions...")
    # TODO: Implement
    return False
        
# bootp is the boot partition. rootp is the partition that will hold rootfs.
def formatDevice():
    print ("Formatting Partitions ...")
    # TODO: Implement
    return False
    
def bootstrapDevice():
    print ("Bootstrapping new filesystem...")
    # To bootstrap our new system, we run debootstrap, passing it the target arch and suite, as well as a directory to work in.
    # FIXME: We do --no-check-certificate and --no-check-gpg to make raspbian work.
    # TODO:debootstrap --no-check-certificate --no-check-gpg --foreign --arch $arch $suite $rootfs $deb_mirror 2>&1

    print ("Second stage. Chrooting...")
    # To be able to chroot into a target file system, the qemu emulator for the target CPU needs to be accessible from inside the chroot jail.
    # TODO: cp /usr/bin/qemu-arm-static usr/bin/ &>
    # TODO: Second stage - Run Post-install scripts.
    return False
    
def configureBoot():
    # TODO: Implement
    print ("Configuring boot partition...")
    print ("Configuring bootloader...")
    #The system you have just created needs a few tweaks so you can use it.
    print ("Configuring fstab...")
    return False
    
def networking():
    #Configure networking for DHCP
    # TODO: Implement
    print ("Configuring Networking...")
    print ("Setting hostname to " + build_details['hostname'] + "...")
    print ("Configuring network adapters...")
    return False
    
def configureSystem():
    # TODO: Implement
    print ("Configuring System")

    # By default, debootstrap creates a very minimal system, so we will want to extend it by installing more packages.
    print ("Configuring sources.list...")
    # The (buggyish) analog audio driver for the SoC.
    print ("Configuring kernel modules...")
    # Will spawn consoles on USB serial adapter for headless use.
    print ("Configuring USB serial console...")
    print ("Configuring locales...") # TODO: Select keymap from full list?
    return False
    
def thirdStage():
    print ("Third stage. Installing packages...")
    
    #  TODO: Implement. Install things we need in order to grab and build firmware from github, and to work with the target remotely. Also, NTP as the date and time will be wrong, due to no RTC being on the board. This is important, as if you get errors relating to certificates, : the problem is likely due to one of two things. Either the time is set incorrectly on your Raspberry Pi, which you can fix by simply setting the time using NTP. The other possible issue is that you might not have the ca-certificates package installed, and so GitHub's SSL certificate isn't trusted.
    return False
    
def cleanUp():
    # Tidy up afterward
    print ("Cleaning up...")
    return False
    
def finalSetup():
    # TODO: Implement
    print ("Configuring RAM/GPU Split...")
    print ("Configuring Overclock...")

    print ("Configuring Locales...")
    print ("Configuring Time Zones...")
    print ("Configuring Keyboard...")

    print ("Configuring SSH...")
    return False

if __name__ == "__main__":
    if checkRequirements():
        build_details = init(build_details)
        build_details = getBuildroot(build_details)
        build_details = getType(build_details)
        build_details = getHostname(build_details)
        build_details = getPassword(build_details)
        build_details = pickPackages(build_details)
        
        partitionDevice()
        mountDevice()
        formatDevice()
        bootstrapDevice()
        configureBoot()
        configureSystem()
        networking()
        thirdStage()
        finalSetup()
        cleanUp()
        
        for k in build_details:
            print(str(k) + " : " + str(build_details[k]))
            
        # TODO: Call bash script with args?
