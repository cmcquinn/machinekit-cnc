#!/bin/bash

# Setup environment variables
export DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true
export LC_ALL=C LANGUAGE=C LANG=C

# Run bash preinstall script
/var/lib/dpkg/info/bash.preinst install

# Configure all packages
dpkg --configure -a

# install machinekit-hal packages
dpkg -i /tmp/debs/machinekit-hal*.deb

# Run dpkg --configure again to get anything that errored out the first time around
dpkg --configure -a
