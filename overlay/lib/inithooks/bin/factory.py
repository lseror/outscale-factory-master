#!/usr/bin/python
"""Setup factory

Option:
--pass= unless provided, will ask interactively
--email= unless provided, will ask interactively

"""

import sys
import getopt
# import hashlib

from dialog_wrapper import Dialog


def usage(s=None):
    if s:
        print >> sys.stderr, "Error:", s
    print >> sys.stderr, "Syntax: %s [options]" % sys.argv[0]
    print >> sys.stderr, __doc__
    sys.exit(1)


def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "h",
                                       ['help', 'pass=', 'email='])
    except getopt.GetoptError as e:
        usage(e)

    password = ""
    email = ""
    for opt, val in opts:
        if opt in ('-h', '--help'):
            usage()
        elif opt == '--pass':
            password = val
        elif opt == '--email':
            email = val

    if not (password and email):
        d = Dialog('TKL Factory - First boot configuration')

    if not password:
        password = d.get_password(
            "Web Password",
            "Enter new password for the buildbot web interface.")

    if not email:
        email = d.get_email(
            "Admin Email",
            "Please enter admin email address for the buildslaves.",
            "admin@example.com")

    # hashpass = hashlib.md5(password).hexdigest()

if __name__ == "__main__":
    main()
