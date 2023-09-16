# -*- coding: utf-8 -*-
"""
Control parameters for the Optimization step in a SEAMM flowchart
"""

import logging
import fhi_aims_step
import seamm
import pprint  # noqa: F401

logger = logging.getLogger(__name__)


class OptimizationParameters(fhi_aims_step.EnergyParameters):
    """
    The control parameters for Optimization.

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
    Optimization, TkOptimization, Optimization OptimizationParameters, OptimizationStep
    """

    parameters = {
        "force_convergence": {
            "default": 1.0e-2,
            "kind": "float",
            "default_units": "eV/Å",
            "enumeration": tuple(),
            "format_string": ".4f",
            "description": "Force convergence:",
            "help_text": "The convergence criterion for the force in the optimization",
        },
        "optimize_cell": {
            "default": "yes",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": ("yes", "fixing the angles", "no"),
            "format_string": "",
            "description": "Optimize the cell (if periodic):",
            "help_text": "Allow the lattice vectors to change during optimization. ",
        },
        "pressure": {
            "default": 0.0,
            "kind": "float",
            "default_units": "GPa",
            "enumeration": tuple(),
            "format_string": ".1f",
            "description": "Pressure:",
            "help_text": "The applied pressure.",
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

        logger.debug("OptimizationParameters.__init__")

        super().__init__(
            defaults={
                **OptimizationParameters.parameters,
                **seamm.standard_parameters.structure_handling_parameters,
                **defaults,
            },
            data=data,
        )

        # Do any local editing of defaults
        tmp = self["configuration name"]
        tmp._data["enumeration"] = ["optimized with {model}", *tmp.enumeration[1:]]
        tmp.default = "keep current name"

        tmp = self["configuration name"]
        tmp._data["enumeration"] = ["optimized with {model}", *tmp.enumeration]
        tmp.default = "optimized with {model}"
