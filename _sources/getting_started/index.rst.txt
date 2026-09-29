***************
Getting Started
***************

Installation
============
The FHI-aims step is installed with the `SEAMM Manager`_, and is probably already part of
your SEAMM installation. To add it, or bring it up to date::

  seamm-manager install fhi-aims-step
  seamm-manager update fhi-aims-step

or use the Manager's window. FHI-aims itself is licensed software that you install
yourself, so installing the step does not install FHI-aims. Instead it creates
``~/SEAMM/fhi-aims.ini`` -- or ``fhi-aims.ini`` in whichever SEAMM installation you are
working on -- which tells SEAMM where FHI-aims is and how to run it. An existing file
is never changed.

.. _SEAMM Manager: https://molssi-seamm.github.io/getting_started/installation/seamm-manager.html

Configuring FHI-aims
====================
The FHI-aims step requires that FHI-aims be installed on your system. Since FHI-aims is
licensed software, the SEAMM installer cannot install it for you. You will need to
obtain it from the `FHI-aims website`_ and install it, following the documentation
there. The FHI-aims step finds where FHI-aims is installed by looking in the file
``~/SEAMM/fhi-aims.ini``, which installing the step creates from the example below.
(If it is missing, the first run of the FHI-aims step creates it.) Edit it to point to
the correct location of FHI-aims on your system.

.. code-block:: ini

    # Configuration options for how to run FHI-aims

    [local]
    # The type of local installation to use. Options are:
    #     conda: Use a conda environment
    #   modules: Use the modules system
    #     local: Use a local installation
    #    docker: Use a Docker container
    # By default SEAMM installs FHI-aims using conda.

    installation = local

    # The command line to use, which should start with the executable followed by any options.
    # Variables in braces {} will be expanded. For example:
    #
    #   code = mpiexec -np {NTASKS} lmp_mpi
    #
    # would expand {NTASKS} to the number of tasks and run the command.
    # For a 'local' installation, the command line should include the full path to the
    # executable or it should be in the path. 

    code = ulimit -s unlimited && {mpiexec} -np {NTASKS} {fhi-aims} > aims.out

    # On a mac, need the next line instead of the above
    # code = ulimit -s hard && OMP_NUM_THREADS=1 && {mpiexec} -np {NTASKS} {fhi-aims} > aims.out

    # The path and name of executable for FHI-aims and the MPI launcher. You'll need to
    # change these and may need to specify the path to the executables.

    fhi-aims = aims.241018.scalapack.mpi.x
    mpiexec = mpirun

    # The path to the basis sets for aims. Adjust as needed.
    basis-path = ~/FHIaims/species_defaults

As long as MPI and FHI-aims are in your path, you should only need to change the exact
name of the executable and the path to the basis sets. If they are not in your path, you
can put full paths in the ``fhi-aims`` and ``mpiexec`` lines.

Running Calculations
====================
The FHI-aims step is designed to be used in a workflow, so you will need to create a
workflow to run calculations. The tutorials will walk you through the process of
creating a workflow and running various types of calculations.

.. toctree::
   :maxdepth: 2
   :titlesonly:

   tutorials/index

That should be enough to get started. For more detail about the functionality in this
plug-in, see the :ref:`User Guide <user-guide>`. 

.. Note::
   You can find other flowcharts for FHI-aims at Zenodo. From SEAMM select ``Open...``
   from the ``File`` menu, ask to open a flowchart from Zenodo and select for flowcharts
   containing the string ``FHI-aims``:

   .. figure:: images/zenodo.png
      :align: center
      :alt: Searching Zenodo for FHI-aims flowcharts

      Searching Zenodo for FHI-aims flowcharts

.. _FHI-aims website: https://fhi-aims.org
