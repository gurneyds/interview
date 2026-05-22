"""
Tests for PersonGenerator.
"""
import pytest
from datetime import datetime
from src.generator import PersonGenerator


def test_generator_creates_valid_person():
    """Test that generator creates a valid Person instance."""
    generator = PersonGenerator(seed=42)
    person = generator.generate_person()

    # Required fields should always be present
    assert person.firstName is not None
    assert person.lastName is not None
    assert person.recordId is not None
    assert person.generatedAt is not None


def test_generator_optional_field_probability():
    """Test that optional fields appear approximately 50% of the time."""
    generator = PersonGenerator(seed=42)
    sample_size = 100

    # Generate many persons and count optional field occurrences
    counts = {
        'birthDate': 0,
        'deathDate': 0,
        'birthPlace': 0,
        'deathPlace': 0,
        'gender': 0
    }

    for _ in range(sample_size):
        person = generator.generate_person()
        if person.birthDate:
            counts['birthDate'] += 1
        if person.deathDate:
            counts['deathDate'] += 1
        if person.birthPlace:
            counts['birthPlace'] += 1
        if person.deathPlace:
            counts['deathPlace'] += 1
        if person.gender:
            counts['gender'] += 1

    # Each field should appear roughly 50% of the time (allow 30-70% range)
    for field, count in counts.items():
        percentage = count / sample_size
        assert 0.3 <= percentage <= 0.7, f"{field} appeared {percentage*100}% of the time"


def test_generator_birth_date_range():
    """Test that birth dates are in the expected range (1800-1950)."""
    generator = PersonGenerator(seed=42)

    for _ in range(20):
        person = generator.generate_person()
        if person.birthDate:
            birth_year = int(person.birthDate.split('-')[0])
            assert 1800 <= birth_year <= 1950


def test_generator_death_date_after_birth():
    """Test that death date is always after birth date."""
    generator = PersonGenerator(seed=42)

    for _ in range(50):
        person = generator.generate_person()
        if person.birthDate and person.deathDate:
            birth = datetime.strptime(person.birthDate, "%Y-%m-%d")
            death = datetime.strptime(person.deathDate, "%Y-%m-%d")
            assert death > birth, "Death date must be after birth date"


def test_generator_place_format():
    """Test that places are in correct format."""
    generator = PersonGenerator(seed=42)

    for _ in range(20):
        person = generator.generate_person()
        if person.birthPlace:
            assert ',' in person.birthPlace, "Place should contain comma separator"
        if person.deathPlace:
            assert ',' in person.deathPlace, "Place should contain comma separator"


def test_generator_gender_values():
    """Test that gender is one of the expected values."""
    generator = PersonGenerator(seed=42)

    for _ in range(50):
        person = generator.generate_person()
        if person.gender:
            assert person.gender in ['M', 'F', 'U'], f"Invalid gender: {person.gender}"
