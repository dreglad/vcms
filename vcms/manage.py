#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    """don't set a default settings file"""
    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vcms.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
