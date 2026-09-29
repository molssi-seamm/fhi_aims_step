# -*- coding: utf-8 -*-

"""Installer for the FHI-aims plug-in.

FHI-aims is licensed software that users build themselves, so this installer does
not install the code. It gives the SEAMM installation a ``fhi-aims.ini`` to edit,
from the template in ``data/fhi-aims.ini``, which says how to run FHI-aims.
"""

import importlib
import logging

import seamm_installer

logger = logging.getLogger(__name__)


class Installer(seamm_installer.InstallerBase):
    """Give the installation a fhi-aims.ini describing how to run FHI-aims."""

    def __init__(self, logger=logger):
        super().__init__(logger=logger)

        logger.debug("Initializing the FHI-aims installer object.")

        self.section = "fhi-aims-step"
        self.executables = ["fhi-aims"]
        self.resource_path = importlib.resources.files("fhi_aims_step") / "data"

    def exe_version(self, config):
        """Return the name and version of FHI-aims, from the executable's name."""
        return "FHI-aims", config.get("fhi-aims", "unknown")
