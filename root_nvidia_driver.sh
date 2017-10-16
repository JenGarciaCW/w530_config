#!/bin/bash


#xserver configr
apt-get install nvidia-xconfig
nvidia-xconfig 

echo "Open /etc/default/grub and modify the following lines:"
echo 'GRUB_CMDLINE_LINUX="nox2apic rcutree.rcu_idle_gp_delay=1"'
echo 'GRUB_GFXMODE=1920x1080x32'
echo 'GRUB_GFXPAYLOAD_LINUX=1920x1080x32'
echo 'are you done ? (Press q to continue)'

#!/bin/bash
while :
do
    # TASK 1
    date
    read -t 100 -n 1 key

    if [[ $key = q ]]
    then
        break
    fi
done

#wifi setting
apt-get update && apt-get install firmware-iwlwifi

#trackpoint support
cp 20-thinkpad.conf /usr/share/X11/xorg.conf.d/20-thinkpad.conf

#install i3
apt-get instal i3

#install joystick
apt-get install joystick

#install gphoto
apt-get install gphoto2

#install v4l
apt-get install v4l-utils

#install nVidia cuda
apt-get install nvidia-cuda-toolkit

#install backlight control
sudo apt-get install xbacklight

#Reboot
update-grub
reboot

