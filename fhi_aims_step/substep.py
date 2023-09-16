# -*- coding: utf-8 -*-

"""Base class for substeps in the FHI-aims step
"""

import json
import logging
from pathlib import Path
import pprint
import re

import psutil

from molsystem.elements import to_symbols
import seamm
from seamm_util import Q_
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
        self.results = None  # Results of the calculation from the tag file.
        self._is_spin_polarized = False
        self._mapping_from_primitive = None
        self._mapping_to_primitive = None

        super().__init__(
            flowchart=flowchart, title=title, extension=extension, logger=logger
        )

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
        # Check for successful run, don't rerun
        path = Path(self.directory) / "success.dat"
        if path.exists():
            result = {}
            path = Path(self.directory) / "stdout.txt"
            if path.exists():
                result["stdout"] = path.read_text()
            result["stderr"] = ""
            return result

        path = Path(self.options["path"]).expanduser().resolve()
        exe = path / self.options["aims"]
        mpiexec = self.options["mpiexec"]
        atoms_per_core = self.options["atoms_per_core"]
        max_cores = self.options["ncores"]
        if max_cores == "available":
            max_cores = self.global_options["ncores"]

        # How many processors does this node have?
        n_cores = psutil.cpu_count(logical=False)
        self.logger.info("The number of cores is {}".format(n_cores))
        if max_cores == "available":
            max_cores = n_cores
        else:
            max_cores = int(max_cores)

        # Get the current configuration because it might change between steps
        _, configuration = self.get_system_configuration()
        n_atoms = configuration.n_atoms
        np = n_atoms // atoms_per_core
        if np <= 0:
            np = 1
        elif np > max_cores:
            np = max_cores

        printer.normal(self.indent + 4 * " " + f"FHI-aims running using {np} cores.")

        cmd = f"ulimit -s hard && {mpiexec} -np {np} {exe} > aims.out"

        local = seamm.ExecLocal()
        result = local.run(
            cmd=cmd,
            files=files,
            return_files=return_files,
            in_situ=True,
            directory=self.directory,
            shell=True,
        )

        if result is None:
            logger.error("There was an error running FHI-aims")
            return None

        logger.debug("\n" + pprint.pformat(result))

        logger.info("stdout:\n" + result["stdout"])
        if result["stderr"] != "":
            logger.warning("stderr:\n" + result["stderr"])

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
        basis = P["basis_version"]
        level = P[basis + "_level"]
        basis_path = Path(self.options["basis_path"]) / basis / level

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

        # Parsing values from the output
        path = Path(self.directory) / "aims.out"
        output = path.read_text()

        # Find the citations
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
