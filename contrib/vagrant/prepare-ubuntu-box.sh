#!/bin/bash -ex

#
# Prepare a Deis-optimized AMI from a vanilla Ubuntu 12.04
# Prepare a Deis-optimized Vagrant box from vanilla Ubuntu 12.04
#
# Instructions:
#
#   1. Launch a vanilla Ubuntu 12.04 instance with `vagrant up`
#   2. SSH in with `vagrant ssh`, do `sudo -i` and install the 3.8 kernel with:
#      apt-get update && apt-get install -yq linux-image-generic-lts-raring linux-headers-generic-lts-raring && reboot
#   3. After reboot is complete, SSH in again and `uname -r` to confirm kernel is 3.8
#   4. Run this script (as root!) to optimize the image for fast boot times
#   5. Create a new box with `vagrant package && cp -f package.box contrib/vagrant/deis-base.box`
#

# Remove any temporary work files, including the postinstall.sh script
rm -f /home/${account}/{*.iso,postinstall*.sh}

# Install some essentials and mDNS daemon
apt-get install python-software-properties curl apt-transport-https -y

# Add the Docker repository key to your local keychain
# using apt-key finger you can check the fingerprint matches 36A1 D786 9245 C895 0F96 6E92 D857 6A8B A88D 21E9
curl https://get.docker.io/gpg | apt-key add -

# Add the Docker repository to your apt sources list.
echo deb https://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list

# upgrade to latest packages
apt-get update
apt-get dist-upgrade -yq

# install required packages
apt-get install lxc-docker git make python-setuptools python-pip -yq

# create buildstep docker image
git clone https://github.com/opdemand/buildstep.git
cd buildstep
git checkout deis
make
cd ..
rm -rf buildstep

# install chef 11.x deps
apt-get install -yq ruby1.9.1 ruby1.9.1-dev make
update-alternatives --set ruby /usr/bin/ruby1.9.1
update-alternatives --set gem /usr/bin/gem1.9.1

# install mDNS support
apt-get install avahi-daemon -yq

# clean and remove old packages
apt-get clean
apt-get autoremove -yq

# reset cloud-init
rm -rf /var/lib/cloud

# purge SSH authorized keys
# rm -f /home/ubuntu/.ssh/authorized_keys
rm -f /root/.ssh/authorized_keys

# ssh host keys are automatically regenerated
# on system boot by ubuntu cloud init

# purge /var/log
find /var/log -type f | xargs rm

# Removing leftover leases and persistent rules
rm -f /var/lib/dhcp3/*

# Make sure Udev doesn't block our network, see: http://6.ptmc.org/?p=164
rm /etc/udev/rules.d/70-persistent-net.rules
mkdir /etc/udev/rules.d/70-persistent-net.rules
rm -rf /dev/.udev/
rm /lib/udev/rules.d/75-persistent-net-generator.rules

# flush writes to block storage
sync

# Zero out the free space to save space in the final image
dd if=/dev/zero of=/EMPTY bs=1M
rm -f /EMPTY
