# -*- coding: utf-8 -*-

"""The graphical part of a Optimization step"""

import logging
import pprint  # noqa: F401
import tkinter as tk
import tkinter.ttk as ttk

import fhi_aims_step
from seamm_util import ureg, Q_, units_class  # noqa: F401, E999
import seamm_widgets as sw

logger = logging.getLogger(__name__)


class TkOptimization(fhi_aims_step.TkEnergy):
    """
    The graphical part of a Optimization step in a flowchart.

    Attributes
    ----------
    tk_flowchart : TkFlowchart = None
        The flowchart that we belong to.
    node : Node = None
        The corresponding node of the non-graphical flowchart
    canvas: tkCanvas = None
        The Tk Canvas to draw on
    dialog : Dialog
        The Pmw dialog object
    x : int = None
        The x-coordinate of the center of the picture of the node
    y : int = None
        The y-coordinate of the center of the picture of the node
    w : int = 200
        The width in pixels of the picture of the node
    h : int = 50
        The height in pixels of the picture of the node
    self[widget] : dict
        A dictionary of tk widgets built using the information
        contained in Optimization_parameters.py

    See Also
    --------
    Optimization, TkOptimization,
    OptimizationParameters,
    """

    def __init__(
        self,
        tk_flowchart=None,
        node=None,
        canvas=None,
        x=None,
        y=None,
        w=200,
        h=50,
        my_logger=logger,
    ):
        """
        Initialize a graphical node.

        Parameters
        ----------
        tk_flowchart: Tk_Flowchart
            The graphical flowchart that we are in.
        node: Node
            The non-graphical node for this step.
        namespace: str
            The stevedore namespace for finding sub-nodes.
        canvas: Canvas
           The Tk canvas to draw on.
        x: float
            The x position of the nodes center on the canvas.
        y: float
            The y position of the nodes cetner on the canvas.
        w: float
            The nodes graphical width, in pixels.
        h: float
            The nodes graphical height, in pixels.

        Returns
        -------
        None
        """
        self.dialog = None

        super().__init__(
            tk_flowchart=tk_flowchart,
            node=node,
            canvas=canvas,
            x=x,
            y=y,
            w=w,
            h=h,
            my_logger=my_logger,
        )

    def create_dialog(self, title="Optimization"):
        """
        Create the dialog. A set of widgets will be chosen by default
        based on what is specified in the Optimization_parameters
        module.

        Parameters
        ----------
        None

        Returns
        -------
        None

        See Also
        --------
        TkOptimization.reset_dialog
        """

        super().create_dialog(title=title)

        # Shortcut for parameters
        P = self.node.parameters

        # Frame to isolate widgets
        opt_frame = self["optimization frame"] = ttk.LabelFrame(
            self["main frame"],
            borderwidth=4,
            relief="sunken",
            text="Optimization Parameters",
            labelanchor="n",
            padding=10,
        )

        for key in fhi_aims_step.OptimizationParameters.parameters:
            self[key] = P[key].widget(opt_frame)

        # Create the structure-handling widgets
        sframe = self["structure frame"] = ttk.LabelFrame(
            self["main frame"], text="Configuration Handling", labelanchor=tk.N
        )
        row = 0
        widgets = []
        for key in ("structure handling", "system name", "configuration name"):
            self[key] = P[key].widget(sframe)
            self[key].grid(row=row, column=0, sticky=tk.EW)
            widgets.append(self[key])
            row += 1
        sw.align_labels(widgets, sticky=tk.E)

        # and lay them out
        self.reset_dialog()

    def reset_dialog(self, widget=None):
        """Layout the widgets in the dialog.

        The widgets are chosen by default from the information in
        Optimization_parameter.

        This function simply lays them out row by row with
        aligned labels. You may wish a more complicated layout that
        is controlled by values of some of the control parameters.
        If so, edit or override this method

        Parameters
        ----------
        widget : Tk Widget = None

        Returns
        -------
        None

        See Also
        --------
        TkOptimization.create_dialog
        """

        row = super().reset_dialog()

        self["optimization frame"].grid(row=row, column=0, sticky=tk.N, pady=5)
        self["structure frame"].grid(
            row=row, column=1, columnspan=2, sticky=tk.N, pady=5
        )
        row += 1

        self.reset_optimization_frame()

        return row

    def reset_optimization_frame(self):
        """Layout the optimization frame according to the current values."""
        frame = self["optimization frame"]
        for slave in frame.grid_slaves():
            slave.grid_forget()

        widgets = []
        row = 0

        for key in ("force_convergence", "optimize_cell", "pressure"):
            w = self[key]
            w.grid(row=row, column=0, columnspan=3, sticky=tk.W)
            widgets.append(w)
            row += 1

        sw.align_labels(widgets, sticky=tk.E)

        frame.columnconfigure(0, minsize=50)

        return row
