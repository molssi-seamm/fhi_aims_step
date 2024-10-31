# -*- coding: utf-8 -*-

"""Base class for substeps in the FHI-aims step
"""

import configparser
import importlib
import json
import logging
from pathlib import Path
import pprint
import re
import shutil

from molsystem.elements import to_symbols
import seamm
import seamm_exec
from seamm_util import Q_, Configuration
import seamm_util.printing as printing

# In addition to the normal logger, two logger-like printing facilities are
# defined: 'job' and 'printer'. 'job' send output to the main job.out file for
# the job, and should be used very sparingly, typically to echo what this step
# will do in the initial summary of the job.
#
# 'printer' sends output to the file 'step.out' in this steps working
# directory, and is used for all normal output from this step.

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter("FHI-aims")


class Substep(seamm.Node):
    """A base class for substeps in the FHI-aims step."""

    def __init__(
        self,
        flowchart=None,
        title="no title",
        extension=None,
        logger=logger,
        module=__name__,
    ):
        self.mapping_from_primitive = None
        self.mapping_to_primitive = None
        self._is_spin_polarized = False
        self._mapping_from_primitive = None
        self._mapping_to_primitive = None
        self._input_only = False

        super().__init__(
            flowchart=flowchart, title=title, extension=extension, logger=logger
        )

    @property
    def global_options(self):
        return self.parent.global_options

    @property
    def input_only(self):
        """Whether to write the input only, not run MOPAC."""
        return self._input_only

    @input_only.setter
    def input_only(self, value):
        self._input_only = value

    @property
    def is_spin_polarized(self):
        """If the calculation is set up a spin polarized."""
        return self._is_spin_polarized

    @is_spin_polarized.setter
    def is_spin_polarized(self, value):
        self._is_spin_polarized = value

    @property
    def is_runable(self):
        """Indicate whether this not runs or just adds input."""
        return True

    @property
    def options(self):
        return self.parent.options

    def run_aims(self, files, return_files=[]):
        """Run a FHI-aims calculation.

        Parameters
        ----------
        files : {}
            Dictionary of input and control files for FHI-aims
        return_files : [str]
            List of files to bring backfrom the calculation

        Returns
        -------
        """
        directory = Path(self.directory)
        if self.input_only:
            for filename in files:
                path = directory / filename
                path.write_text(files[filename])
            return

        # Check for successful run, don't rerun
        path = directory / "success.dat"
        if path.exists():
            result = {}
            path = directory / "stdout.txt"
            if path.exists():
                result["stdout"] = path.read_text()
            result["stderr"] = ""
            return result

        # Access the options
        options = self.options
        seamm_options = self.global_options

        # Get the computational environment and set limits
        ce = seamm_exec.computational_environment()

        atoms_per_core = options["atoms_per_core"]
        max_cores = options["ncores"]
        if max_cores == "available":
            max_cores = self.global_options["ncores"]

        # How many processors does this node have?
        n_cores = ce["NTASKS"]
        self.logger.info("The number of cores is {}".format(n_cores))
        if max_cores == "available":
            max_cores = n_cores
        else:
            max_cores = int(max_cores)

        # Get the current configuration because it might change between steps
        if atoms_per_core > 0:
            _, configuration = self.get_system_configuration()
            n_atoms = configuration.n_atoms
            np = n_atoms // atoms_per_core
            if np <= 0:
                np = 1
            elif np > max_cores:
                np = max_cores
        else:
            np = max_cores

        ce["NTASKS"] = np

        printer.normal(self.indent + 4 * " " + f"FHI-aims running using {np} cores.")

        cmd = ["{code}"]

        # Run FHI-aims
        executor = self.parent.flowchart.executor

        # Read configuration file for FHI-aims
        executor_type = executor.name
        full_config = configparser.ConfigParser()
        ini_dir = Path(seamm_options["root"]).expanduser()
        path = ini_dir / "fhi-aims.ini"

        # If the config file doesn't exists, get the default
        if not path.exists():
            resources = importlib.resources.files("fhi-aims_step") / "data"
            ini_text = (resources / "fhi-aims.ini").read_text()
            txt_config = Configuration(path)
            txt_config.from_string(ini_text)
            txt_config.save()

        full_config.read(ini_dir / "fhi-aims.ini")

        # Getting desperate! Look for an executable in the path
        if executor_type not in full_config:
            path = shutil.which("fhi-aims")
            if path is None:
                raise RuntimeError(
                    f"No section for '{executor_type}' in FHI-aims ini file "
                    f"({ini_dir / 'fhi-aims.ini'}), nor in the defaults, nor "
                    "in the path!"
                )
            else:
                txt_config = Configuration(path)
                txt_config.add_section(executor_type)
                txt_config.set_value(executor_type, "installation", "local")
                txt_config.set_value(executor_type, "fhi-aims", str(path))
                path = shutil.which("mpiexec")
                if path is not None:
                    txt_config.set_value(executor_type, "mpiexec", str(path))
                txt_config.save()
                full_config.read(ini_dir / "fhi-aims.ini")

        config = dict(full_config.items(executor_type))

        result = executor.run(
            cmd=cmd,
            ce=ce,
            config=config,
            directory=self.directory,
            files=files,
            return_files=return_files,
            in_situ=True,
            shell=True,
            env={"OMP_NUM_THREADS": "1"},
        )

        if not result:
            self.logger.error("There was an error running FHI-aims")
            return None

        logger.debug("\n" + pprint.pformat(result))

        return result

    def _basis_sets(self, P, symbols, atnos):
        """The basis set part of the control file.

        Parameters
        ----------
        P : {str: value}
            The options for this substep
        symbols : [str]
            The symbols of the elements
        atnos : [int]
            The atomic numbers of the elements

        Returns
        -------
        str
            The basis set text for FHI-aims
        """
        # Get the configuration for FHI-aims to find where the basis sets are.
        executor = self.parent.flowchart.executor

        # Read configuration file for FHI-aims
        ini_dir = Path(self.global_options["root"]).expanduser()
        full_config = configparser.ConfigParser()
        full_config.read(ini_dir / "fhi-aims.ini")
        executor_type = executor.name
        if executor_type not in full_config:
            raise RuntimeError(
                f"No section for '{executor_type}' in the FHI-aims ini file "
                f"({ini_dir / 'fhi-aims.ini'})"
            )
        config = dict(full_config.items(executor_type))

        basis = P["basis_version"]
        level = P[basis + "_level"]
        basis_path = Path(config["basis-path"]) / basis / level

        # The model chemistry
        model = P["submodel"]
        if " : " in model:
            model = model.split(" : ")[0].strip()
        self.model = f"{model}/{basis}({level})"

        filename = {
            atno: f"{atno:02}_{symbol}_default" for atno, symbol in zip(atnos, symbols)
        }
        result = ""
        for atno in sorted(filename.keys()):
            path = basis_path / filename[atno]
            result += path.read_text()
        return result

    def _geometry(self, configuration):
        """Get the geometry for FHI-aims.

        Parameters
        ----------
        configuration : molsystem._Configuration
            The current configuration

        Returns
        -------
        str
            The contents of the geometry.in for FHI-aims
        """

        key = "atom" if configuration.periodicity == 0 else "atom_frac"

        lines = []
        lines.append(f"# Geometry for {configuration.system.name}/{configuration.name}")
        lines.append("#")
        if configuration.periodicity == 0:
            xyzs = configuration.coordinates
            symbols = configuration.atoms.symbols
        else:
            if "primitive cell" in self.parameters:
                use_primitive_cell = self.parameters["primitive cell"].get(
                    context=seamm.flowchart_variables._data
                )
            else:
                use_primitive_cell = True

            if use_primitive_cell:
                # Write the structure using the primitive cell
                (
                    lattice,
                    xyzs,
                    atomic_numbers,
                    self._mapping_from_primitive,
                    self._mapping_to_primitive,
                ) = configuration.primitive_cell()
                lines.append("# Using primitive cell. Conventional cell is")
            else:
                # Use the full cell
                lattice = configuration.cell.vectors()
                xyzs = configuration.atoms.get_coordinates(fractionals=True)
                atomic_numbers = configuration.atoms.atomic_numbers

                n_atoms = len(atomic_numbers)
                self._mapping_from_primitive = [i for i in range(n_atoms)]
                self._mapping_to_primitive = [i for i in range(n_atoms)]
            symbols = to_symbols(atomic_numbers)

            a, b, c, alpha, beta, gamma = configuration.cell.parameters
            lines.append(
                f"# cell = {a:4f} {b:.4f} {c:.4f} {alpha:.2f} {beta:.2f} {gamma:.2f}"
            )
            for abc in lattice:
                x, y, z = abc
                lines.append(f"lattice_vector  {x:15.9f} {y:15.9f} {z:15.9f}")
            lines.append("#")

        if self.is_spin_polarized:
            spins = configuration.atoms["spin"]
            for xyz, symbol, spin in zip(xyzs, symbols, spins):
                x, y, z = xyz
                lines.append(f"{key}  {x:15.8f}  {y:15.8f}  {z:15.8f} {symbol}")
                lines.append(f"initial_moment  {spin:8.4f}")
        else:
            for xyz, symbol in zip(xyzs, symbols):
                x, y, z = xyz
                lines.append(f"{key}  {x:15.8f}  {y:15.8f}  {z:15.8f} {symbol}")
        return "\n".join(lines)

    def parse_data(self):
        """Get the data from the AIMS files

        Parameters
        ----------
        none
        """
        data = {}

        # Parsing values from the JSON
        path = Path(self.directory) / "aims.json"
        if path.exists():
            with path.open() as fd:
                jdata = json.load(fd)
        for section in jdata:
            record = section["record_type"]
            for key, mdata in self._metadata["results"].items():
                self.logger.debug(f"results {key=}")
                if (
                    "calculation" in mdata
                    and self.calculation not in mdata["calculation"]
                ):
                    continue
                if "json_section" not in mdata or mdata["json_section"] != record:
                    continue

                tmp_key = key.rstrip("^")
                if tmp_key in section:
                    value = section[tmp_key]
                    if "energy" in tmp_key:
                        # AIMS has a bad conversion to eV. Fix
                        aimsEh2eV = (
                            float(section["hartree"])
                            if "hartree" in section
                            else 27.2113845
                        )
                        value = value / aimsEh2eV * Q_(1, "E_h").m_as("eV")
                    if "type" in mdata:
                        if isinstance(value, list):
                            value = [mdata["type"](v) for v in value]
                        else:
                            value = mdata["type"](value)
                    if mdata["dimensionality"] == "scalar":
                        data[key] = value
                    else:
                        if key not in data:
                            data[key] = []
                        data[key].append(value)

        if "is_a_nice_day" in section:
            data["is_a_nice_day"] = section["is_a_nice_day"]

        if "total_energy" in data:
            data["energy"] = data["total_energy"]
        data["model"] = "FHI-aims/" + self.model

        # Parsing values from the output
        path = Path(self.directory) / "aims.out"
        output = path.read_text()

        # Find the citations and other data
        lines = output.splitlines()

        # Check that the job ended successfully
        if "is_a_nice_day" not in data:
            if "          Have a nice day." in lines:
                data["is_a_nice_day"] = True
            else:
                data["is_a_nice_day"] = False

        if "    http://doi.org/10.1016/j.cpc.2017.09.007" in lines:
            self.references.cite(
                raw=self._bibliography["YU2018267"],
                alias="ELSI",
                module="FHI-aims step",
                level=1,
                note="The principle citation for ELSI.",
            )
        if "    http://doi.org/10.1016/j.jcp.2009.08.008" in lines:
            self.references.cite(
                raw=self._bibliography["HAVU20098367"],
                alias="Numerical grids for integration",
                module="FHI-aims step",
                level=1,
                note="The principle citation for numerical integration grids.",
            )

        # Forces. The output looks like this
        #
        # Total atomic forces (unitary forces cleaned) [eV/Ang]:
        # |    1   0.116396923435835E+00   0.380404354092886E-01  -0.486778273969592E-27
        # |    2   0.177234658278163E+00  -0.618817461451795E-01  -0.649037698626122E-27
        # |    3  -0.293631581713999E+00   0.238413107358909E-01  -0.649037698626122E-27

        it = iter(lines)
        for line in it:
            if "Total atomic forces" in line:
                forces = []
                for line in it:
                    line = line.strip()
                    if len(line) == 0:
                        break
                    parts = line.split()
                    forces.append([-float(p) for p in parts[2:]])
                data["gradients"] = forces

        for key, mdata in self._metadata["results"].items():
            self.logger.debug(f"results {key=}")
            if key in data:
                continue
            if "calculation" in mdata and self.calculation not in mdata["calculation"]:
                continue
            if "re" not in mdata:
                continue

            self.logger.debug(mdata["re"])
            matches = re.findall(mdata["re"], output)
            self.logger.debug(matches)
            if len(matches) > 0:
                txt = matches[-1]
                if txt == "":
                    self.logger.warning(
                        f"Parsing output, re ({mdata['re']}) gave error"
                    )
                else:
                    if "type" in mdata:
                        data[key] = mdata["type"](txt)
                    else:
                        data[key] = txt

        return data
