# -*- coding: utf-8 -*-

"""The graphical part of a Energy step"""

import logging
import pprint  # noqa: F401
import tkinter as tk
import tkinter.ttk as ttk

import fhi_aims_step  # noqa: F401, E999
import seamm
from seamm_util import ureg, Q_, units_class  # noqa: F401, E999
import seamm_widgets as sw

logger = logging.getLogger(__name__)


class TkEnergy(seamm.TkNode):
    """
    The graphical part of a Energy step in a flowchart.

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
        contained in Energy_parameters.py

    See Also
    --------
    Energy, TkEnergy,
    EnergyParameters,
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

    def create_dialog(self, title="Energy"):
        """
        Create the dialog. A set of widgets will be chosen by default
        based on what is specified in the Energy_parameters
        module.

        Parameters
        ----------
        None

        Returns
        -------
        None

        See Also
        --------
        TkEnergy.reset_dialog
        """

        # Shortcut for parameters
        P = self.node.parameters

        frame = super().create_dialog(title="Energy")

        # Make scrollable in case too large
        self["scrolled frame"] = sw.ScrolledFrame(frame)
        self["scrolled frame"].grid(row=0, column=0, sticky=tk.NSEW)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        main_frame = self["main frame"] = self["scrolled frame"].interior()

        # Then create the widgets
        for key in ("gui", "calculate_gradients"):
            self[key] = P[key].widget(main_frame)

        # Patch width of GUI widget ... it is too wide by default
        self["gui"].configure(width=75)
        self["gui"].combobox.state(["readonly"])

        # Frame to isolate widgets
        e_frame = self["energy frame"] = ttk.LabelFrame(
            main_frame,
            borderwidth=4,
            relief="sunken",
            text="Electronic Structure Definition",
            labelanchor="n",
            padding=10,
        )

        # Then create the widgets
        for key in fhi_aims_step.EnergyParameters.energy_parameters:
            self[key] = P[key].widget(e_frame)
            try:
                self[key].configure(width=45)
            except Exception:
                pass

        for key in ("gui", "basis_version", "model", "submodel"):
            self[key].bind("<<ComboboxSelected>>", self.reset_energy_frame)
            self[key].bind("<Return>", self.reset_energy_frame)
            self[key].bind("<FocusOut>", self.reset_energy_frame)

        # The k-space integration
        k_frame = self["k-space frame"] = ttk.LabelFrame(
            main_frame,
            borderwidth=4,
            relief="sunken",
            text="k-space integration (for periodic systems)",
            labelanchor="n",
            padding=10,
        )
        for key in fhi_aims_step.EnergyParameters.kspace_parameters:
            self[key] = P[key].widget(k_frame)

        for key in ("na", "nb", "nc"):
            self[key].entry.configure(width=4)

        for key in ("k-grid method", "occupation type"):
            self[key].bind("<<ComboboxSelected>>", self.reset_kspace_frame)
            self[key].bind("<Return>", self.reset_kspace_frame)
            self[key].bind("<FocusOut>", self.reset_kspace_frame)

        # A tab for output of orbitals, etc.
        notebook = self["notebook"]
        self["output frame"] = oframe = ttk.Frame(notebook)
        notebook.insert(self["results frame"], oframe, text="Output", sticky="new")

        # Frame to isolate widgets
        p_frame = self["plot frame"] = ttk.LabelFrame(
            self["output frame"],
            borderwidth=4,
            relief="sunken",
            text="Plots",
            labelanchor="n",
            padding=10,
        )

        for key in fhi_aims_step.EnergyParameters.output_parameters:
            self[key] = P[key].widget(p_frame)

        # Set the callbacks for changes
        for widget in ("orbitals",):
            w = self[widget]
            w.combobox.bind("<<ComboboxSelected>>", self.reset_plotting)
            w.combobox.bind("<Return>", self.reset_plotting)
            w.combobox.bind("<FocusOut>", self.reset_plotting)
        p_frame.grid(row=0, column=0, sticky="new")
        oframe.columnconfigure(0, weight=1)

        # and lay them out
        self.reset_plotting()

    def edit(self):
        """Present a dialog for editing this step's parameters.

        Subclasses can override this.
        """
        # Create the dialog if it doesn't exist
        if self.dialog is None:
            self.create_dialog()
            # After full creation, reset the dialog. This may do nothing,
            # or may layout the widgets, but can only be done after fully
            # creating the dialog.
            self.reset_dialog()
            # And resize the dialog, making it large
            screen_w = self.dialog.winfo_screenwidth()
            screen_h = self.dialog.winfo_screenheight()
            w = int(0.95 * screen_w)
            h = int(0.9 * screen_h)
            x = int(0.05 * screen_w / 2)
            y = int(0.1 * screen_h / 2)

            self.dialog.geometry(f"{w}x{h}+{x}+{y}")

        # And put it on-screen, the first time centered. If it contains
        # a subflowchart, save it so it can be restored on a 'Cancel'
        if self.tk_subflowchart is not None:
            self.tk_subflowchart.push()

        self.dialog.activate(geometry="centerscreenfirst")

    def reset_dialog(self, widget=None):
        """Layout the widgets in the dialog.

        The widgets are chosen by default from the information in
        Energy_parameter.

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
        TkEnergy.create_dialog
        """

        # Remove any widgets previously packed
        frame = self["main frame"]
        for slave in frame.grid_slaves():
            slave.grid_forget()

        # Shortcut for parameters
        P = self.node.parameters

        # keep track of the row in a variable, so that the layout is flexible
        # if e.g. rows are skipped to control such as "method" here
        row = 0

        # The level of the GUI
        self["gui"].grid(row=row, column=0, columnspan=4, pady=5)
        row += 1

        # The model for the calculation
        self["energy frame"].grid(row=row, column=0, columnspan=2, pady=5, sticky=tk.N)
        self["k-space frame"].grid(row=row, column=2, columnspan=2, pady=5, sticky=tk.N)
        row += 1

        # Other parameters for a single-point calculation
        if type(self) is fhi_aims_step.TkEnergy:
            keys = ["calculate_gradients"]
            for key in keys:
                self[key].grid(row=row, column=0, columnspan=4, pady=10)
                row += 1

        # Layout the energy widgets
        self.reset_energy_frame()
        self.reset_kspace_frame()

        # Setup the results if there are any
        have_results = (
            "results" in self.node.metadata and len(self.node.metadata["results"]) > 0
        )
        if have_results and "results" in P:
            self.setup_results()

        return row

    def reset_energy_frame(self, widget=None):
        """Layout the widgets in the dialog.

        The widgets are chosen by default from the information in
        Energy_parameter.

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
        TkEnergy.create_dialog
        """

        # Remove any widgets previously packed
        frame = self["energy frame"]
        for slave in frame.grid_slaves():
            slave.grid_forget()

        # Shortcut for parameters
        P = self.node.parameters

        # keep track of the row in a variable, so that the layout is flexible
        # if e.g. rows are skipped to control such as "method" here
        row = 0

        # The level of the gui
        tmp = self["gui"].get()
        if "energy" in tmp:
            if "molecules" in tmp:
                gui = "molecule/energy"
            elif " metallic" in tmp:
                gui = "metal/energy"
            else:
                gui = "standard"
        elif "band" in tmp:
            if "molecules" in tmp:
                gui = "molecule/band"
            elif " metallic" in tmp:
                gui = "metal/band"
            else:
                gui = "standard"
        else:
            gui = "experimental" if "experimental" in tmp else "standard"

        # The model for the calculation
        keys = ["model", "submodel"]
        model = self["model"].get()

        # And what models have available sublevels?
        model_data = self.node.metadata["computational models"][
            "Density Functional Theory (DFT)"
        ]["models"]
        models = []
        for tmp in model_data.keys():
            choices = model_data[tmp]["parameterizations"]
            if gui == "experimental":
                if len(choices) > 0:
                    models.append(tmp)
            elif gui == "standard":
                if (
                    len(
                        [
                            m
                            for m in choices.keys()
                            if "experimental" not in choices[m]["gui"]
                        ]
                    )
                    > 0
                ):
                    models.append(tmp)
            else:
                if len([m for m in choices.keys() if gui in choices[m]["gui"]]) > 0:
                    models.append(tmp)
        w = self["model"]
        if w.combobox.cget("values") != models:
            w.config(values=models)
            if not self.is_expr(model) and model not in models and len(models) > 0:
                w.set(models[0])
            else:
                w.set(model)

        # Fill out the possible submodels
        submodel = self["submodel"].get()
        choices = model_data[model]["parameterizations"]
        if gui == "experimental":
            submodels = [*choices.keys()]
        elif gui == "standard":
            submodels = [
                m for m in choices.keys() if "experimental" not in choices[m]["gui"]
            ]
        else:
            submodels = [m for m in choices.keys() if gui in choices[m]["gui"]]

        w = self["submodel"]
        if w.combobox.cget("values") != submodels:
            w.config(values=submodels)
            if (
                not self.is_expr(submodel)
                and submodel not in submodels
                and len(submodels) > 0
            ):
                w.set(submodels[0])
            else:
                w.set(submodel)

        # And the basis
        widgets = []
        keys.append("basis_version")

        basis_version = self["basis_version"].get()
        key = basis_version + "_level"
        if key in P:
            keys.append(key)
        else:
            tk.messagebox.showwarning(
                title=f"{basis_version} basis not supported yet",
                message=f"{basis_version} basis not supported yet",
            )

        keys.append("spin_polarization")
        keys.append("relativity")
        keys.append("dispersion")
        keys.append("primitive cell")

        for key in keys:
            self[key].grid(row=row, column=0, sticky=tk.EW)
            widgets.append(self[key])
            row += 1

        # Align the labels
        sw.align_labels(widgets, sticky=tk.E)

        # Setup the results if there are any
        have_results = (
            "results" in self.node.metadata and len(self.node.metadata["results"]) > 0
        )
        if have_results and "results" in P:
            self.setup_results()

    def reset_kspace_frame(self, widget=None):
        """Layout the widgets in the dialog.

        The widgets are chosen by default from the information in
        Energy_parameter.

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
        TkEnergy.create_dialog
        """

        # Remove any widgets previously packed
        frame = self["k-space frame"]
        for slave in frame.grid_slaves():
            slave.grid_forget()

        # keep track of the row in a variable, so that the layout is flexible
        # if e.g. rows are skipped to control such as "method" here
        row = 0

        # The model for the calculation
        key = "k-grid method"
        method = self[key].get()
        self[key].grid(row=row, column=0, columnspan=4, sticky=tk.W)
        row += 1

        if "explicit" in method:
            for col, key in enumerate(("na", "nb", "nc"), start=1):
                self[key].grid(row=row, column=col, sticky=tk.EW)
            row += 1
        else:
            widgets = []
            for key in ("k-spacing", "odd grid", "centering"):
                self[key].grid(row=row, column=1, columnspan=3, sticky=tk.EW)
                widgets.append(self[key])
                row += 1
            sw.align_labels(widgets, sticky=tk.E)
        frame.columnconfigure(0, minsize=30)

        key = "occupation type"
        smearing = self[key].get()
        self[key].grid(row=row, column=0, columnspan=4, sticky=tk.W)
        row += 1

        if smearing not in ("integer",):
            key = "smearing width"
            self[key].grid(row=row, column=1, columnspan=3, sticky=tk.W)
            row += 1

    def right_click(self, event):
        """
        Handles the right click event on the node.

        Parameters
        ----------
        event : Tk Event

        Returns
        -------
        None

        See Also
        --------
        TkEnergy.edit
        """

        super().right_click(event)
        self.popup_menu.add_command(label="Edit..", command=self.edit)

        self.popup_menu.tk_popup(event.x_root, event.y_root, 0)

    def reset_plotting(self, widget=None):
        frame = self["plot frame"]
        for slave in frame.grid_slaves():
            slave.grid_forget()

        plot_orbitals = self["orbitals"].get() == "yes"

        widgets = []

        row = 0
        for key in (
            "total density",
            "total spin density",
            "difference density",
            "orbitals",
        ):
            self[key].grid(row=row, column=0, columnspan=4, sticky=tk.EW)
            widgets.append(self[key])
            row += 1

        if plot_orbitals:
            key = "selected orbitals"
            self[key].grid(row=row, column=1, columnspan=4, sticky=tk.EW)
            row += 1
            key = "selected k-points"
            self[key].grid(row=row, column=1, columnspan=4, sticky=tk.EW)
            row += 1

        key = "region"
        self[key].grid(row=row, column=0, columnspan=4, sticky=tk.EW)
        widgets.append(self[key])
        row += 1

        key = "nx"
        self[key].grid(row=row, column=0, columnspan=2, sticky=tk.EW)
        widgets.append(self[key])
        self["ny"].grid(row=row, column=2, sticky=tk.EW)
        self["nz"].grid(row=row, column=3, sticky=tk.EW)

        sw.align_labels(widgets, sticky=tk.E)
        frame.columnconfigure(0, minsize=10)
        frame.columnconfigure(4, weight=1)

        return row
