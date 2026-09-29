# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Handle the installation of the FHI-aims step."""

from .installer import Installer


def run():
    """Give the SEAMM installation a fhi-aims.ini describing how to run FHI-aims."""
    installer = Installer()
    installer.run()


if __name__ == "__main__":
    run()
