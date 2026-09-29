#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""fhi-aims.ini: the shipped template and how the step reads it."""

import configparser
import importlib.resources

import pytest

from fhi_aims_step import substep

TEMPLATE = importlib.resources.files("fhi_aims_step") / "data" / "fhi-aims.ini"


def _step():
    """A substep without a flowchart; _fhi_aims_config needs no state."""
    return substep.Substep.__new__(substep.Substep)


def test_missing_file_gets_the_template(tmp_path):
    config = _step()._fhi_aims_config("local", tmp_path)
    assert config["installation"] == "local"
    assert (tmp_path / "fhi-aims.ini").read_text() != ""


def test_unknown_executor_found_on_the_path(tmp_path, monkeypatch):
    exe = tmp_path / "bin" / "fhi-aims"
    exe.parent.mkdir()
    exe.write_text("#!/bin/sh\n")
    found = {"fhi-aims": str(exe), "mpiexec": "/usr/bin/mpiexec"}
    monkeypatch.setattr(substep.shutil, "which", lambda name: found.get(name))
    config = _step()._fhi_aims_config("cluster", tmp_path)
    assert config["fhi-aims"] == str(exe)
    assert exe.read_text() == "#!/bin/sh\n"  # the executable is left alone
    saved = configparser.ConfigParser()
    saved.read(tmp_path / "fhi-aims.ini")
    assert saved["cluster"]["mpiexec"] == "/usr/bin/mpiexec"


def test_unknown_executor_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr(substep.shutil, "which", lambda name: None)
    with pytest.raises(RuntimeError, match="does not know how to run FHI-aims"):
        _step()._fhi_aims_config("cluster", tmp_path)


def test_installer_points_at_the_template():
    pytest.importorskip("seamm_installer")  # from the SEAMM Manager
    from fhi_aims_step.installer import Installer  # noqa: F401

    assert TEMPLATE.is_file()
    assert (TEMPLATE.parent / "configuration.txt").is_file()
