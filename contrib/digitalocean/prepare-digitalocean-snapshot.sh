#!/bin/bash -ex

#
# Prepare a Deis-optimized snapshot from a vanilla Ubuntu 12.04.3 droplet.
#
# Instructions:
#
#   1. Launch a vanilla Ubuntu 12.04.3 droplet (64-bit)
#   2. Run this script (as root!) to install the packages necessary for faster boot times
#   3. Create a new snapshot of this droplet with the name 'deis-base'
#   4. Create/update your Deis flavors to use your new snapshot
#

THIS_DIR=$(cd $(dirname $0); pwd) # absolute path
CONTRIB_DIR=$(dirname $THIS_DIR)

# upgrade to latest packages
apt-get update
apt-get upgrade -yq

# install HTTPS transport support
apt-get install -qy apt-transport-https

# install docker's dependencies
apt-get install python-software-properties -y

# Add the Docker repository key to your local keychain
# using apt-key finger you can check the fingerprint matches 36A1 D786 9245 C895 0F96 6E92 D857 6A8B A88D 21E9
curl https://get.docker.io/gpg | apt-key add -

# Add the Docker repository to your apt sources list.
echo deb https://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list

# upgrade to latest packages
apt-get update
apt-get -qy upgrade

# install required packages
apt-get install lxc-docker curl git make python-setuptools python-pip -yq

# create buildstep docker image
git clone -b deis https://github.com/opdemand/buildstep.git
cd buildstep
git checkout deis
make
cd ..
rm -rf buildstep

# install chef 11.x deps
apt-get install -yq ruby1.9.1 ruby1.9.1-dev make
update-alternatives --set ruby /usr/bin/ruby1.9.1
update-alternatives --set gem /usr/bin/gem1.9.1

# clean and remove old packages
apt-get clean
apt-get autoremove -yq

# reset cloud-init
rm -rf /var/lib/cloud

# purge SSH authorized keys
rm -f /root/.ssh/authorized_keys

# ssh host keys are automatically regenerated
# on system boot by ubuntu cloud init

# purge /var/log
find /var/log -type f | xargs rm

# flush writes to block storage
sync
