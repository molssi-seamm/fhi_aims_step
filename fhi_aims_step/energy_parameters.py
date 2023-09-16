# -*- coding: utf-8 -*-
"""
Control parameters for the Energy step in a SEAMM flowchart
"""

import logging
import seamm
import pprint  # noqa: F401

logger = logging.getLogger(__name__)


class EnergyParameters(seamm.Parameters):  # noqa: E999
    """
    The control parameters for Energy.

    You need to replace the "time" entry in dictionary below these comments with the
    definitions of parameters to control this step. The keys are parameters for the
    current plugin,the values are dictionaries as outlined below.

    Examples
    --------
    ::

        parameters = {
            "time": {
                "default": 100.0,
                "kind": "float",
                "default_units": "ps",
                "enumeration": tuple(),
                "format_string": ".1f",
                "description": "Simulation time:",
                "help_text": ("The time to simulate in the dynamics run.")
            },
        }

    parameters : {str: {str: str}}
        A dictionary containing the parameters for the current step.
        Each key of the dictionary is a dictionary that contains the
        the following keys:

    parameters["default"] :
        The default value of the parameter, used to reset it.

    parameters["kind"] : enum()
        Specifies the kind of a variable. One of  "integer", "float", "string",
        "boolean", or "enum"

        While the "kind" of a variable might be a numeric value, it may still have
        enumerated custom values meaningful to the user. For instance, if the parameter
        is a convergence criterion for an optimizer, custom values like "normal",
        "precise", etc, might be adequate. In addition, any parameter can be set to a
        variable of expression, indicated by having "$" as the first character in the
        field. For example, $OPTIMIZER_CONV.

    parameters["default_units"] : str
        The default units, used for resetting the value.

    parameters["enumeration"]: tuple
        A tuple of enumerated values.

    parameters["format_string"]: str
        A format string for "pretty" output.

    parameters["description"]: str
        A short string used as a prompt in the GUI.

    parameters["help_text"]: str
        A longer string to display as help for the user.

    See Also
    --------
    Energy, TkEnergy, Energy EnergyParameters, EnergyStep
    """

    parameters = {
        "gui": {
            "default": (
                "with recommended features for energy or structure of molecules "
                "or nonmetallic solids"
            ),
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                (
                    "with recommended features for energy or structure involving "
                    "metallic solids"
                ),
                (
                    "with recommended features for energy or structure of molecules "
                    "or nonmetallic solids"
                ),
                "with recommended features for band structures of metallic solids",
                (
                    "with recommended features for orbital energies of molecules or "
                    "band structures for nonmetallic solids"
                ),
                "with all standard features",
                "including experimental features",
            ),
            "format_string": "",
            "description": "Configure GUI",
            "help_text": "How to configure the GUI",
        },
        "calculate_gradients": {
            "default": "no",
            "kind": "boolean",
            "default_units": "",
            "enumeration": ("yes", "no"),
            "format_string": "",
            "description": "Calculate gradients:",
            "help_text": (
                "Whether to calculate the gradients in a single-point calculation."
            ),
        },
        "results": {
            "default": {},
            "kind": "dictionary",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "",
            "description": "results",
            "help_text": "The results to save to variables or in tables.",
        },
    }

    energy_parameters = {
        "basis_version": {
            "default": "defaults_2020",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "defaults_2010",
                "defaults_2020",
                "NAO-VCC-nZ",
                "NAO-J-n",
                "non-standard/gaussian_tight_770",
                "non-standard/Tier2_aug2",
                "custom",
            ),
            "format_string": "",
            "description": "Basis set version:",
            "help_text": "The version of basis sets used.",
        },
        "defaults_2010_level": {
            "default": "light",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "light",
                "intermediate",
                "tight",
                "really_tight",
            ),
            "format_string": "",
            "description": "Basis set level:",
            "help_text": "The level of 2010 basis sets used.",
        },
        "defaults_2020_level": {
            "default": "light",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "light_spd/light",
                "light",
                "intermediate",
                "tight",
                "really_tight",
            ),
            "format_string": "",
            "description": "Basis set level:",
            "help_text": "The level of 2010 basis sets used.",
        },
        "NAO-VCC-nZ_level": {
            "default": "NAO-VCC-2Z",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "NAO-VCC-2Z",
                "NAO-VCC-3Z",
                "NAO-VCC-4Z",
                "NAO-VCC-5Z",
            ),
            "format_string": "",
            "description": "Basis set level:",
            "help_text": "The level of NAO-VCC (valence correlation) basis sets used.",
        },
        "NAO-J-n_level": {
            "default": "NAO-J-2",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "NAO-J-2",
                "NAO-J-3",
                "NAO-J-4",
                "NAO-J-5",
            ),
            "format_string": "",
            "description": "Basis set level:",
            "help_text": "The level of NAO-j (spin-coupling) basis sets used.",
        },
        "model": {
            "default": "Generalized-gradient approximations (GGA)",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "Local-density approximation (LDA)",
                "Generalized-gradient approximations (GGA)",
                "Meta-generalized gradient approximations (meta-GGA)",
                "Hartree-Fock and hybrid functionals",
                "Hybrid meta generalized gradient approximation (Hybrid meta-GGA)",
            ),
            "format_string": "",
            "description": "Computational model:",
            "help_text": "The high-level computational model employed.",
        },
        "submodel": {
            "default": "pbe : Perdew, Burke and Ernzerhof",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "pbe : Perdew, Burke and Ernzerhof",
                "am05 : Armiento and Mattsson",
                "blyp : Becke and Lee-Yang-Parr",
                "pbeint",
                "pbesol : modified PBE GGA",
                "rpbe : the RPBE modified PBE functional",
                "revpbe : the revPBE modified PBE GGA",
                "r48pbe : 0.52*pbe and 0.48*rpbe",
                "pw91_gga : Perdew-Wang 1991 GGA",
                "b86bbpe : Becke’s B86b + PBE",
            ),
            "format_string": "",
            "description": "Model version:",
            "help_text": "The version of the model employed.",
        },
        "spin_polarization": {
            "default": "default",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": ("default", "none"),
            "format_string": "",
            "description": "Spin polarized?:",
            "help_text": (
                "Whether to do a spin polarized calculation. The default is to do so "
                "if there are spins on any atoms. You can also turn this off, but "
                "cannot force a spin-polarized calculation without setting spins on "
                "one or more atoms in the structure."
            ),
        },
        "fixed_spin_moment": {
            "default": "no",
            "kind": "integer",
            "default_units": "",
            "enumeration": ("no", "yes"),
            "format_string": "",
            "description": "Fix the spin moment:",
            "help_text": (
                "Whether to fix the spin moment, by default to the configuration's "
                "multiplicity. You may also specifiy and integer multiplicity here."
            ),
        },
        "relativity": {
            "default": "atomic ZORA approximation",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": ("none", "atomic ZORA approximation"),
            "format_string": "",
            "description": "Relativity:",
            "help_text": "Whether and how to calculate relatavistic effects.",
        },
        "dispersion": {
            "default": "nonlocal many-body dispersion (MBD-NL)",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "none",
                "nonlocal many-body dispersion (MBD-NL)",
                "range-separated self-consistently screened (MBD@rsSCS)",
            ),
            "format_string": "",
            "description": "Long-range vdW term:",
            "help_text": (
                "Whether and how to calculate the many-body dispersions effects."
            ),
        },
        "primitive cell": {
            "default": "yes",
            "kind": "boolean",
            "default_units": "",
            "enumeration": ("yes", "no"),
            "format_string": "",
            "description": "If possible, use primitive cell:",
            "help_text": "Whether to use the primitive cell for the calculation.",
        },
    }

    kspace_parameters = {
        "k-grid method": {
            "default": "grid spacing",
            "kind": "string",
            "default_units": "",
            "enumeration": ("grid spacing", "explicit grid dimensions"),
            "format_string": "",
            "description": "Specify k-space grid using:",
            "help_text": "How to specify the k-space integration grid.",
        },
        "k-spacing": {
            "default": 0.2,
            "kind": "float",
            "default_units": "1/Å",
            "enumeration": None,
            "format_string": "",
            "description": "K-spacing:",
            "help_text": "The spacing of the grid in reciprocal space.",
        },
        "odd grid": {
            "default": "yes",
            "kind": "boolean",
            "default_units": "",
            "enumeration": ("yes", "no"),
            "format_string": "",
            "description": "Force to odd numbers:",
            "help_text": "Whether to force the grid sizes to odd numbers.",
        },
        "centering": {
            "default": "𝚪-centered",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "𝚪-centered",
                "off-center",
                "Monkhorst-Pack",
            ),
            "format_string": "",
            "description": "Centering of grid:",
            "help_text": "How to center the grid in reciprocal space.",
        },
        "occupation type": {
            "default": "Gaussian",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "Gaussian",
                "Methfessel-Paxton",
                "Fermi",
                "integer",
                "cubic",
                "cold",
            ),
            "format_string": "",
            "description": "Smearing:",
            "help_text": (
                "How occupy the orbitals, typically smearing the electrons as they "
                "would be at finite temperature."
            ),
        },
        "smearing width": {
            "default": 0.01,
            "kind": "float",
            "default_units": "eV",
            "enumeration": None,
            "format_string": ".3f",
            "description": "Width:",
            "help_text": "The smearing or broadening width.",
        },
        "na": {
            "default": 4,
            "kind": "integer",
            "default_units": "",
            "enumeration": None,
            "format_string": "",
            "description": "NPoints in a:",
            "help_text": (
                "Number of points in the first direction of the Brillouin zone."
            ),
        },
        "nb": {
            "default": 4,
            "kind": "integer",
            "default_units": "",
            "enumeration": None,
            "format_string": "",
            "description": "b:",
            "help_text": (
                "Number of points in the second direction of the Brillouin zone."
            ),
        },
        "nc": {
            "default": 4,
            "kind": "integer",
            "default_units": "",
            "enumeration": None,
            "format_string": "",
            "description": "c:",
            "help_text": (
                "Number of points in the third direction of the Brillouin zone."
            ),
        },
    }

    output_parameters = {
        "total density": {
            "default": "yes",
            "kind": "boolean",
            "default_units": "",
            "enumeration": ("yes", "no"),
            "format_string": "",
            "description": "Plot total density:",
            "help_text": "Whether to plot the total charge density.",
        },
        "total spin density": {
            "default": "yes",
            "kind": "boolean",
            "default_units": "",
            "enumeration": ("yes", "no"),
            "format_string": "",
            "description": "Plot total spin density:",
            "help_text": "Whether to plot the total spin density.",
        },
        "difference density": {
            "default": "yes",
            "kind": "boolean",
            "default_units": "",
            "enumeration": ("yes", "no"),
            "format_string": "",
            "description": "Plot difference density:",
            "help_text": "Whether to plot the difference density.",
        },
        "orbitals": {
            "default": "yes",
            "kind": "boolean",
            "default_units": "",
            "enumeration": ("yes", "no"),
            "format_string": "",
            "description": "Plot orbitals:",
            "help_text": "Whether to plot orbitals.",
        },
        "selected orbitals": {
            "default": "-1, HOMO, LUMO, +1",
            "kind": "string",
            "default_units": "",
            "enumeration": ("all", "-1, HOMO, LUMO, +1"),
            "format_string": "",
            "description": "Selected orbitals:",
            "help_text": "Which orbitals to plot.",
        },
        "selected k-points": {
            "default": "none",
            "kind": "string",
            "default_units": "",
            "enumeration": ("none", "all"),
            "format_string": "",
            "description": "For crystals, k-points:",
            "help_text": "Plots the orbitals at these k-points.",
        },
        "region": {
            "default": "default",
            "kind": "string",
            "default_units": "",
            "enumeration": ("default", "explicit"),
            "format_string": "",
            "description": "Region:",
            "help_text": "The region for the plots",
        },
        "nx": {
            "default": 50,
            "kind": "integer",
            "default_units": "",
            "enumeration": None,
            "format_string": "",
            "description": "Grid:",
            "help_text": "Number of grid points in first direction",
        },
        "ny": {
            "default": 50,
            "kind": "integer",
            "default_units": "",
            "enumeration": None,
            "format_string": "",
            "description": "x",
            "help_text": "Number of grid points in second direction",
        },
        "nz": {
            "default": 50,
            "kind": "integer",
            "default_units": "",
            "enumeration": None,
            "format_string": "",
            "description": "x",
            "help_text": "Number of grid points in first direction",
        },
    }

    def __init__(self, defaults={}, data=None):
        """
        Initialize the parameters, by default with the parameters defined above

        Parameters
        ----------
        defaults: dict
            A dictionary of parameters to initialize. The parameters
            above are used first and any given will override/add to them.
        data: dict
            A dictionary of keys and a subdictionary with value and units
            for updating the current, default values.

        Returns
        -------
        None
        """

        logger.debug("EnergyParameters.__init__")

        super().__init__(
            defaults={
                **EnergyParameters.parameters,
                **EnergyParameters.energy_parameters,
                **EnergyParameters.kspace_parameters,
                **EnergyParameters.output_parameters,
                **defaults,
            },
            data=data,
        )
