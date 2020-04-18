ARG BASE_IMAGE

FROM ${BASE_IMAGE}
LABEL maintainer="Cameron McQuinn <cameron.mcquinn@gmail.com>"

##############################
# Machinekit:  Configure multistrap

# Set up debian/control for `mk-build-deps`
RUN rm -rf /tmp/debian
ADD debian/ /tmp/debian/
RUN MK_CROSS_BUILDER=1 /tmp/debian/configure -r

# Directory for `mk-build-deps` apt repository
RUN rm -rf /tmp/debs && \
    mkdir /tmp/debs && \
    touch /tmp/debs/Sources

# Create deps package and local package repo
ARG MK_HAL_REPO
ADD ${MK_HAL_REPO} /tmp/mk-hal
RUN if test $DISTRO_VER -eq 8; then \
        mk-build-deps --arch $DEBIAN_ARCH /tmp/debian/control; \
    else \
        mk-build-deps --build-arch $DEBIAN_ARCH --host-arch $DEBIAN_ARCH \
	    /tmp/debian/control; \
    fi \
    && mv *.deb /tmp/debs \
    && cp /tmp/mk-hal/* /tmp/debs

# Remove machinekit-hal-xenomai for distros other than Jessie
RUN if test $DISTRO_VER -gt 8; then \
        rm /tmp/debs/machinekit-hal-xenomai*; \
    fi

# Generage Packages file for local repo
RUN ( cd /tmp/debs && dpkg-scanpackages -m . > /tmp/debs/Packages )

# Add deps repo to apt sources for native builds
RUN if test $DISTRO_VER -le 9 -a $DEBIAN_ARCH = amd64; then \
	echo "deb file:///tmp/debs ./" > /etc/apt/sources.list.d/local.list \
	&& apt-get update; \
    fi

###########################################
# Multistrap setup

# Add multistrap configurations
RUN rm -rf /tmp/multistrap-configs
ADD scripts/buildsystem/debian/multistrap-configs /tmp/multistrap-configs/

##############################
# Machinekit:  Host arch build environment

# Native arch:  Install build dependencies
RUN if test -z "$SYS_ROOT"; then \
        apt-get update \
        && if test $DISTRO_VER -le 9; then \
            apt-get install -y  -o Apt::Get::AllowUnauthenticated=true \
            machinekit-cnc-build-deps machinekit-hal* \
            && sed -i /etc/apt/sources.list.d/local.list -e '/^deb/ s/^/#/' \
            && apt-get update ; \
            else \
            apt-get install -y /tmp/debs/machinekit-cnc-build-deps_*.deb /tmp/debs/machinekit-hal*.deb; \
    	fi \
    fi

# Foreign arch:  Build "sysroot"
# - Select and unpack build dependency packages
RUN test -z "$SYS_ROOT" \
    || multistrap -f /tmp/multistrap-configs/$DISTRO_CODENAME.conf \
	-a $DEBIAN_ARCH -d $SYS_ROOT
# - Fix symlinks in "sysroot" libdir pointing to `/lib/$MULTIARCH`
RUN test -z "$SYS_ROOT" \
    || { \
        for link in $(find $SYS_ROOT/usr/lib/${HOST_MULTIARCH}/ -type l); do \
            if test $(dirname $(readlink $link)) != .; then \
                ln -sf ../../../lib/${HOST_MULTIARCH}/$(basename \
                    $(readlink $link)) $link; \
            fi; \
        done; \
    }

# Monkey-patch entire /usr/include, and re-add build-arch headers
RUN test -z "$SYS_ROOT" \
    || { \
        mv /usr/include /usr/include.build && \
        ln -s $SYS_ROOT/usr/include /usr/include && \
	ln -sf /usr/include.build/x86_64-linux-gnu $SYS_ROOT/usr/include; \
    }
