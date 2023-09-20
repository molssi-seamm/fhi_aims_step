# -*- coding: utf-8 -*-

"""Non-graphical part of the Optimization step in a FHI aims flowchart
"""

import logging
from pathlib import Path
import pkg_resources
import pprint  # noqa: F401
import traceback

import fhi_aims_step  # noqa: E999
import molsystem
import seamm
from seamm_util import ureg, Q_  # noqa: F401
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __

# In addition to the normal logger, two logger-like printing facilities are
# defined: "job" and "printer". "job" send output to the main job.out file for
# the job, and should be used very sparingly, typically to echo what this step
# will do in the initial summary of the job.
#
# "printer" sends output to the file "step.out" in this steps working
# directory, and is used for all normal output from this step.

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter("FHI aims")

# Add this module's properties to the standard properties
path = Path(pkg_resources.resource_filename(__name__, "data/"))
csv_file = path / "properties.csv"
if path.exists():
    molsystem.add_properties_from_file(csv_file)


class Optimization(fhi_aims_step.Energy):
    """
    The non-graphical part of a Optimization step in a flowchart.

    Attributes
    ----------
    parser : configargparse.ArgParser
        The parser object.

    options : tuple
        It contains a two item tuple containing the populated namespace and the
        list of remaining argument strings.

    subflowchart : seamm.Flowchart
        A SEAMM Flowchart object that represents a subflowchart, if needed.

    parameters : OptimizationParameters
        The control parameters for Optimization.

    See Also
    --------
    TkOptimization,
    Optimization, OptimizationParameters
    """

    def __init__(
        self,
        flowchart=None,
        title="Optimization",
        extension=None,
        module=__name__,
        logger=logger,
    ):
        """A substep for Optimization in a subflowchart for FHI aims.

        You may wish to change the title above, which is the string displayed
        in the box representing the step in the flowchart.

        Parameters
        ----------
        flowchart: seamm.Flowchart
            The non-graphical flowchart that contains this step.

        title: str
            The name displayed in the flowchart.
        extension: None
            Not yet implemented
        logger : Logger = logger
            The logger to use and pass to parent classes

        Returns
        -------
        None
        """
        logger.debug(f"Creating Optimization {self}")

        super().__init__(
            flowchart=flowchart,
            title=title,
            extension=extension,
            module=module,
            logger=logger,
        )

        self._calculation = "optimization"
        self._model = None
        self._metadata = fhi_aims_step.metadata
        self.parameters = fhi_aims_step.OptimizationParameters()

    @property
    def header(self):
        """A printable header for this section of output"""
        return "Step {}: {}".format(".".join(str(e) for e in self._id), self.title)

    @property
    def version(self):
        """The semantic version of this module."""
        return fhi_aims_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return fhi_aims_step.__git_revision__

    def description_text(self, P=None):
        """Create the text description of what this step will do.
        The dictionary of control values is passed in as P so that
        the code can test values, etc.

        Parameters
        ----------
        P: dict
            An optional dictionary of the current values of the control
            parameters.
        Returns
        -------
        str
            A description of the current step.
        """
        if not P:
            P = self.parameters.values_to_dict()

        tmp = super().description_text(P)
        energy_description = "\n".join(tmp.splitlines()[1:])

        text = (
            "The optimization using BFGS will stop at force convergence of "
            f"{P['force_convergence']}."
        )
        if P["optimize_cell"] == "yes":
            text += " For periodic systems, the unit cell will also be optimized."
        elif "angle" in P["optimize_cell"]:
            text += (
                " For periodic systems, the unit cell will also be optimized, but "
                "cell angles will be fixed."
            )
        if P["pressure"] != 0.0:
            text += f" An external pressure of {P['pressure']} will be applied."

        text += f" The optimized structure will {P['structure handling']} "

        confname = P["configuration name"]
        if confname == "use SMILES string":
            text += "using SMILES as its name."
        elif confname == "use Canonical SMILES string":
            text += "using canonical SMILES as its name."
        elif confname == "keep current name":
            text += "keeping the current name."
        elif confname == "optimized with {model}":
            text += "with 'optimized with <model>' as its name."
        elif confname == "use configuration number":
            text += "using the index of the configuration (1, 2, ...) as its name."
        else:
            confname = confname.replace("{model}", "<model>")
            text += f"with '{confname}' as its name."

        return (
            self.header
            + "\n"
            + __(text, indent=4 * " ").__str__()
            + "\n\n"
            + energy_description
        )

    def run(self, lines=None):
        """Run an Optimization step.

        Parameters
        ----------
        None

        Returns
        -------
        seamm.Node
            The next node object in the flowchart.
        """
        if lines is None:
            lines = []

        # Get the values of the parameters, dereferencing any variables
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        directory = Path(self.directory)
        directory.mkdir(parents=True, exist_ok=True)

        # Get the current system and configuration (ignoring the system...)
        _, configuration = self.get_system_configuration(None)

        convergence = P["force_convergence"].m_as("eV/Å")
        lines.append(f"relax_geometry           bfgs {convergence:.4f}")

        if P["optimize_cell"] == "yes":
            lines.append("relax_unit_cell          full")
        elif "angle" in P["optimize_cell"]:
            lines.append("relax_unit_cell          fixed_angles")

        if P["pressure"].magnitude != 0.0:
            lines.append(f"external_pressure        {P['pressure'].m_as('eV/Å^3')}")

        next_node = super().run(printer=printer, lines=lines)

        # Add other citations here or in the appropriate place in the code.
        # Add the bibtex to data/references.bib, and add a self.reference.cite
        # similar to the above to actually add the citation to the references.

        return next_node

    def analyze(self, indent="", configuration=None, data={}, **kwargs):
        """Do any analysis of the output from this step.

        Also print important results to the local step.out file using
        "printer".

        Parameters
        ----------
        indent: str
            An extra indentation for the output
        """
        # Get the parameters used
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        if len(data) == 0:
            data = self.parse_data()

        # Check that the job ended successfully
        if "is_a_nice_day" in data and data["is_a_nice_day"]:
            text = "The optimization finished successfully."
            # Write a small file to say that LAMMPS ran successfully, so cancel
            # skip if rerunning.
            path = Path(self.directory) / "success.dat"
            path.write_text("success")
        else:
            text = "The optimization did not complete properly! Be cautious.\n\n"

        path = Path(self.directory) / "geometry.in.next_step"
        coordinate_type = None
        if path.exists():
            lines = path.read_text().splitlines()
            xyz = []
            lattice_vectors = []
            for line in lines:
                line = line.strip()
                if len(line) == 0:
                    continue
                if line[0] == "#":
                    continue
                tmp = line.split()
                if tmp[0] == "atom":
                    coordinate_type = "Cartesian"
                    x, y, z = tmp[1:4]
                    xyz.append([float(x), float(y), float(z)])
                elif tmp[0] == "atom_frac":
                    coordinate_type = "fractional"
                    x, y, z = tmp[1:4]
                    xyz.append([float(x), float(y), float(z)])
                elif tmp[0] == "lattice_vector":
                    x, y, z = tmp[1:4]
                    lattice_vectors.append([float(x), float(y), float(z)])

            # Follow instructions for where to put the coordinates,
            _, starting_configuration = self.get_system_configuration(None)
            system, configuration = self.get_system_configuration(
                P=P, same_as=starting_configuration, model=self.model
            )

            if configuration.periodicity == 3:
                (
                    lattice_in,
                    fractionals_in,
                    atomic_numbers,
                    self._mapping_from_primitive,
                    self._mapping_to_primitive,
                ) = starting_configuration.primitive_cell()

                tmp = configuration.update(
                    xyz,
                    fractionals=coordinate_type == "fractional",
                    atomic_numbers=atomic_numbers,
                    lattice=lattice_vectors,
                    space_group=starting_configuration.symmetry.group,
                    symprec=0.01,
                )

                # Symmetry may have changed
                if tmp != "":
                    logger.warning(tmp)
                    text += f"\n\nWarning: {tmp}\n\n"
                    (
                        lattice,
                        fractionals,
                        atomic_numbers,
                        self._mapping_from_primitive,
                        self._mapping_to_primitive,
                    ) = configuration.primitive_cell()
            else:
                configuration.atoms.set_coordinates(
                    xyz, fractionals=coordinate_type == "fractional"
                )
        elif "relaxation_step_number" in data and data["relaxation_step_number"] == 0:
            # When aims does not steps it doesn't write a structure file :-)
            # Just copy the previous structure to any new one created...
            _, starting_configuration = self.get_system_configuration(None)
            system, configuration = self.get_system_configuration(
                P=P, same_as=starting_configuration, model=self.model
            )

        # Write the structure out for viewing.
        directory = Path(self.directory)
        directory.mkdir(parents=True, exist_ok=True)

        #  MMCIF file has bonds
        try:
            path = directory / "optimized.mmcif"
            path.write_text(configuration.to_mmcif_text())
        except Exception:
            message = "Error creating the mmcif file\n\n" + traceback.format_exc()
            logger.warning(message)
        # CIF file has cell
        if configuration.periodicity == 3:
            try:
                path = directory / "optimized.cif"
                path.write_text(configuration.to_cif_text())
            except Exception:
                message = "Error creating the cif file\n\n" + traceback.format_exc()
                logger.warning(message)

        printer.normal(
            __(
                text,
                indent=self.indent + 4 * " ",
                wrap=True,
                dedent=False,
            )
        )

        super().analyze(indent=indent, configuration=configuration, **kwargs)

        text += (
            f" The optimized structure was placed in configuration {system.name}/"
            f"{configuration.name}."
        )

        printer.normal(
            __(
                text,
                indent=self.indent + 4 * " ",
                wrap=True,
                dedent=False,
            )
        )
        printer.normal("")
