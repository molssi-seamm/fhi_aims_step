=======
History
=======
2024.7.30 -- Fixed issue with initialization of fhi-aims.ini
   * Fixed issue with the initialization of the fhi-aims.ini fileif it did not exist.
   * Cleaned up the section for seamm.ini now that it no longers handles the
     executable.

2024.1.19 -- Enhancements, but still debugging symmetry
   * Added ability to write out the input file and not run FHI-aims
   * Check if the calculation has been run, and don't rerun FHI-aims
   * Switched to new method of executing background jobs that supports containers.

2023.9.8 -- Initial version
   * Plug-in created using the SEAMM plug-in cookiecutter.
