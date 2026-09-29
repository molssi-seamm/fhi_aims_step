=======
History
=======
2026.9.29 -- Bugfix: a missing fhi-aims.ini no longer stops the step
    * Creating ``~/SEAMM/fhi-aims.ini`` from the template failed with "No module named
      'fhi-aims_step'", so the step could not run without the file. It is now created.
    * When looking for FHI-aims on the PATH for an executor with no section in the file,
      the new section was written over the FHI-aims executable instead of into
      ``fhi-aims.ini``. It is now written to the file.
    * Added ``fhi-aims-step-installer``, which the SEAMM Manager runs when the step is
      installed, to write the template for you to edit.
    * The documentation describes installing with the SEAMM Manager.

2026.3.1 -- Internal: switching from deprecated library pkg_resources to importlib

2024.10.31 -- Added a first tutorial
   * Added a first tutorial to the documentation.
     
2024.10.30 -- Enhancements for energy/gradient drivers
   * Added the standard properties for energy and gradient drivers so that aims can be
     used with the ThermoChemistry, Structure, and Reaction plug-ins.
   * Changed defaults to make normal runs easier to set up.
     
2024.7.30 -- Fixed issue with initialization of fhi-aims.ini
   * Fixed issue with the initialization of the fhi-aims.ini file if it did not exist.
   * Cleaned up the section for seamm.ini now that it no longer handles the
     executable.

2024.1.19 -- Enhancements, but still debugging symmetry
   * Added ability to write out the input file and not run FHI-aims
   * Check if the calculation has been run, and don't rerun FHI-aims
   * Switched to new method of executing background jobs that supports containers.

2023.9.8 -- Initial version
   * Plug-in created using the SEAMM plug-in cookiecutter.
