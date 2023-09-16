# -*- coding: utf-8 -*-

"""This file contains metadata describing the results from FHIaims
"""

metadata = {}

"""Description of the computational models for FHIaims.

Hamiltonians, approximations, and basis set or parameterizations,
only if appropriate for this code. For example::

    metadata["computational models"] = {
        "Hartree-Fock": {
            "models": {
                "PM7": {
                    "parameterizations": {
                        "PM7": {
                            "elements": "1-60,62-83",
                            "periodic": True,
                            "reactions": True,
                            "optimization": True,
                            "code": "mopac",
                        },
                        "PM7-TS": {
                            "elements": "1-60,62-83",
                            "periodic": True,
                            "reactions": True,
                            "optimization": False,
                            "code": "mopac",
                        },
                    },
                },
            },
        },
    }
"""

metadata["computational models"] = {
    "Density Functional Theory (DFT)": {
        "models": {
            "Local-density approximation (LDA)": {
                "parameterizations": {
                    "vwn : Vosko-Wilk-Nusair": {
                        "gui": "metal/energy",
                        "description": "LDA of Vosko, Wilk, and Nusair 1980 [233].",
                    },
                    "pw-lda : Perdew-Wang": {
                        "gui": "metal/energy",
                        "description": (
                            "Homogeneous electron gas based on Ceperley and Alder [42] "
                            "as parameterized by Perdew and Wang 1992 [183]. "
                            "Recommended LDA parameterization."
                        ),
                    },
                    "pz-lda : Perdew-Zunger": {
                        "gui": "metal/energy",
                        "description": (
                            "Homogeneous electron gas based on Ceperley and Alder [42],"
                            " as parameterized by Perdew and Zunger 1981 [184]"
                        ),
                    },
                    "vwn-gauss : VWN based on random phase approx.": {
                        "gui": "standard",
                        "description": (
                            "LDA of Vosko, Wilk, and Nusair 1980, but based on the "
                            "random phase approximation [210]. Do not use this LDA "
                            "unless for one specific reason: In the B3LYP "
                            "implementation of the Gaussian code, this functional "
                            "is allegedly used instead of the correct VWN functional. "
                            "It is therefore now present in many reference results in "
                            "the literature, and also available here for comparison."
                        ),
                    },
                }
            },
            "Generalized-gradient approximations (GGA)": {
                "parameterizations": {
                    "pbe : Perdew, Burke and Ernzerhof": {
                        "gui": "metal/energy molecule/energy",
                        "description": "GGA of Perdew, Burke and Ernzerhof 1997 [181].",
                    },
                    "am05 : Armiento and Mattsson": {
                        "gui": "standard",
                        "description": (
                            "GGA functional designed to include surface effects in "
                            "self-consistent density functional theory, according to "
                            "Armiento and Mattsson [9]"
                        ),
                    },
                    "blyp : Becke and Lee-Yang-Parr": {
                        "gui": "standard",
                        "description": (
                            "The BLYP functional: Becke (1988) exchange [20] and "
                            "Lee-Yang-Parr correlation [150]."
                        ),
                    },
                    "pbeint": {
                        "gui": "standard",
                        "description": "PBEint functional of Ref. [67]",
                    },
                    "pbesol : modified PBE GGA": {
                        "gui": "metal/energy",
                        "description": "Modified PBE GGA according to Ref. [187].",
                    },
                    "rpbe : the RPBE modified PBE functional": {
                        "gui": "standard",
                        "description": (
                            "The RPBE modified PBE functional according to Ref. [93]."
                        ),
                    },
                    "revpbe : the revPBE modified PBE GGA": {
                        "gui": "standard",
                        "description": (
                            "The revPBE modified PBE GGA suggested in Ref. [247]."
                        ),
                    },
                    "r48pbe : 0.52*pbe and 0.48*rpbe": {
                        "gui": "standard",
                        "description": (
                            "The mixed functional containing 0.52*pbe and 0.48*rpbe "
                            "according to Ref. [173]"
                        ),
                    },
                    "pw91_gga : Perdew-Wang 1991 GGA": {
                        "gui": "metal/energy",
                        "description": (
                            "GGA according to Perdew and Wang, usually referred to as "
                            "'Perdew-Wang 1991 GGA'. This GGA is most accessibly "
                            "described in Reference 26 and 27 of Ref. [182]. Note "
                            "that the often mis-quoted reference [183] does not(!) "
                            "describe the Perdew-Wang GGA but instead only the "
                            "correlation part of the local-density approximation "
                            "described above."
                        ),
                    },
                    "b86bbpe : Becke’s B86b + PBE": {
                        "gui": "molecule/energy",
                        "description": (
                            "Becke’s B86b exchange[19] plus PBE correlation[181]."
                        ),
                    },
                },
            },
            "Meta-generalized gradient approximations (meta-GGA)": {
                "parameterizations": {
                    "m06-l : Truhlar’s optimized meta-GGA": {
                        "gui": "recommended",
                        "description": (
                            "Truhlar’s optimized meta-GGA of the 'M06' suite of "
                            "functionals. [250]"
                        ),
                    },
                    "m11-l : Truhlar’s optimized range-separated local meta-GGA": {
                        "gui": "recommended",
                        "description": (
                            "Truhlar’s optimized range-separated local meta-GGA of the "
                            "'M11' suite of functionals. [191]"
                        ),
                    },
                    "revtpss": {
                        "gui": "standard",
                        "description": (
                            "Meta-GGA revTPSS functional of Ref. [185, 186]",
                        ),
                    },
                    "tpss": {
                        "gui": "recommended",
                        "description": "Meta-GGA TPSS functional of Ref. [223]",
                    },
                    "tpssloc": {
                        "gui": "standard",
                        "description": (
                            "Meta-GGA TPSSloc functional, thanks to E. Fabiano and "
                            "F. Della Sala. L.A. Constantin, E. Fabiano, F.Della Sala, "
                            "Ref. [51]."
                        ),
                    },
                    "scan or SCAN:": {
                        "gui": "recommended",
                        "description": (
                            "'Strongly Constrained and Appropriately Normed Semilocal "
                            "Density Functional,' i.e., the SCAN meta-GGA functional "
                            "by Sun, Ruzsinszky, and Perdew.[219]"
                        ),
                    },
                },
            },
            "Hybrid functionals and Hartree-Fock": {
                "parameterizations": {
                    "b3lyp": {
                        "gui": "molecule/energy",
                        "description": (
                            "'B3LYP' hybrid functional as allegedly implemented in the "
                            "Gaussian code (i.e., using the RPA version of the "
                            "Vosko-Wilk-Nusair local-density approximation, see Refs. "
                            "[233, 210] for details). Note that this is therefore not "
                            "exactly the same B3LYP as originally described by Becke "
                            "in 1993."
                        ),
                    },
                    "hf : Hartree-Fock": {
                        "gui": "standard",
                        "description": "Hartree-Fock exchange, only",
                    },
                    "hse03 : Heyd, Scuseria and Ernzerhof": {
                        "gui": "standard",
                        "description": (
                            "Hybrid functional as used in Heyd, Scuseria and Ernzerhof "
                            "[105, 106]. In this functional, 25 % of the exchange "
                            "energy is split into a short-ranged, screened Hartree-Fock"
                            " part, and a PBE GGA-like functional for the longrange "
                            "part of exchange. The remaining 75 % exchange and full "
                            "correlation energy are treated as in PBE. As clarified in "
                            "Refs. [141, 106], two different screening parameters were "
                            "used in the short-range exchange part and longrange "
                            "exchange part of the original HSE functional, "
                            "respectively. The ’hse03’ functional in FHI-aims "
                            "reproduces these original values exactly."
                        ),
                    },
                    "hse06 : Heyd, Scuseria and Ernzerhof": {
                        "gui": "molecule/energy",
                        "description": (
                            "Hybrid functional according to Heyd, Scuseria and "
                            "Ernzerhof [105], following the naming convention "
                            "suggested in Ref. [141]. In this case, the additional "
                            "option value is needed, representing the single real, "
                            "positive screening parameter omega as clarified in Ref. "
                            "[141]. In this functional, 25 % of the exchange energy is "
                            "split into a short-ranged, screened Hartree-Fock part, "
                            "and a PBE GGA-like functional for the long-range part of "
                            "exchange. The remaining 75 % exchange and full "
                            "correlation energy are treated as in PBE."
                        ),
                    },
                    "pbe0": {
                        "gui": "molecule/energy",
                        "description": (
                            "PBE0 hybrid functional [1], mixing 75 % GGA exchange with "
                            "25 % Hartree-Fock exchange"
                        ),
                    },
                    "pbesol0": {
                        "gui": "recommended",
                        "description": (
                            "Hybrid functional in analogy to PBE0 [1], except that the "
                            "PBEsol [187] GGA functionals are used, mixing 75 % GGA "
                            "exchange with 25 % Hartree-Fock exchange."
                        ),
                    },
                    "b86bpbe-25": {
                        "gui": "molecule/energy",
                        "description": (
                            "B86bPBE hybrid functional [19, 181], mixing 75 % GGA "
                            "exchange with 25 % Hartree-Fock exchange."
                        ),
                    },
                    "b86bpbe-50": {
                        "gui": "standard",
                        "description": (
                            "B86bPBE hybrid functional [19, 181], mixing 75 % GGA "
                            "exchange with 50 % Hartree-Fock exchange."
                        ),
                    },
                    "lc_wpbeh": {
                        "gui": "standard",
                        "description": (
                            "Range separated hybrid functional LC-!PBEh using 100 % "
                            "Hartree-Fock exchange in the long-range part and omegaPBE "
                            "[179] in the shortrange part. The full correlation energy "
                            "is treated as in PBE."
                        ),
                    },
                },
            },
            "Hybrid meta generalized gradient approximation (Hybrid meta-GGA)": {
                "parameterizations": {
                    "m06": {
                        "gui": "recommended",
                        "description": (
                            "Truhlar’s optimized hybrid meta-GGA of the 'M06' suite of "
                            "functionals; with 27% exact exchange. [249]"
                        ),
                    },
                    "m06-2x": {
                        "gui": "standard",
                        "description": (
                            "Truhlar’s optimized hybrid meta-GGA of the 'M06' suite of "
                            "functionals, with double contribution (54%) from the "
                            "hartree-fock exact exchange. [249]"
                        ),
                    },
                    "m06-hf": {
                        "gui": "standard",
                        "description": (
                            "Truhlar’s optimized hybrid meta-GGA of the 'M06' suite of "
                            "functionals, with 100% exact exchage contribution. [248]"
                        ),
                    },
                    "m08-hx": {
                        "gui": "recommended",
                        "description": (
                            "Truhlar’s optimized hybrid meta-GGA of the 'M08' suite of "
                            "functionals, with 52.23% contribution from the "
                            "hartree-fock exact exchange. [251]"
                        ),
                    },
                    "m08-so": {
                        "gui": "standard",
                        "description": (
                            "Truhlar’s optimized hybrid meta-GGA of the 'M08' suite of "
                            "functionals, with 56.79% contribution from the "
                            "hartree-fock exact exchange. [251]"
                        ),
                    },
                    "m11": {
                        "gui": "recommended",
                        "description": (
                            "Truhlar’s optimized range-separated local meta-GGA of the "
                            "'M11' suite of functionals [190]. The range-separation "
                            "variable is also hardcoded in this implementation with "
                            "omega = 0.25 bohr−1"
                        ),
                    },
                },
            },
            # "": {
            #     "parameterizations": {
            #         "": {
            #             "description": (
            #             ),
            #         },
            #         "": {
            #             "description": (
            #             ),
            #         },
            #         "": {
            #             "description": (
            #             ),
            #         },
            #         "": {
            #             "description": (
            #             ),
            #         },
            #         "": {
            #             "description": (
            #             ),
            #         },
            #     },
            # },
        }
    }
}

"""Description of the FHIaims keywords.

(Only needed if this code uses keywords)

Fields
------
description : str
    A human readable description of the keyword.
takes values : int (optional)
    Number of values the keyword takes. If missing the keyword takes no values.
default : str (optional)
    The default value(s) if the keyword takes values.
format : str (optional)
    How the keyword is formatted in the MOPAC input.

For example::
    metadata["keywords"] = {
        "0SCF": {
            "description": "Read in data, then stop",
        },
        "ALT_A": {
            "description": "In PDB files with alternative atoms, select atoms A",
            "takes values": 1,
            "default": "A",
            "format": "{}={}",
        },
    }
"""
# metadata["keywords"] = {
# }

"""Properties that FHIaims produces.
`metadata["results"]` describes the results that this step can produce. It is a
dictionary where the keys are the internal names of the results within this step, and
the values are a dictionary describing the result. For example::

    metadata["results"] = {
        "total_energy": {
            "calculation": [
                "energy",
                "optimization",
            ],
            "description": "The total energy",
            "dimensionality": "scalar",
            "methods": [
                "ccsd",
                "ccsd(t)",
                "dft",
                "hf",
            ],
            "property": "total energy#Psi4#{model}",
            "type": "float",
            "units": "E_h",
        },
    }

Fields
______

calculation : [str]
    Optional metadata describing what subtype of the step produces this result.
    The subtypes are completely arbitrary, but often they are types of calculations
    which is why this is name `calculation`. To use this, the step or a substep
    define `self._calculation` as a value. That value is used to select only the
    results with that value in this field.

description : str
    A human-readable description of the result.

dimensionality : str
    The dimensions of the data. The value can be "scalar" or an array definition
    of the form "[dim1, dim2,...]". Symmetric tringular matrices are denoted
    "triangular[n,n]". The dimensions can be integers, other scalar
    results, or standard parameters such as `n_atoms`. For example, '[3]',
    [3, n_atoms], or "triangular[n_aos, n_aos]".

methods : str
    Optional metadata like the `calculation` data. `methods` provides a second
    level of filtering, often used for the Hamiltionian for *ab initio* calculations
    where some properties may or may not be calculated depending on the type of
    theory.

property : str
    An optional definition of the property for storing this result. Must be one of
    the standard properties defined either in SEAMM or in this steps property
    metadata in `data/properties.csv`.

type : str
    The type of the data: string, integer, or float.

units : str
    Optional units for the result. If present, the value should be in these units.
"""
metadata["results"] = {
    "total_energy": {
        "calculation": [
            "energy",
            "optimization",
        ],
        "description": "The total energy",
        "dimensionality": "scalar",
        "property": "total energy#FHIaims#{model}",
        "type": float,
        "units": "eV",
        "json_section": "final_output",
        "re": (
            r"Total energy of the DFT / Hartree-Fock s.c.f. calculation      :"
            r" *([-+.0-9]+) eV"
        ),
    },
    "dispersion_energy": {
        "calculation": [
            "energy",
            "optimization",
        ],
        "description": "vdW energy correction",
        "dimensionality": "scalar",
        "type": float,
        "units": "eV",
        "re": r"Libmbd: Evaluated energy: *([-+E.0-9]+)",
    },
    "total_number_of_loops": {
        "calculation": [
            "energy",
            "optimization",
        ],
        "description": "Number of SCF iterations",
        "dimensionality": "scalar",
        "type": int,
        "json_section": "final_output",
    },
    "relaxation_step_number": {
        "calculation": [
            "optimization",
        ],
        "description": "Number of geometry steps",
        "dimensionality": "scalar",
        "type": int,
        "json_section": "final_output",
    },
    "maximum_force": {
        "calculation": [
            "optimization",
        ],
        "description": "Maximum force",
        "dimensionality": "scalar",
        "type": float,
        "units": "eV/Å",
        "re": r"Maximum force component is *([-+E.0-9]+) +eV/A",
    },
    "norm_force_atoms": {
        "calculation": [
            "optimization",
        ],
        "description": "Norm of force on atoms",
        "dimensionality": "scalar",
        "type": float,
        "units": "eV/Å",
        "re": r"\|\| Forces on atoms   \|\| = *([-+E.0-9]+) +eV/A",
    },
    "n_basis": {
        "description": "Number of basis fnctns",
        "dimensionality": "scalar",
        "type": int,
        "json_section": "final_output",
    },
    "n_electrons": {
        "description": "Number of electrons",
        "dimensionality": "scalar",
        "type": float,
        "json_section": "final_output",
    },
    "n_spin": {
        "description": "Number of spins",
        "dimensionality": "scalar",
        "type": int,
        "json_section": "final_output",
    },
    "time_total": {
        "description": "Total cpu time",
        "dimensionality": "scalar",
        "type": float,
        "json_section": "final_output",
    },
    "clock_time_total": {
        "description": "Total wallclock time",
        "dimensionality": "scalar",
        "type": float,
        "json_section": "final_output",
    },
    "total_energy^": {
        "calculation": [
            "energy",
            "optimization",
        ],
        "description": "SCF iteration energy",
        "dimensionality": "[n_iterations]",
        "type": float,
        "units": "eV",
        "json_section": "scf_iteration",
    },
    "change_charge_density": {
        "description": "SCF final delta charge density",
        "dimensionality": "[n_iterations]",
        "type": float,
        "json_section": "scf_iteration",
    },
    "change_spin_density": {
        "description": "SCF final delta spin density",
        "dimensionality": "[n_iterations]",
        "type": float,
        "json_section": "scf_iteration",
    },
    "change_sum_eigenvalues": {
        "description": "SCF final delta eigenvalue sum",
        "dimensionality": "[n_iterations]",
        "type": float,
        "json_section": "scf_iteration",
    },
    "change_forces": {
        "description": "SCF final delta forces",
        "dimensionality": "[n_iterations]",
        "type": float,
        "json_section": "scf_iteration",
    },
    "atoms_proj_charge": {
        "description": "Mulliken charges on atoms",
        "dimensionality": "[n_atoms]",
        "type": float,
        "json_section": "mulliken",
    },
    "atoms_proj_spin": {
        "description": "Mulliken spins on atoms",
        "dimensionality": "[n_atoms]",
        "type": float,
        "json_section": "mulliken",
    },
    "total_spin": {
        "description": "Total spin",
        "dimensionality": "scalar",
        "type": float,
        "json_section": "mulliken",
    },
}
