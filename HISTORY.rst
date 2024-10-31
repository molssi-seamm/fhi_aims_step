=======
History
=======
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
