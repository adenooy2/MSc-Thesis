"""
Python model 'V5_months_calibrated.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.functions import ramp
from pysd.py_backend.statefuls import Integ, Delay
from pysd import Component

__pysd_version__ = "3.7.1"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 276,
    "time_step": lambda: 1,
    "saveper": lambda: 12,
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Month",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP",
    units="Month",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Detection",
    units="People/Month",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_detection": 1, "cdr": 1},
    other_deps={
        "_delay_detection": {
            "initial": {"active": 1, "diagnosis_delay": 1},
            "step": {"active": 1, "diagnosis_delay": 1},
        }
    },
)
def detection():
    return _delay_detection() * cdr()


_delay_detection = Delay(
    lambda: active(),
    lambda: diagnosis_delay(),
    lambda: active(),
    lambda: 1,
    time_step,
    "_delay_detection",
)


@component.add(
    name="progression",
    units="People/Month",
    comp_type="Stateful",
    comp_subtype="Delay",
    depends_on={"_delay_progression": 1, "progression_rate": 1},
    other_deps={
        "_delay_progression": {
            "initial": {"latent_tb_infection": 1, "progression_time": 1},
            "step": {"latent_tb_infection": 1, "progression_time": 1},
        }
    },
)
def progression():
    return _delay_progression() * progression_rate()


_delay_progression = Delay(
    lambda: latent_tb_infection(),
    lambda: progression_time(),
    lambda: latent_tb_infection(),
    lambda: 1,
    time_step,
    "_delay_progression",
)


@component.add(
    name="Relapse",
    units="People/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"detected_and_treated_tb": 1, "relapse_rate": 1},
)
def relapse():
    return detected_and_treated_tb() * relapse_rate()


@component.add(
    name="CDR",
    units="1/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def cdr():
    return (0.46 + ramp(__data["time"], 0.0383 / 12, 16 * 12, 22 * 12)) / 12


@component.add(name="CFR", units="1/Month", comp_type="Constant", comp_subtype="Normal")
def cfr():
    return 0.089 / 12


@component.add(
    name="deaths TB",
    units="People/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"active": 1, "cfr": 1},
)
def deaths_tb():
    return active() * (cfr() / 12)


@component.add(
    name="progression time", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def progression_time():
    return 6


@component.add(
    name="Active",
    units="People",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_active": 1},
    other_deps={
        "_integ_active": {
            "initial": {"initial_incident": 1},
            "step": {
                "progression": 1,
                "relapse": 1,
                "deaths_a": 1,
                "deaths_tb": 1,
                "detection": 1,
            },
        }
    },
)
def active():
    return _integ_active()


_integ_active = Integ(
    lambda: progression() + relapse() - deaths_a() - deaths_tb() - detection(),
    lambda: initial_incident(),
    "_integ_active",
)


@component.add(
    name="birth rate",
    units="1/Month",
    limits=(0.0, 0.1, 0.0001),
    comp_type="Constant",
    comp_subtype="Normal",
)
def birth_rate():
    return 0.027 / 12


@component.add(
    name="births",
    units="People/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"birth_rate": 1, "total_pop": 1},
)
def births():
    return birth_rate() * total_pop()


@component.add(
    name="deaths A",
    units="People/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"active": 1, "general_mortality": 1},
)
def deaths_a():
    return active() * general_mortality()


@component.add(
    name="deaths L",
    units="People/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"latent_tb_infection": 1, "general_mortality": 1},
)
def deaths_l():
    return latent_tb_infection() * general_mortality()


@component.add(
    name="deaths S",
    units="People/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"susceptible": 1, "general_mortality": 1},
)
def deaths_s():
    return susceptible() * general_mortality()


@component.add(
    name="deaths T",
    units="People/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"detected_and_treated_tb": 1, "general_mortality": 1},
)
def deaths_t():
    return detected_and_treated_tb() * general_mortality()


@component.add(
    name="Susceptible",
    units="People",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_susceptible": 1},
    other_deps={
        "_integ_susceptible": {
            "initial": {"initial_incident": 1, "initial_latent": 1},
            "step": {"births": 1, "deaths_s": 1, "infection": 1},
        }
    },
)
def susceptible():
    return _integ_susceptible()


_integ_susceptible = Integ(
    lambda: births() - deaths_s() - infection(),
    lambda: 38000000.0 - initial_incident() - initial_latent(),
    "_integ_susceptible",
)


@component.add(
    name="total pop",
    units="People",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "active": 1,
        "detected_and_treated_tb": 1,
        "latent_tb_infection": 1,
        "susceptible": 1,
    },
)
def total_pop():
    return active() + detected_and_treated_tb() + latent_tb_infection() + susceptible()


@component.add(
    name="general mortality",
    units="1/Month",
    limits=(0.0, 1.0, 0.0001),
    comp_type="Constant",
    comp_subtype="Normal",
)
def general_mortality():
    return 0.0075 / 12


@component.add(
    name="infection",
    units="People/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"force_of_infection": 1, "susceptible": 1, "total_pop": 1, "active": 1},
)
def infection():
    return force_of_infection() * susceptible() * (active() / total_pop())


@component.add(
    name="initial incident",
    units="People",
    limits=(0.0, 2000000.0, 50000.0),
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_incident():
    return 3000000.0


@component.add(
    name="initial latent",
    units="People",
    limits=(0.0, 2000000.0),
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_latent():
    return 497.3


@component.add(
    name="Latent TB infection",
    units="People",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_latent_tb_infection": 1},
    other_deps={
        "_integ_latent_tb_infection": {
            "initial": {"initial_latent": 1},
            "step": {"infection": 1, "deaths_l": 1, "progression": 1},
        }
    },
)
def latent_tb_infection():
    return _integ_latent_tb_infection()


_integ_latent_tb_infection = Integ(
    lambda: infection() - deaths_l() - progression(),
    lambda: initial_latent(),
    "_integ_latent_tb_infection",
)


@component.add(
    name="diagnosis delay",
    units="Month",
    limits=(0.0, 20.0),
    comp_type="Constant",
    comp_subtype="Normal",
)
def diagnosis_delay():
    return 6


@component.add(
    name="Detected and Treated TB",
    units="People",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_detected_and_treated_tb": 1},
    other_deps={
        "_integ_detected_and_treated_tb": {
            "initial": {},
            "step": {"detection": 1, "deaths_t": 1, "relapse": 1},
        }
    },
)
def detected_and_treated_tb():
    return _integ_detected_and_treated_tb()


_integ_detected_and_treated_tb = Integ(
    lambda: detection() - deaths_t() - relapse(),
    lambda: 55000,
    "_integ_detected_and_treated_tb",
)


@component.add(
    name="relapse rate",
    units="1/Month",
    limits=(0.0, 0.1),
    comp_type="Constant",
    comp_subtype="Normal",
)
def relapse_rate():
    return 0.0079857


@component.add(
    name="force of infection",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def force_of_infection():
    return 0.072


@component.add(
    name="progression rate",
    units="1/Month",
    limits=(0.0, 0.2, 0.001),
    comp_type="Constant",
    comp_subtype="Normal",
)
def progression_rate():
    return 0.04973
