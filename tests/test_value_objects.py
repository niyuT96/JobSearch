from conftest import require_attr


def test_location_normalization():
    """Method under test: domain.value_objects.Location"""
    Location = require_attr("domain.value_objects", "Location")
    loc = Location("  Berlin, DE ")
    assert str(loc)


def test_skillset_dedup():
    """Method under test: domain.value_objects.SkillSet"""
    SkillSet = require_attr("domain.value_objects", "SkillSet")
    skills = SkillSet(["Python", "python", "SQL"])
    assert len(skills) >= 2

