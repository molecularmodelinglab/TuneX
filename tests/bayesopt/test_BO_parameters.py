from app.bayesopt.parameters import ParameterConverter
from app.models.campaign import Campaign
from app.models.parameters.types import (
    Categorical,
    ContinuousNumerical,
    DiscreteNumericalIrregular,
    DiscreteNumericalRegular,
    Fixed,
    Substance,
)


def build_full_parameter_campaign():
    campaign = Campaign(name="Test Parameters")

    cont = ContinuousNumerical.create_default("Temp")
    cont.load_constraints({"min": 10.0, "max": 90.0})
    campaign.parameters.append(cont)

    disc_reg = DiscreteNumericalRegular.create_default("Pressure")
    disc_reg.load_constraints({"min": 1.0, "max": 5.0, "step": 1.0})
    campaign.parameters.append(disc_reg)

    disc_irreg = DiscreteNumericalIrregular.create_default("pH")
    disc_irreg.load_constraints({"values": [6.5, 7.0, 7.5]})
    campaign.parameters.append(disc_irreg)

    cat = Categorical.create_default("Catalyst")
    cat.load_constraints({"values": ["Pt", "Pd"]})
    campaign.parameters.append(cat)

    sub = Substance.create_default("Solvent")
    sub.load_constraints({"values": ["CCO", "CC"]})
    campaign.parameters.append(sub)

    fixed = Fixed.create_default("Reactor")
    fixed.load_constraints({"value": "Batch"})
    campaign.parameters.append(fixed)

    return campaign


def test_parameter_conversion_and_search_space():
    campaign = build_full_parameter_campaign()

    # Validate each parameter constraints first
    for p in campaign.parameters:
        assert ParameterConverter.validate_parameter_constraints(p)

    search_space = ParameterConverter.create_search_space(campaign.parameters)

    # Fixed parameter should be excluded
    names = [p.name for p in search_space.parameters]
    assert "Reactor" not in names
    assert {"Temp", "Pressure", "pH", "Catalyst", "Solvent"}.issubset(set(names))


def test_discrete_regular_generation_values():
    disc_reg = DiscreteNumericalRegular.create_default("Pressure")
    disc_reg.load_constraints({"min": 1.0, "max": 3.0, "step": 0.5})
    param = ParameterConverter.convert_parameter(disc_reg)
    # Should include both ends
    assert param.values[0] == 1.0
    assert param.values[-1] == 3.0


def test_invalid_continuous_missing_bounds():
    cont = ContinuousNumerical.create_default("Temp")
    cont.load_constraints({"min": None, "max": None})
    assert not ParameterConverter.validate_parameter_constraints(cont)


def test_substance_parameter_conversion():
    sub = Substance.create_default("Solvent")
    sub.load_constraints({"values": ["CCO", "CC"]})
    param = ParameterConverter.convert_parameter(sub)
    # Ensure data dict built
    assert all(k.startswith("mol_") for k in param.data.keys())
    assert set(param.data.values()) == {"CCO", "CC"}
