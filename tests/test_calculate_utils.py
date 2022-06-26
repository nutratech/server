import pytest

import ntserv.utils.calculate as calc


# ------------------------------------------------
# 1 rep max
# ------------------------------------------------
def _check_orm_results(maxes, expected_results):
    for n_reps, expected_max in expected_results:
        assert maxes[n_reps] == expected_max


@pytest.mark.parametrize(
    "reps,weight,expected_results",
    [
        (3, 315, [(1, 336.0)]),
        (8, 275, [(1, 339.2)]),
        (10, 225, [(1, 292.5)]),
        (12, 225, [(1, 307.5)]),
        (15, 225, [(1, 330.0)]),
        (20, 225, [(1, 367.5)]),
    ],
)
def test_orm_epley(reps, weight, expected_results):
    maxes = calc.orm_epley(reps, weight)
    _check_orm_results(maxes, expected_results)


@pytest.mark.parametrize(
    "reps,weight,expected_results",
    [
        (3, 315, [(1, 333.5)]),
        (8, 275, [(1, 341.4)]),
        (10, 225, [(1, 300.0)]),
        (12, 225, [(1, 324.0)]),
        # NOTE: Brzycki loses accuracy > 12 reps (tends to overestimate)
        (15, 225, [(1, 368.2)]),
        (20, 225, [(1, 476.5)]),
    ],
)
def test_orm_brzycki(reps, weight, expected_results):
    maxes = calc.orm_brzycki(reps, weight)
    _check_orm_results(maxes, expected_results)


# ------------------------------------------------
# BMR
# ------------------------------------------------
def test_bmr_katch_mcardle():
    pass


def test_bmr_cunningham():
    pass


@pytest.mark.parametrize(
    "gender,weight,height,dob,activity_factor,expected_result",
    [
        ("MALE", 77, 177, 725864400, 0.55, {"bmr": 1740, "tdee": 2697}),
        ("FEMALE", 77, 177, 725864400, 0.55, {"bmr": 1574, "tdee": 2440}),
    ],
)
def test_bmr_mifflin_st_jeor(
    gender, weight, height, dob, activity_factor, expected_result
):
    result = calc.bmr_mifflin_st_jeor(gender, weight, height, dob, activity_factor)
    assert result == expected_result


@pytest.mark.parametrize(
    "gender,weight,height,dob,activity_factor,expected_result",
    [
        ("MALE", 77, 177, 725864400, 0.55, {"bmr": 1802, "tdee": 2793}),
        ("FEMALE", 77, 177, 725864400, 0.55, {"bmr": 1580, "tdee": 2449}),
    ],
)
def test_bmr_harris_benedict(
    gender, weight, height, dob, activity_factor, expected_result
):
    result = calc.bmr_harris_benedict(gender, weight, height, dob, activity_factor)
    assert result == expected_result