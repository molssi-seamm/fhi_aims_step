#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fhi_aims_step` package."""

import pytest  # noqa: F401
import fhi_aims_step  # noqa: F401


def test_construction():
    """Just create an object and test its type."""
    result = fhi_aims_step.FHIaims()
    assert str(type(result)) == "<class 'fhi_aims_step.fhi_aims.FHIaims'>"
