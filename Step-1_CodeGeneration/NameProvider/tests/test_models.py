"""
Tests for Person data model.
"""
import pytest
from src.models import Person


def test_person_required_fields():
    """Test that required fields are validated."""
    # Should succeed with required fields
    person = Person(firstName="John", lastName="Smith")
    assert person.firstName == "John"
    assert person.lastName == "Smith"
    assert person.recordId is not None  # Auto-generated
    assert person.generatedAt is not None  # Auto-generated


def test_person_optional_fields():
    """Test that optional fields work correctly."""
    person = Person(
        firstName="Jane",
        lastName="Doe",
        birthDate="1850-05-15",
        deathDate="1920-03-20",
        birthPlace="Boston, MA",
        deathPlace="Seattle, WA",
        gender="F"
    )

    assert person.birthDate == "1850-05-15"
    assert person.deathDate == "1920-03-20"
    assert person.birthPlace == "Boston, MA"
    assert person.deathPlace == "Seattle, WA"
    assert person.gender == "F"


def test_person_missing_required_field():
    """Test that missing required fields raise validation error."""
    with pytest.raises(Exception):  # Pydantic ValidationError
        Person(firstName="John")  # Missing lastName


def test_person_auto_generated_fields():
    """Test that recordId and generatedAt are auto-generated."""
    person1 = Person(firstName="John", lastName="Smith")
    person2 = Person(firstName="Jane", lastName="Doe")

    # Each person should have unique recordId
    assert person1.recordId != person2.recordId

    # Both should have generatedAt timestamps
    assert "T" in person1.generatedAt  # ISO 8601 format
    assert "Z" in person1.generatedAt  # UTC timezone
