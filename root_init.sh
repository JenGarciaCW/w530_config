#!/bin/sh

# Check number of arguments
#	root_init {username} 
if [ "$#" -ne 1 ] || ! [ -d "$1" ]; then
  echo "Usage: $0 username " >&2
  exit 1
fi

# Install sudo and add user name to sudoers list
USER = $1
apt-get install sudo
echo "$1 ALL=(ALL:ALL) ALL" | sudo EDITOR='tee -a' visudo 

# Add needed sources.list repositories
cp sources.list /etc/apt/sources.list
apt-get update
apt-get install deb-multimedia-keyring
apt-get update

#Install Nvidia Drivers
aptitude -r install linux-headers-$(uname -r|sed 's,[^-]*-[^-]*-,,')
aptitude install nvidia-detect
nvidia-detect
aptitude -r install nvidia-kernel-dkms
mkdir /etc/X11/xorg.conf.d
echo -e 'Section "Device"\n\tIdentifier "My GPU"\n\tDriver "nvidia"\nEndSection' > /etc/X11/xorg.conf
reboot


