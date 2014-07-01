"""
Various functions used by Buildbot's master.cfg.
"""
import random
import string
import sys
from fnmatch import fnmatch

import boto.ec2

random.seed()


class AMINotFound(Exception):

    """
    This error will be raised at startup
    by buildbot if the slave AMI is not found.
    """


def generate_password(minlen=32, maxlen=64):
    """
    Generate a random password for slave instances.
    """
    return ''.join(random.choice(string.ascii_letters + string.digits)
                   for i in range(random.randint(minlen, maxlen)))


def find_images(region, pattern, tags={}):
    """
    Take name pattern and/or tags,
    return list of image objects,
    sorted by name in reverse order.

    The name pattern is shell style: ?*[seq][!seq].
    """
    conn = boto.ec2.connect_to_region(region)
    filters = {}
    if tags:
        filters.update(('tag' + k, tags[k]) for k in tags)
    images = conn.get_all_images(filters=filters)
    if pattern:
        images = [each for each in images
                  if fnmatch(each.name, pattern)]
    return sorted(
        images,
        reverse=True,
        key=lambda x: x.name)


def get_image_id(region, pattern, tags={}):
    """
    Return first image id found.
    """
    images = find_images(region, pattern, tags)
    if not images:
        raise AMINotFound('No such image region={} pattern={} tags={}'
                          .format(repr(region), repr(pattern), repr(tags)))
    return images[0].id


def delete_images(region, image_id_list):
    """
    Delete all images and snapshots.
    """
    conn = boto.ec2.connect_to_region(region)
    for image_id in image_id_list:
        sys.stderr.write('Deleting {}\n'.format(image_id))
        conn.deregister_image(image_id, delete_snapshot=True)


def _test_find_images():
    """
    Test harness for find_images()
    """
    import json
    import pprint
    if len(sys.argv) != 4:
        sys.stderr.write('Usage: {} REGION NAME_PATTERN TAGS_JSON\n'
                         .format(sys.argv[0]))
        sys.exit(1)
    images = find_images(
        sys.argv[1],
        sys.argv[2],
        json.loads(sys.argv[3]))
    pprint.pprint(
        [(each.id, each.name)
         for each in images])

if __name__ == '__main__':
    _test_find_images()
