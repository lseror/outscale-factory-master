"""
Buildbot build steps used to create a TurnKey appliance.

The module is a wrapper over create_ami. It encapsulates
the EC2 calls that are part of the build process and happen
on the buildmaster side.

For the EC2 slave instances we use buildbot's stuff,
see master.cfg.
"""

from datetime import datetime

import boto

from twisted.python import failure
from twisted.internet import threads, defer

from buildbot.status import results
from buildbot.process.buildstep import BuildStep
try:
    # 0.8.8
    from buildbot.buildslave.ec2 import EC2LatentBuildSlave
except ImportError:
    # 0.8.6p1
    from buildbot.ec2buildslave import EC2LatentBuildSlave
    
from outscale_image_factory import create_ami


class _EC2BuildStep(BuildStep):

    def __init__(self, region=None, location=None, **kw):
        BuildStep.__init__(self, **kw)
        if region is None or location is None:
            raise TypeError(
                "BuildStep arguments *region* and *location* are required")
        self.region = region
        self.location = location
        self.addFactoryArguments(region=region, location=location)

    def _connect(self):
        return boto.ec2.connect_to_region(self.region)

    def _timestamp(self):
        return datetime.now().strftime('%F-%H.%M.%S')


class AttachNewVolume(_EC2BuildStep):

    """
    Attach a new volume to the EC2 build slave.
    """

    def __init__(self, **kw):
        _EC2BuildStep.__init__(self, **kw)

    @defer.inlineCallbacks
    def start(self):
        appliance = self.getProperty('appliance_name')
        volume_name = 'temp-{}-{}'.format(appliance, self._timestamp())
        volume_tags = dict(name=volume_name)
        volume_size = 10 # FIXME
        assert isinstance(self.buildslave, EC2LatentBuildSlave)
        instance_id = self.buildslave.instance.id
        self.setProperty('buildslave_instance_id', instance_id)
        self.setProperty('volume_name', volume_name),
        self.setProperty('volume_size', volume_size)

        conn = yield threads.deferToThread(self._connect)

        volume_id, device, error = yield threads.deferToThread(
            create_ami.attach_new_volume,
            conn, instance_id, volume_size, self.location, volume_tags)

        self.setProperty('volume_id', volume_id)
        self.setProperty('device_name', device)
        if volume_id and not error:
            self.finished(results.SUCCESS)
        else:
            self.failed(failure.Failure(error))


class CreateImage(_EC2BuildStep):

    """
    Create image from the buildslave's build volume.

    TODO tag the image with the git branch and revision.
    """

    def __init__(self, **kw):
        _EC2BuildStep.__init__(self, **kw)

    @defer.inlineCallbacks
    def start(self):
        revision = self.getProperty('revision')
        branch = self.getProperty('branch')
        appliance = self.getProperty('appliance_name')
        volume_id = self.getProperty('volume_id')
        image_name = 'app-{}-{}'.format(appliance, self._timestamp())
        self.setProperty('image_name', image_name)

        conn = yield threads.deferToThread(self._connect)

        image_id, error = yield threads.deferToThread(create_ami.create_image,
                                                      conn, image_name, volume_id)

        self.setProperty('image_id', image_id)
        if not error:
            self.finished(results.SUCCESS)
        else:
            self.failed(failure.Failure(error))


class DestroyVolume(_EC2BuildStep):

    """
    Destroy the build volume.
    """

    def __init__(self, **kw):
        _EC2BuildStep.__init__(self, **kw)

    @defer.inlineCallbacks
    def start(self):
        volume_id = self.getProperty('volume_id')
        conn = yield threads.deferToThread(self._connect)
        ok, error = yield threads.deferToThread(create_ami.destroy_volume,
                                                conn, volume_id)
        if ok:
            self.finished(results.SUCCESS)
        else:
            self.failed(failure.Failure(error))
