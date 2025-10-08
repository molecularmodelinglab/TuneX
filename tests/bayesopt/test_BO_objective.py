import pytest

from app.bayesopt.objective import ObjectiveConverter
from app.models.campaign import Target


def test_single_target_objective_creation():
    t = Target(name="Yield", mode="Max", weight=2.0, min_value=0.0, max_value=100.0)
    obj = ObjectiveConverter.create_objective([t])
    # Depending on baybe version attribute may be _target
    single_target = getattr(obj, "target", getattr(obj, "_target", None))
    assert single_target is not None
    assert single_target.name == "Yield"


def test_multi_target_desirability_objective_creation():
    t1 = Target(name="Yield", mode="Max", weight=3.0, min_value=0.0, max_value=100.0)
    t2 = Target(name="Cost", mode="Min", weight=1.0, min_value=0.0, max_value=1000.0)
    obj = ObjectiveConverter.create_objective([t1, t2])
    # DesirabilityObjective may store targets in targets or _targets
    targets = getattr(obj, "targets", getattr(obj, "_targets", None))
    assert targets is not None
    assert len(targets) == 2


def test_target_validation_duplicate_names():
    t1 = Target(name="Yield", mode="Max", weight=1.0, min_value=0.0, max_value=100.0)
    t2 = Target(name="Yield", mode="Min", weight=1.0, min_value=0.0, max_value=100.0)
    errors = ObjectiveConverter.validate_targets([t1, t2])
    assert any("Duplicate" in e for e in errors)


def test_desirability_weights_normalization():
    t1 = Target(name="A", mode="Max", weight=3.0, min_value=0, max_value=10)
    t2 = Target(name="B", mode="Min", weight=1.0, min_value=0, max_value=10)
    weights = ObjectiveConverter.calculate_desirability_weights([t1, t2])
    assert pytest.approx(weights["A"] + weights["B"], rel=1e-6) == 1.0
    assert weights["A"] > weights["B"]


def test_explain_desirability_function_contains_targets():
    t1 = Target(name="Yield", mode="Max", weight=2.0, min_value=0.0, max_value=100.0)
    t2 = Target(name="Cost", mode="Min", weight=1.0, min_value=0.0, max_value=1000.0)
    explanation = ObjectiveConverter.explain_desirability_function([t1, t2])
    assert "Yield" in explanation and "Cost" in explanation
