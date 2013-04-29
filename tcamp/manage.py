#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # shim tagger into the path
    sys.path.append(os.path.realpath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)),
                     '..', 'tagger')))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
