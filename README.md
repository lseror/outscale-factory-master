Turnkey Linux Factory for the Outscale Cloud
============================================
Master appliance
----------------

This package is part of a factory that generates
[Turnkey Linux](http://turnkeylinux.org) appliance images for the
[Outscale](http://www.outscale.com) cloud. Since the Outscale cloud
provides an EC2-compatible API, it should be fairly portable.

This package is based on the TKL `core` appliance.

The master appliance runs a [Buildbot](http://buildbot.net) master
server. The master server orchestrates the build process and
instantiates several Buildbot slave instances.

The factory is based on TKL v13, Buildbot v0.8.6p1, Boto and miscellaneous
packages included in [Debian](http://www.debian.org) Wheezy.

Other factory components:
 * [outscale-factory-slave](http://github.com/nodalink/outscale-factory-slave):
the slave appliance which is instantiated on-demand on the cloud.
 * [outscale-image-factory](http://github.com/nodalink/outscale-image-factory):
various tools used to generate images on the Outscale cloud.
