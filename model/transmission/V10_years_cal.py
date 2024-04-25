"""
Python model 'V10_years_cal.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.functions import ramp
from pysd.py_backend.statefuls import Smooth, Delay, Integ
from pysd import Component

__pysd_version__ = "3.7.1"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 2000,
    "final_time": lambda: 2021,
    "time_step": lambda: 1,
    "saveper": lambda: time_step(),
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
    name="FINAL TIME", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Year",
    limits=(0.0, np.nan),
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP",
    units="Year",
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
    units="People/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"active": 1, "cdr": 1},
)
def detection():
    return active() * cdr()


@component.add(
    name="Cumulative Cases",
    units="People",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_cumulative_cases": 1},
    other_deps={"_integ_cumulative_cases": {"initial": {}, "step": {"progression": 1}}},
)
def cumulative_cases():
    return _integ_cumulative_cases()


_integ_cumulative_cases = Integ(
    lambda: progression(), lambda: 0, "_integ_cumulative_cases"
)


@component.add(
    name="progression",
    units="People/Year",
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
    units="People/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"detected_and_treated_tb": 1, "relapse_rate": 1},
)
def relapse():
    return detected_and_treated_tb() * relapse_rate()


@component.add(
    name="CDR",
    units="1/Year",
    comp_type="Stateful",
    comp_subtype="Smooth",
    depends_on={"_smooth_cdr": 1},
    other_deps={"_smooth_cdr": {"initial": {"time": 1}, "step": {"time": 1}}},
)
def cdr():
    return _smooth_cdr()


_smooth_cdr = Smooth(
    lambda: 0.46 + ramp(__data["time"], 0.022, 2016, 2021),
    lambda: 2,
    lambda: 0.46 + ramp(__data["time"], 0.022, 2016, 2021),
    lambda: 1,
    "_smooth_cdr",
)


@component.add(
    name="CFR",
    units="1/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def cfr():
    return 0.45 + ramp(__data["time"], -0.015, 2007, 2022)


@component.add(
    name="deaths TB",
    units="People/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"active": 1, "cfr": 1},
)
def deaths_tb():
    return active() * (cfr() / 12)


@component.add(
    name="progression time", units="Year", comp_type="Constant", comp_subtype="Normal"
)
def progression_time():
    return 3.9661


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
    units="1/Year",
    limits=(0.0, 0.1, 0.0001),
    comp_type="Constant",
    comp_subtype="Normal",
)
def birth_rate():
    return 0.028


@component.add(
    name="births",
    units="People/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"birth_rate": 1, "total_pop": 1},
)
def births():
    return birth_rate() * total_pop()


@component.add(
    name="deaths A",
    units="People/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"active": 1, "general_mortality": 1},
)
def deaths_a():
    return active() * general_mortality()


@component.add(
    name="deaths L",
    units="People/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"latent_tb_infection": 1, "general_mortality": 1},
)
def deaths_l():
    return latent_tb_infection() * general_mortality()


@component.add(
    name="deaths S",
    units="People/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"susceptible": 1, "general_mortality": 1},
)
def deaths_s():
    return susceptible() * general_mortality()


@component.add(
    name="deaths T",
    units="People/Year",
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
    units="1/Year",
    limits=(0.0, 1.0, 0.0001),
    comp_type="Constant",
    comp_subtype="Normal",
)
def general_mortality():
    return 0.008


@component.add(
    name="infection",
    units="People/Year",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"transmission_rate": 1, "susceptible": 1, "total_pop": 1, "active": 1},
)
def infection():
    return transmission_rate() * susceptible() * (active() / total_pop())


@component.add(
    name="initial incident",
    units="People",
    limits=(0.0, 2000000.0, 50000.0),
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_incident():
    return 1971000.0


@component.add(
    name="initial latent",
    units="People",
    limits=(0.0, 2000000.0),
    comp_type="Constant",
    comp_subtype="Normal",
)
def initial_latent():
    return 988380


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
    units="1/Year",
    limits=(0.0, 0.1),
    comp_type="Constant",
    comp_subtype="Normal",
)
def relapse_rate():
    return 0.004


@component.add(
    name="transmission rate",
    units="1/Year",
    comp_type="Constant",
    comp_subtype="Normal",
)
def transmission_rate():
    return 0.3683


@component.add(
    name="progression rate",
    units="1/Year",
    limits=(0.0, 0.2, 0.001),
    comp_type="Constant",
    comp_subtype="Normal",
)
def progression_rate():
    return 0.1559
