# -*- coding: utf-8 -*-

"""Non-graphical part of the FHI-aims step in a SEAMM flowchart
"""

import logging
from pathlib import Path
import pkg_resources
import pprint  # noqa: F401
import sys

import fhi_aims_step
import molsystem
import seamm
from seamm_util import ureg, Q_, getParser  # noqa: F401
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


class FHIaims(seamm.Node):
    """
    The non-graphical part of a FHI-aims step in a flowchart.

    Attributes
    ----------
    parser : configargparse.ArgParser
        The parser object.

    options : tuple
        It contains a two item tuple containing the populated namespace and the
        list of remaining argument strings.

    subflowchart : seamm.Flowchart
        A SEAMM Flowchart object that represents a subflowchart, if needed.

    parameters : FHIaimsParameters
        The control parameters for FHI-aims.

    See Also
    --------
    TkFHIaims,
    FHIaims, FHIaimsParameters
    """

    def __init__(
        self,
        flowchart=None,
        title="FHI-aims",
        namespace="org.molssi.seamm.fhi_aims",
        extension=None,
        logger=logger,
    ):
        """A step for FHI-aims in a SEAMM flowchart.

        You may wish to change the title above, which is the string displayed
        in the box representing the step in the flowchart.

        Parameters
        ----------
        flowchart: seamm.Flowchart
            The non-graphical flowchart that contains this step.

        title: str
            The name displayed in the flowchart.
        namespace : str
            The namespace for the plug-ins of the subflowchart
        extension: None
            Not yet implemented
        logger : Logger = logger
            The logger to use and pass to parent classes

        Returns
        -------
        None
        """
        logger.debug(f"Creating FHI-aims {self}")
        self.subflowchart = seamm.Flowchart(
            parent=self, name="FHI-aims", namespace=namespace
        )

        super().__init__(
            flowchart=flowchart,
            title="FHI-aims",
            extension=extension,
            module=__name__,
            logger=logger,
        )
        self.parameters = fhi_aims_step.FHIaimsParameters()

        self._metadata = fhi_aims_step.metadata

    @property
    def version(self):
        """The semantic version of this module."""
        return fhi_aims_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return fhi_aims_step.__git_revision__

    def analyze(self, indent="", **kwargs):
        """Do any analysis of the output from this step.

        Also print important results to the local step.out file using
        "printer".

        Parameters
        ----------
        indent: str
            An extra indentation for the output
        """
        # Get the first real node
        node = self.subflowchart.get_node("1").next()

        # Loop over the subnodes, asking them to do their analysis
        while node is not None:
            for value in node.description:
                printer.important(value)
                printer.important(" ")

            node.analyze()

            node = node.next()

    def create_parser(self):
        """Setup the command-line / config file parser"""
        parser_name = self.step_type
        parser = getParser()

        # Remember if the parser exists ... this type of step may have been
        # found before
        parser_exists = parser.exists(parser_name)

        # Create the standard options, e.g. log-level
        result = super().create_parser(name=parser_name)

        if parser_exists:
            return result

        # FHI-aims specific options

        parser.add_argument(
            parser_name,
            "--max-atoms-to-print",
            default=25,
            help="Maximum number of atoms to print charges, etc.",
        )

        parser.add_argument(
            parser_name,
            "--ncores",
            default="available",
            help=(
                "The maximum number of cores to use for FHI-aims. "
                "Default: all available cores."
            ),
        )
        parser.add_argument(
            parser_name,
            "--atoms-per-core",
            type=int,
            default="5",
            help="the optimal number of atoms per core for FHI-aims",
        )
        parser.add_argument(
            parser_name,
            "--html",
            action="store_true",
            help="whether to write out html files for graphs, etc.",
        )
        parser.add_argument(
            parser_name,
            "--modules",
            nargs="*",
            default=None,
            help="the environment modules to load for FHI-aims",
        )
        parser.add_argument(
            parser_name,
            "--path",
            default=None,
            help="the path to the FHI-aims executables",
        )
        parser.add_argument(
            parser_name,
            "--basis-path",
            default=None,
            help="the path to the basis sets",
        )
        parser.add_argument(
            parser_name,
            "--aims",
            default="aims.x",
            help="the executable for FHI-aims",
        )
        parser.add_argument(
            parser_name, "--mpiexec", default="mpiexec", help="the mpi executable"
        )

        return result

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
        self.subflowchart.root_directory = self.flowchart.root_directory

        # Get the first real node
        node = self.subflowchart.get_node("1").next()

        text = self.header + "\n\n"
        while node is not None:
            try:
                text += __(node.description_text(), indent=3 * " ").__str__()
            except Exception as e:
                print(f"Error describing fhi_aims flowchart: {e} in {node}")
                logger.critical(f"Error describing fhi_aims flowchart: {e} in {node}")
                raise
            except:  # noqa: E722
                print(
                    "Unexpected error describing fhi_aims flowchart: "
                    f"{sys.exc_info()[0]} in {str(node)}"
                )
                logger.critical(
                    "Unexpected error describing fhi_aims flowchart: "
                    f"{sys.exc_info()[0]} in {str(node)}"
                )
                raise
            text += "\n"
            node = node.next()

        return text

    def run(self):
        """Run a FHI-aims step.

        Parameters
        ----------
        None

        Returns
        -------
        seamm.Node
            The next node object in the flowchart.
        """
        next_node = super().run(printer)

        # Print our header to the main output
        printer.important(self.header)
        printer.important("")

        # Add the main citation for FHI-aims
        self.references.cite(
            raw=self._bibliography["BLUM20092175"],
            alias="FHI-aims",
            module="FHI-aims step",
            level=1,
            note="The principle citation for FHI-aims.",
        )

        # Get the first real node
        node = self.subflowchart.get_node("1").next()

        # And loop
        while node is not None:
            if node.is_runable:
                node.run()
            node = node.next()

        # Add other citations here or in the appropriate place in the code.
        # Add the bibtex to data/references.bib, and add a self.reference.cite
        # similar to the above to actually add the citation to the references.

        return next_node

    def set_id(self, node_id):
        """Set the id for node to a given tuple"""
        self._id = node_id

        # and set our subnodes
        self.subflowchart.set_ids(self._id)

        return self.next()
