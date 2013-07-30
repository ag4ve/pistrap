#!/bin/bash

#Copyright (c) 2012
#James Bennet <github@james-bennet.com>, Klaus M Pfeiffer <klaus.m.pfeiffer@kmp.or.at>, "Super" Nathan Weber <supernathansunshine@gmail.com>

#Permission to use, copy, modify, and/or distribute this software for
#any purpose with or without fee is hereby granted, provided that the
#above copyright notice and this permission notice appear in all copies.

#THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
#WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
#OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE
#FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
#DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
#IN AN CTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
#OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

#******** GENERAL NOTES ********
# pistrap.sh - Builds your own minimal (i.e. no GUI) RaspberryPi SD-card image. Images will fit in 1gb and take about 15m (on my crummy connection)
# The root password on the created image will be "raspberry".

# I take the "QEMU/debootstrap approach". See: http://wiki.debian.org/EmDebian/CrossDebootstrap and http://wiki.debian.org/EmDebian/DeBootstrap
# Based on work by Klaus M Pfeiffer at http://blog.kmp.or.at/2012/05/build-your-own-raspberry-pi-image/

# Report any issues using github.

# To test your image on x86, follow http://xecdesign.com/qemu-emulating-raspberry-pi-the-easy-way/

#******** PACKAGING NOTES ********
# I package for debian, but any dist that has debootstrap should work, as the apt-get's are done inside the debian chroots.

# Use passed args

hostname="${1}"
dist="${2}"
deb_mirror="${3}"
bootsize="${4}"
buildenv="${5}"
suite="${6}"
password="${7}"
arch="${8}"
size="${9}"

# Set defaults otherwise

image=""
device=""
mydate=`date +%Y%m%d`

if [ -z "$1" ]
  then
    hostname="raspberry"
fi

if [ -z "$1" ]
  then
    hostname="raspberry"
fi

if [ -z "$2" ]
  then
    deb_mirror="http://archive.raspbian.org/raspbian"
fi

if [ -z "$3" ]
  then
    dist="raspbian"
fi

if [ -z "$4" ]
  then
    bootsize="64M" # Boot partition size on RPI.
fi

if [ -z "$5" ]
  then
    buildenv="/root/build"
fi

if [ -z "$6" ]
  then
    suite="wheezy"
fi

if [ -z "$7" ]
  then
    password="raspberry"
fi

if [ -z "$8" ]
  then
    arch="armhf"
fi

if [ -z "$9" ]
  then
    size="1000" # Size of image to create in MB. You will need to set this higher if you want a larger selection.
fi

# Derived variables
bootfs="${rootfs}/boot"
rootfs="${buildenv}/rootfs"

function main
{
partitionDevice
mountDevice
formatDevice
bootstrapDevice
configureBoot
configureSystem
networking
thirdStage
finalSetup
cleanUp
}

function partitionDevice
{
if [ "$device" == "" ]; then
  mkdir -p $buildenv
  image="${buildenv}/pistrap_${suite}_${arch}_${mydate}.img"
  dd if=/dev/zero of=$image bs=1MB count=$size
  device=`losetup -f --show $image`
else
  dd if=/dev/zero of=$device bs=512 count=1
fi

fdisk $device << EOF
n
p
1

+$bootsize
t
c
n
p
2


w
EOF
}

function mountDevice
{
if [ "$image" != "" ]; then
  losetup -d $device
  device=`kpartx -va $image | sed -E 's/.*(loop[0-9])p.*/\1/g' | head -1`
  device="/dev/mapper/${device}"
  bootp=${device}p1
  rootp=${device}p2
else
  if ! [ -b ${device}1 ]; then
    bootp=${device}p1
    rootp=${device}p2
    if ! [ -b ${bootp} ]; then
      exit 1
    fi
  else
    bootp=${device}1
    rootp=${device}2
  fi
fi
}

function formatDevice
{
mkfs.vfat $bootp # Boot partition
mkfs.ext4 $rootp # Partition that will hold rootfs.

mkdir -p $rootfs
}

function bootstrapDevice
{
mount $rootp $rootfs
cd $rootfs

# To bootstrap our new system, we run debootstrap, passing it the target arch and suite, as well as a directory to work in.
# FIXME: We do --no-check-certificate and --no-check-gpg to make raspbian work.
debootstrap --no-check-certificate --no-check-gpg --foreign --arch $arch $suite $rootfs $deb_mirror

# To be able to chroot into a target file system, the qemu emulator for the target CPU needs to be accessible from inside the chroot jail.
cp /usr/bin/qemu-arm-static usr/bin/
# Second stage - Run Post-install scripts.
LANG=C chroot $rootfs /debootstrap/debootstrap --no-check-certificate --no-check-gpg --second-stage
}

function configureBoot
{
mount $bootp $bootfs

echo "dwc_otg.lpm_enable=0 console=ttyUSB0,115200 kgdboc=ttyUSB0,115200 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 rootwait" > boot/cmdline.txt

#The system you have just created needs a few tweaks so you can use it.
echo "proc            /proc           proc    defaults        0       0
/dev/mmcblk0p1  /boot           vfat    defaults        0       0
" > etc/fstab
}

function networking
{
#Configure networking for DHCP
echo $hostname > etc/hostname
echo "127.0.1.1\t$hostname\n" >> etc/hosts

echo "auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
" > etc/network/interfaces
}

function configureSystem
{
# By default, debootstrap creates a very minimal system, so we will want to extend it by installing more packages.
echo "deb $deb_mirror $suite main contrib non-free
" > etc/apt/sources.list

# The (buggyish) analog audio driver for the SoC.
echo "vchiq
snd_bcm2835
" >> etc/modules


echo "pcm.mmap0 {
    type mmap_emul;
    slave {
      pcm \"hw:0,0\";
    }
}

pcm.!default {
  type plug;
  slave {
    pcm mmap0;
  }
}
" > etc/asound.conf

# Will spawn consoles on USB serial adapter for headless use.
echo "T0:23:respawn:/sbin/getty -L ttyUSB0 115200 vt100" >> etc/inittab

echo "console-common	console-data/keymap/policy	select	Select keymap from full list
console-common	console-data/keymap/full	select	de-latin1-nodeadkeys
" > debconf.set
}

function thirdStage
{
# Install things we need in order to grab and build firmware from github, and to work with the target remotely. Also, NTP as the date and time will be wrong, due to no RTC being on the board. This is important, as if you get errors relating to certificates, then the problem is likely due to one of two things. Either the time is set incorrectly on your Raspberry Pi, which you can fix by simply setting the time using NTP. The other possible issue is that you might not have the ca-certificates package installed, and so GitHub's SSL certificate isn't trusted.

echo "#!/bin/bash
debconf-set-selections /debconf.set
rm -f /debconf.set
apt-get -qq update
apt-get -qq -y install --no-install-recommends git-core binutils ca-certificates locales console-common ntp ntpdate fake-hwclock openssh-server wget module-init-tools avahi-daemon cpufrequtils sysfsutils haveged rng-tools
wget  -q http://raw.github.com/Hexxeh/rpi-update/master/rpi-update -O /usr/bin/rpi-update
chmod +x /usr/bin/rpi-update
mkdir -p /lib/modules/3.1.9+
mkdir -p /lib/modules/3.6.11+
touch /boot/start.elf
rpi-update
echo \"root:$password\" | chpasswd
sed -i -e 's/KERNEL\!=\"eth\*|/KERNEL\!=\"/' /lib/udev/rules.d/75-persistent-net-generator.rules
apt-get update && yes | apt-get upgrade
rm -f /etc/udev/rules.d/70-persistent-net.rules
rm -f third-stage
" > third-stage
chmod +x third-stage
LANG=C chroot $rootfs /third-stage

# Is this redundant?
echo "deb $deb_mirror $suite main contrib non-free
" > etc/apt/sources.list
}

function cleanUp
{
# Tidy up afterward
echo "#!/bin/bash
apt-get -qq clean
rm -f cleanup
" > cleanup
chmod +x cleanup
LANG=C chroot $rootfs /cleanup

cd

umount $bootp
umount $rootp

if [ "$image" != "" ]; then
  kpartx -d $image
fi
}

function finalSetup
{

# TODO: Memory split - gpu_mem in /boot/config.txt
# GPU memory in megabytes ARM gets the remaining memory. Min 16. Default 64 
# We dont care as want to run headless.

echo "gpu_mem=16" >> boot/config.txt
echo "gpu_mem_256=16" >> boot/config.txt
echo "gpu_mem_512=16" >> boot/config.txt

echo "# High, but stable overclock as max freq, Minor overclock as min freq
arm_freq = 930 # Default 700mhz
core_freq = 450 # Default 250mhz
sdram_freq = 500 # Frequency of SDRAM in MHz. Default 400mhz
arm_freq_min = 800 # Minimum value of arm_freq used for dynamic clocking. Default 700mhz
core_freq = 450 # Default 250mhz
sdram_freq_min = 450 # Minimum value of sdram_freq used for dynamic clocking. Default 400mhz
# The ondemand governor usually only kicks in at 95% load, we want to stay at max.
force_turbo = 1 - TODO: Set off as may void warranty?
" >>  boot/config.txt

# Localisation
dpkg-reconfigure locales
dpkg-reconfigure tzdata
dpkg-reconfigure keyboard-configuration
invoke-rc.d keyboard-setup start

# Enable SSH
insserv avahi-daemon
update-rc.d ssh enable
}

#RUN
main
