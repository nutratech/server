#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 20:53:14 2020

@author: shane
"""
import math
import traceback
from datetime import datetime

from ntserv.utils.logger import get_logger

# TODO: generalize activity level across BMR calcs, e.g. LIGHT, MODERATE, EXTREME

_logger = get_logger(__name__)

# ------------------------------------------------
# 1 rep max
# ------------------------------------------------

common_n_reps = (1, 2, 3, 5, 6, 8, 10, 12, 15, 20)


def orm_epley(reps: float, weight: float) -> dict:
    """
    Returns a dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 6, 8, 10, 12, 15, 20)

    1 RM = weight * (1 + (reps - 1) / 30)

    Source: https://workoutable.com/one-rep-max-calculator/
    """

    def one_rm() -> float:
        _un_rounded_result = weight * (1 + (reps - 1) / 30)
        return round(_un_rounded_result, 1)

    def weight_max_reps(target_reps: float) -> float:
        _un_rounded_result = one_rm() / (1 + (target_reps - 1) / 30)
        return round(_un_rounded_result, 1)

    maxes = {n_reps: weight_max_reps(n_reps) for n_reps in common_n_reps}
    return maxes


def orm_brzycki(reps: float, weight: float) -> dict:
    """
    Returns a dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 6, 8, 10, 12, 15)

    1 RM = weight * 36 / (37 - reps)

    Source: https://workoutable.com/one-rep-max-calculator/
    """

    def _one_rm() -> float:
        _un_rounded_result = weight * 36 / (37 - reps)
        return round(_un_rounded_result, 1)

    one_rm = _one_rm()

    def weight_max_reps(target_reps: float) -> float:
        _un_rounded_result = one_rm / (1 + (target_reps - 1) / 30)
        return round(_un_rounded_result, 1)

    maxes = {n_reps: weight_max_reps(n_reps) for n_reps in common_n_reps}
    return maxes


def orm_dos_remedios(reps: int, weight: float) -> dict:
    """
    Returns dict {n_reps: max_weight, ...}
        for n_reps: (1, 2, 3, 5, 6, 8, 10, 12, 15)

    Or an {"error": "INVALID_RANGE", ...}

    Source:
        https://www.peterrobertscoaching.com/blog/the-best-way-to-calculate-1-rep-max
    """

    _common_n_reps = {
        1: 1,
        2: 0.92,
        3: 0.9,
        5: 0.87,
        6: 0.82,
        8: 0.75,
        10: 0.7,
        12: 0.65,
        15: 0.6,
    }

    def _one_rm() -> float:
        _multiplier = _common_n_reps[reps]
        _un_rounded_result = weight / _multiplier
        return round(_un_rounded_result, 1)

    try:
        one_rm = _one_rm()
    except KeyError:
        _logger.debug(traceback.format_exc())
        valid_reps = list(_common_n_reps.keys())
        return {
            "error": "INVALID_RANGE",
            "requires": ["reps", "in", valid_reps, "got", reps],
        }

    def max_weight(target_reps: int) -> float:
        _multiplier = _common_n_reps[target_reps]
        _un_rounded_result = one_rm * _multiplier
        return round(_un_rounded_result, 1)

    return {n_reps: max_weight(n_reps) for n_reps in _common_n_reps}


# ------------------------------------------------
# BMR
# ------------------------------------------------
def bmr_katch_mcardle(lbm: float, activity_factor: float):
    """
    @param lbm: lean mass in kg
    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}

    BMR = 370 + (21.6 x Lean Body Mass(kg) )

    Source: https://www.calculatorpro.com/calculator/katch-mcardle-bmr-calculator/
    Source: https://tdeecalculator.net/about.php
    """

    bmr = 370 + (21.6 * lbm)
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


def bmr_cunningham(lbm: float, activity_factor: float):
    """
    @param lbm: lean mass in kg
    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}

    Source: https://www.slideshare.net/lsandon/weight-management-in-athletes-lecture
    """

    bmr = 500 + 22 * lbm
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


def bmr_mifflin_st_jeor(
    gender: str, weight: float, height: float, dob: int, activity_factor: float
) -> dict:
    """
    @param gender: {'MALE', 'FEMALE'}
    @param weight: kg
    @param height: cm
    @param dob: int, unix timestamp (seconds)
    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}

    Activity Factor\n
    ---------------\n
    0.200 = sedentary (little or no exercise)

    0.375 = lightly active
        (light exercise/sports 1-3 days/week, approx. 590 Cal/day)

    0.550 = moderately active
        (moderate exercise/sports 3-5 days/week, approx. 870 Cal/day)

    0.725 = very active
        (hard exercise/sports 6-7 days a week, approx. 1150 Cal/day)

    0.900 = extra active
        (very hard exercise/sports and physical job, approx. 1580 Cal/day)

    Source: https://www.myfeetinmotion.com/mifflin-st-jeor-equation/
    """

    def gender_specific_bmr(_gender: str, _bmr: float) -> float:
        _second_term = {
            "MALE": 5,
            "FEMALE": -161,
        }
        # Exc: KeyError
        return _bmr + _second_term[gender]

    bmr = 10 * weight + 6.25 + 6.25 * height - 5 * _age(dob)

    bmr = gender_specific_bmr(gender, bmr)
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


def bmr_harris_benedict(
    gender: str, weight: float, height: float, dob: int, activity_factor: float
) -> dict:
    """
    @param gender: {'MALE', 'FEMALE'}
    @param weight: kg
    @param height: cm
    @param dob: int, unix timestamp (seconds)
    @param activity_factor: {0.200, 0.375, 0.550, 0.725, 0.900}

    Harris-Benedict = (13.397m + 4.799h - 5.677a) + 88.362 (MEN)

    Harris-Benedict = (9.247m + 3.098h - 4.330a) + 447.593 (WOMEN)

    m is mass in kg, h is height in cm, a is age in years

    Source: https://tdeecalculator.net/about.php
    """

    def gender_specific_bmr(_gender: str) -> float:
        age = _age(dob)

        _gender_specific_bmr = {
            "MALE": (13.397 * weight + 4.799 * height - 5.677 * age) + 88.362,
            "FEMALE": (9.247 * weight + 3.098 * height - 4.330 * age) + 447.593,
        }
        # Exc: KeyError
        return _gender_specific_bmr[_gender]

    bmr = gender_specific_bmr(gender)
    tdee = bmr * (1 + activity_factor)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
    }


# ------------------------------------------------
# Body fat
# ------------------------------------------------
def bf_navy(
    gender: str, height: float, waist: float, neck: float, hip: float = 0
) -> float:
    """
    @param gender: {'MALE', 'FEMALE'}
    @param height: cm
    @param waist: cm
    @param neck: cm
    @param hip: (cm) Only required for "FEMALE" gender

    @return: float (e.g. 0.17)
    """

    _gender_specific_denominator = {
        "MALE": (
            1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)
        ),
        "FEMALE": (
            1.29579
            - 0.35004 * math.log10(waist + hip - neck)
            + 0.22100 * math.log10(height)
        ),
    }

    # Exc: KeyError
    return round(495 / _gender_specific_denominator[gender] - 450, 2)


def bf_3site(
    gender: str,
    age: float,
    chest: float,
    abd: float,
    thigh: float,
) -> float:
    """
    @param gender: {'MALE', 'FEMALE'}
    @param age: (years) float
    @param chest: (mm) Manifold
    @param abd: (mm) Manifold
    @param thigh: (mm) Manifold

    @return: float (e.g. 0.17)
    """

    st3 = chest + abd + thigh

    _gender_specific_denominator = {
        "MALE": 1.10938 - 0.0008267 * st3 + 0.0000016 * st3 * st3 - 0.0002574 * age,
        "FEMALE": 1.089733 - 0.0009245 * st3 + 0.0000025 * st3 * st3 - 0.0000979 * age,
    }

    # Exc: KeyError
    return round(495 / _gender_specific_denominator[gender] - 450, 2)


def bf_7site(
    gender: str,
    age: float,
    chest: float,
    abd: float,
    thigh: float,
    tricep: float,
    sub: float,
    sup: float,
    mid: float,
):
    """
    @param gender: {'MALE', 'FEMALE'}
    @param age: (years) float
    @param chest: (mm) Manifold
    @param abd: (mm) Manifold
    @param thigh: (mm) Manifold
    @param tricep: (mm) Manifold
    @param sub: (mm) Manifold
    @param sup: (mm) Manifold
    @param mid: (mm) Manifold

    @return: float (e.g. 0.17)
    """

    st7 = chest + abd + thigh + tricep + sub + sup + mid

    _gender_specific_denominator = {
        "MALE": 1.112 - 0.00043499 * st7 + 0.00000055 * st7 * st7 - 0.00028826 * age,
        "FEMALE": 1.097 - 0.00046971 * st7 + 0.00000056 * st7 * st7 - 0.00012828 * age,
    }

    # Exc: KeyError
    return round(495 / _gender_specific_denominator[gender] - 450, 2)


# ------------------------------------------------
# Misc functions
# ------------------------------------------------
def _age(dob: int) -> float:
    now = datetime.now().timestamp()
    years = (now - dob) / (365 * 24 * 3600)
    return years
