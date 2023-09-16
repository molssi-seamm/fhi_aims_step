# -*- coding: utf-8 -*-

"""Non-graphical part of the Energy step in a FHI-aims flowchart
"""

import csv
import logging
from pathlib import Path
import pkg_resources
import pprint  # noqa: F401
import textwrap

import numpy as np
from tabulate import tabulate

import fhi_aims_step
from .substep import Substep
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
printer = printing.getPrinter("FHI-aims")

# Add this module's properties to the standard properties
path = Path(pkg_resources.resource_filename(__name__, "data/"))
csv_file = path / "properties.csv"
if path.exists():
    molsystem.add_properties_from_file(csv_file)


class Energy(Substep):
    """
    The non-graphical part of a Energy step in a flowchart.

    Attributes
    ----------
    parser : configargparse.ArgParser
        The parser object.

    options : tuple
        It contains a two item tuple containing the populated namespace and the
        list of remaining argument strings.

    subflowchart : seamm.Flowchart
        A SEAMM Flowchart object that represents a subflowchart, if needed.

    parameters : EnergyParameters
        The control parameters for Energy.

    See Also
    --------
    TkEnergy,
    Energy, EnergyParameters
    """

    def __init__(
        self,
        flowchart=None,
        title="Energy",
        extension=None,
        module=__name__,
        logger=logger,
    ):
        """A substep for Energy in a subflowchart for FHI-aims.

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
        logger.debug(f"Creating Energy {self}")

        super().__init__(
            flowchart=flowchart,
            title=title,
            extension=extension,
            module=__name__,
            logger=logger,
        )

        self._calculation = "energy"
        self._model = None
        self._metadata = fhi_aims_step.metadata
        self.parameters = fhi_aims_step.EnergyParameters()

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

    def analyze(self, indent="", configuration=None, data={}, **kwargs):
        """Do any analysis of the output from this step.

        Also print important results to the local step.out file using
        "printer".

        Parameters
        ----------
        indent: str
            An extra indentation for the output
        """
        options = self.parent.options
        directory = Path(self.directory)

        if len(data) == 0:
            data = self.parse_data()

        text = ""
        if type(self) is fhi_aims_step.Energy:
            # Check that the job ended successfully
            if "is_a_nice_day" in data and data["is_a_nice_day"]:
                text += "The calculation finished successfully."
                # Write a small file to say that LAMMPS ran successfully, so cancel
                # skip if rerunning.
                path = Path(self.directory) / "success.dat"
                path.write_text("success")
            else:
                text += "The calculation did not complete properly! Be cautious.\n\n"

        if len(text) > 0:
            printer.normal(
                __(
                    text,
                    indent=self.indent + 4 * " ",
                    wrap=True,
                    dedent=False,
                )
            )
        text = ""

        # Put any requested results into variables or tables
        self.store_results(configuration=configuration, data=data)

        # Prepare our summary
        table = {
            "Item": [],
            "Value": [],
            "Units": [],
        }
        if "total_energy" in data:
            table["Item"].append("Total energy")
            table["Value"].append(f"{data['total_energy']:.5f}")
            table["Units"].append("eV")
        if "dispersion_energy" in data:
            table["Item"].append("vdW correction")
            table["Value"].append(f"{data['dispersion_energy']:.5f}")
            table["Units"].append("eV")
        if "total_spin" in data:
            table["Item"].append("Total Spin")
            table["Value"].append(f"{data['total_spin']:.5f}")
            table["Units"].append(" ")
        if "relaxation_step_number" in data:
            table["Item"].append("Optimization steps")
            table["Value"].append(data["relaxation_step_number"])
            table["Units"].append(" ")
        if "norm_force_atoms" in data:
            table["Item"].append("Force norm")
            table["Value"].append(data["norm_force_atoms"])
            table["Units"].append("eV/Å")
        if "maximum_force" in data:
            table["Item"].append("Maximum force")
            table["Value"].append(data["maximum_force"])
            table["Units"].append("eV/Å")
        if "total_number_of_loops" in data:
            table["Item"].append("SCF steps")
            table["Value"].append(data["total_number_of_loops"])
            table["Units"].append(" ")
        if "change_charge_density" in data:
            table["Item"].append("Δ charge density")
            table["Value"].append(f"{data['change_charge_density'][-1]:.2e}")
            table["Units"].append(" ")
        if "change_spin_density" in data:
            table["Item"].append("Δ spin density")
            table["Value"].append(f"{data['change_spin_density'][-1]:.2e}")
            table["Units"].append(" ")
        if "change_sum_eigenvalues" in data:
            table["Item"].append("Δ Σ(eigenvalues)")
            table["Value"].append(f"{data['change_sum_eigenvalues'][-1]:.2e}")
            table["Units"].append(" ")
        if "change_forces" in data:
            table["Item"].append("Δ forces")
            table["Value"].append(f"{data['change_forces'][-1]:.2e}")
            table["Units"].append(" ")

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="psql",
            colalign=("center", "decimal"),
            disable_numparse=True,
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        text_lines.append("SCF Results".center(length))
        text_lines.append(tmp)
        tmp = "\n\n"
        tmp += textwrap.indent("\n".join(text_lines), self.indent + 7 * " ")
        printer.normal(tmp)

        system, configuration = self.get_system_configuration(None)
        symbols = configuration.atoms.asymmetric_symbols
        atoms = configuration.atoms
        symmetry = configuration.symmetry
        # Charge and spin, if available
        if "atoms_proj_charge" in data:
            # Add to atoms (in coordinate table)
            if "charge" not in atoms:
                atoms.add_attribute(
                    "charge", coltype="float", configuration_dependent=True
                )
            if symmetry.n_symops == 1:
                chgs = data["atoms_proj_charge"][0]
            else:
                chgs, delta = symmetry.symmetrize_atomic_scalar(
                    data["atoms_proj_charge"][0]
                )
                delta = np.array(delta)
                max_delta = np.max(abs(delta))
                text += (
                    "The maximum difference of the charges of symmetry related atoms "
                    f"was {max_delta:.4f}\n"
                )
            atoms["charge"][0:] = chgs

            # Print the charges and dump to a csv file
            chg_tbl = {
                "Atom": [*range(1, len(symbols) + 1)],
                "Element": symbols,
                "Charge": [],
            }
            with open(directory / "atom_properties.csv", "w", newline="") as fd:
                writer = csv.writer(fd)
                if "atoms_proj_spin" in data:
                    # Add to atoms (in coordinate table)
                    if "spin" not in atoms:
                        atoms.add_attribute(
                            "spin", coltype="float", configuration_dependent=True
                        )
                        if symmetry.n_symops == 1:
                            spins = data["atoms_proj_spin"][0]
                        else:
                            spins, delta = symmetry.symmetrize_atomic_scalar(
                                data["atoms_proj_spin"][0]
                            )
                            atoms["spins"][0:] = spins
                            delta = np.array(delta)
                            max_delta = np.max(abs(delta))
                            text += (
                                " The maximum difference of the spins of symmetry "
                                f"related atoms was {max_delta:.4f}.\n"
                            )
                        atoms["spin"][0:] = spins

                    header = "        Atomic charges and spins"
                    chg_tbl["Spin"] = []
                    writer.writerow(["Atom", "Element", "Charge", "Spin"])
                    for atom, symbol, q, s in zip(
                        range(1, len(symbols) + 1),
                        symbols,
                        data["atoms_proj_charge"][0],
                        data["atoms_proj_spin"][0],
                    ):
                        q = f"{q:.3f}"
                        s = f"{s:.3f}"

                        writer.writerow([atom, symbol, q, s])

                        chg_tbl["Charge"].append(q)
                        chg_tbl["Spin"].append(s)
                else:
                    header = "        Atomic charges"
                    writer.writerow(["Atom", "Element", "Charge"])
                    for atom, symbol, q in zip(
                        range(1, len(symbols) + 1),
                        symbols,
                        data["atoms_proj_charge"][0],
                    ):
                        q = f"{q:.2f}"
                        writer.writerow([atom, symbol, q])

                        chg_tbl["Charge"].append(q)
            if len(symbols) <= int(options["max_atoms_to_print"]):
                tmp = tabulate(
                    chg_tbl,
                    headers="keys",
                    tablefmt="psql",
                    colalign=("center", "center"),
                )
                length = len(tmp.splitlines()[0])
                text_lines = []
                text_lines.append(header.center(length))
                text_lines.append(tmp)
                tmp = "\n\n"
                tmp += textwrap.indent("\n".join(text_lines), self.indent + 7 * " ")
                printer.normal(tmp)

        if len(text) > 0:
            printer.normal(
                __(
                    text,
                    indent=self.indent + 4 * " ",
                    wrap=True,
                    dedent=False,
                )
            )
        text = []

        printer.normal("")

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

        model = P["model"]
        submodel = P["submodel"]
        if type(self) is fhi_aims_step.Energy:
            text = "A single point"
        else:
            text = "Using an"
        if self.is_expr(model):
            if self.is_expr(submodel):
                text += (
                    " energy calculation with the model and submodel "
                    f"determined at runtime from '{model}' and '{submodel}.'"
                )
        else:
            model = model[0].lower() + model[1:]
            if self.is_expr(submodel):
                text += (
                    f" energy calculation with the {model} and "
                    f"submodel determined at runtime by '{submodel}.'"
                )
            else:
                text += (
                    f" energy calculation with the '{submodel}' variant "
                    f"of the {model}."
                )

        text += " The basis set version is "
        basis = P["basis_version"]
        if self.is_expr(basis):
            text += f"determined by the variable '{basis}'."
        else:
            text += f"'{basis}'"
            level = P[basis + "_level"]
            if self.is_expr(level):
                text += f". The level of the basis set will be determined by '{level}'."
            else:
                text += f", level '{level}'."

        relativity = P["relativity"]
        if self.is_expr(relativity):
            text += (
                " Whether and how relativity will be included will be determined by "
                f"'{relativity}'."
            )
        elif relativity == "none":
            text += " Relativistic effects will not be included."
        else:
            text += f" Relativistic effects will be included using the {relativity}."

        dispersion = P["dispersion"]
        if self.is_expr(dispersion):
            text += (
                " Whether and how long-range van der Waals effects (many-body "
                f"dispersion) will be included will be determined by '{dispersion}'."
            )
        elif dispersion == "none":
            text += " Long-range van der Waals terms will not be included."
        else:
            text += (
                f" Long-range van der Waals terms will be included using {dispersion}."
            )

        # k-space integration
        kmethod = P["k-grid method"]
        if kmethod == "grid spacing":
            if isinstance(P["odd grid"], bool) or P["odd grid"] == "yes":
                text += (
                    f" For periodic systems a {P['centering']} grid with a spacing of "
                    f"{P['k-spacing']} and odd numbers of points will be used."
                )
            else:
                text += (
                    f" For periodic systems a {P['centering']} grid with a spacing of "
                    f"{P['k-spacing']} will be used."
                )
        elif kmethod == "explicit grid dimensions":
            text += (
                f" For periodic systems a {P['na']} x{P['nb']} x{P['nc']} "
                "grid will be used."
            )
        broadening = P["occupation type"]
        if broadening in ("integer",):
            text += " The occupation will be constrained to be integers."
        else:
            text += (
                " The effect of temperature on the electron distribution "
                f"will be modeled using {P['occupation type']} broadening with a "
                f"width of {P['smearing width']}."
            )
        forces = P["calculate_gradients"]
        if not isinstance(forces, bool) and self.is_expr(forces):
            text += (
                " Whether forces will be calculated in this single-point calculation "
                f"will be determined by '{forces}'."
            )
        if forces == "yes" or (isinstance(forces, bool) and forces):
            text += " The forces will be calculated for this single-point calculation."

        return self.header + "\n" + __(text, indent=4 * " ").__str__()

    def plot_control(self, P, configuration):
        """Create the density and orbital plots if requested

        Parameters
        ----------
        data : dict()
             Dictionary of results from the calculation (results.tag file)
        """
        lines = []
        # periodicity = configuration.periodicity

        # output cube eigenstate 5

        if P["total density"]:
            lines.append("output cube               total_density")
        if self.is_spin_polarized and P["total spin density"]:
            lines.append("output cube               spin_density")
        if P["difference density"]:
            lines.append("output cube               delta_density")

        # # and work out the orbitals
        # txt = P["selected orbitals"]
        # if txt == "all":
        #     options["PlottedLevels"] = "1:-1"
        # else:
        #     orbitals = []
        #     for chunk in txt.split(","):
        #         chunk = chunk.strip()
        #         if ":" in chunk or ".." in chunk:
        #             if ":" in chunk:
        #                 first, last = chunk.split(":")
        #             elif ".." in chunk:
        #                 first, last = chunk.split("..")
        #             first = first.strip().upper()
        #             last = last.strip().upper()

        #             if first == "HOMO":
        #                 first = homo
        #             elif first == "LUMO":
        #                 first = homo + 1
        #             else:
        #                 first = int(first.removeprefix("HOMO").removeprefix("LUMO"))
        #                 if first < 0:
        #                     first = homo + first
        #                 else:
        #                     first = homo + 1 + first

        #             if last == "HOMO":
        #                 last = homo
        #             elif last == "LUMO":
        #                 last = homo + 1
        #             else:
        #                 last = int(last.removeprefix("HOMO").removeprefix("LUMO"))
        #                 if last < 0:
        #                     last = homo + last
        #                 else:
        #                     last = homo + 1 + last

        #             orbitals.extend(range(first, last + 1))
        #         else:
        #             first = chunk.strip().upper()

        #             if first == "HOMO":
        #                 first = homo
        #             elif first == "LUMO":
        #                 first = homo + 1
        #             else:
        #                 first = int(first.removeprefix("HOMO").removeprefix("LUMO"))
        #                 if first < 0:
        #                     first = homo + first
        #                 else:
        #                     first = homo + 1 + first
        #             orbitals.append(first)

        #         # Remove orbitals out of limits
        #         tmp = orbitals
        #         orbitals = []
        #         for x in tmp:
        #             if x > 0 and x <= n_orbitals:
        #                 orbitals.append(x)

        #         options["PlottedLevels"] = orbitals

        # if periodicity != 0:
        #     if P["selected k-points"] == "all":
        #         options["PlottedKPoints"] = "1:-1"
        #     else:
        #         kpoints = []
        #         for chunk in P["selected k-points"].split(","):
        #             chunk = chunk.strip()
        #             if ":" in chunk or ".." in chunk:
        #                 if ":" in chunk:
        #                     first, last = chunk.split(":")
        #                 elif ".." in chunk:
        #                     first, last = chunk.split("..")
        #                 first = int(first.strip())
        #                 last = int(last.strip())

        #                 if first < 1:
        #                     first = 1

        #                 if last > last_kpoint:
        #                     last = last_kpoint

        #                 kpoints.extend(range(first, last + 1))
        #             else:
        #                 first = int(chunk.strip())
        #                 if first > 0 and first <= last_kpoint:
        #                     kpoints.append(first)
        #         options["PlottedKPoints"] = kpoints

        lines.append("")
        return lines

    def run(self, printer=printer, lines=None):
        """Get the input for an energy step.

        Parameters
        ----------
        None

        Returns
        -------
        str
            The input for FHI-aims
        """
        if lines is None:
            lines = []

        # Get the values of the parameters, dereferencing any variables
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        _, configuration = self.get_system_configuration()

        # Print what we are doing
        printer.important(__(self.description_text(P), indent=self.indent))

        directory = Path(self.directory)
        directory.mkdir(parents=True, exist_ok=True)

        model = P["submodel"]
        if " : " in model:
            model = model.split(" : ")[0].strip()
        lines.append("output                   json_log")
        lines.append(f"xc                       {model}")
        lines.append(f"charge                   {configuration.charge}")

        # Handle spin
        multiplicity = configuration.spin_multiplicity
        self.is_spin_polarized = False
        if P["spin_polarization"] == "none":
            lines.append("spin                      none")
        else:
            atoms = configuration.atoms
            have_spins = "spin" in atoms
            if have_spins:
                for tmp in atoms["spin"]:
                    if tmp is None:
                        have_spins = False
                        break
            if have_spins:
                self.is_spin_polarized = True
                lines.append("spin                     collinear")
                if P["fixed_spin_moment"] == "yes":
                    lines.append(f"fixed_spin_moment        {multiplicity-1}")
                elif isinstance(P["fixed_spin_moment"], int):
                    lines.append(f"fixed_spin_moment        {P['fixed_spin_moment']-1}")
            else:
                lines.append("spin                     none")
        lines.append("output                   Mulliken")

        if P["relativity"] == "atomic ZORA approximation":
            lines.append("relativistic             atomic_zora scalar")
        else:
            lines.append("relativistic             none")
        if P["calculate_gradients"]:
            lines.append("compute_forces           .true.")
        if "MBD-NL" in P["dispersion"]:
            lines.append("many_body_dispersion_nl")
        elif "MBD@rsSCS" in P["dispersion"]:
            lines.append("many_body_dispersion")

        if configuration.periodicity != 0:
            if "explicit" in P["k-grid method"]:
                lines.append(f"k_grid                   {P['na']} {P['nb']} {P['nc']}")
            else:
                lengths = configuration.cell.reciprocal_lengths()
                spacing = P["k-spacing"].to("1/Å").magnitude
                na = round(lengths[0] / spacing)
                nb = round(lengths[0] / spacing)
                nc = round(lengths[0] / spacing)
                na = na if na > 0 else 1
                nb = nb if nb > 0 else 1
                nc = nc if nc > 0 else 1
                if P["odd grid"]:
                    na = na + 1 if na % 2 == 0 else na
                    nb = nb + 1 if nb % 2 == 0 else nb
                    nc = nc + 1 if nc % 2 == 0 else nc

                lines.append(f"k_grid                   {P['na']} {P['nb']} {P['nc']}")

                if P["centering"] == "𝚪-centered":
                    oa = 0.0 if na % 2 == 1 else 1 / (2 * na)
                    ob = 0.0 if nb % 2 == 1 else 1 / (2 * nb)
                    oc = 0.0 if nc % 2 == 1 else 1 / (2 * nc)
                elif P["centering"] == "off center":
                    oa = 0.0 if na % 2 == 0 else 1 / (2 * na)
                    ob = 0.0 if nb % 2 == 0 else 1 / (2 * nb)
                    oc = 0.0 if nc % 2 == 0 else 1 / (2 * nc)
                elif P["centering"] == "Monkhorst-Pack":
                    oa = 0.0 if na % 2 == 1 else 0.5 - 1 / (2 * na)
                    ob = 0.0 if nb % 2 == 1 else 0.5 - 1 / (2 * nb)
                    oc = 0.0 if nc % 2 == 1 else 0.5 - 1 / (2 * nc)
                else:
                    raise RuntimeError(
                        f"Don't recognize k-space grid centering {P['centering']}"
                    )
                lines.append(f"k_offset                 {oa:8.6f} {ob:8.6f} {oc:8.6f}")

                lines.append(
                    f"occupation_type          {P['occupation type'].lower()} "
                    f"{P['smearing width'].m_as('eV'):.4f}"
                )

        # Any plotting we need to do (orbitals, density, ...)
        lines.extend(self.plot_control(P, configuration))

        data = "\n".join(lines)
        data += self._basis_sets(
            P, configuration.atoms.symbols, configuration.atoms.atomic_numbers
        )

        files = {
            "control.in": data,
            "geometry.in": self._geometry(configuration),
        }

        return_files = ["aims.out", "geometry.in.next_step", "*.cube", "*.json"]
        self.run_aims(files, return_files)

        self.analyze(configuration=configuration)
