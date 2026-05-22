"""
Mock person data generator using Faker library.
"""
from faker import Faker
from datetime import datetime, timedelta
import random
from .models import Person


class PersonGenerator:
    """
    Generates realistic mock genealogy person records.

    Each optional field (birthDate, deathDate, birthPlace, deathPlace, gender)
    has an independent 50% probability of being included.
    """

    def __init__(self, seed: int = None):
        """
        Initialize the generator with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible generation (optional)
        """
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

    def generate_person(self) -> Person:
        """
        Generate a single Person record with required and optional fields.

        Returns:
            Person: A Person model instance with randomly generated data
        """
        # Required fields - always present
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()

        # Optional fields - each has 50% probability
        birth_date = self._generate_birth_date() if random.random() < 0.5 else None
        death_date = self._generate_death_date(birth_date) if (birth_date and random.random() < 0.5) else None
        birth_place = self._generate_place() if random.random() < 0.5 else None
        death_place = self._generate_place() if random.random() < 0.5 else None
        gender = self._generate_gender() if random.random() < 0.5 else None

        return Person(
            firstName=first_name,
            lastName=last_name,
            birthDate=birth_date,
            deathDate=death_date,
            birthPlace=birth_place,
            deathPlace=death_place,
            gender=gender
        )

    def _generate_birth_date(self) -> str:
        """
        Generate a birth date between 1800 and 1950 (genealogy research range).

        Returns:
            str: Date in ISO 8601 format (YYYY-MM-DD)
        """
        start_date = datetime(1800, 1, 1)
        end_date = datetime(1950, 12, 31)
        days_between = (end_date - start_date).days
        random_days = random.randint(0, days_between)
        birth_date = start_date + timedelta(days=random_days)
        return birth_date.strftime("%Y-%m-%d")

    def _generate_death_date(self, birth_date: str) -> str:
        """
        Generate a death date that is 20-90 years after birth date.

        Args:
            birth_date: Birth date in ISO 8601 format (YYYY-MM-DD)

        Returns:
            str: Death date in ISO 8601 format (YYYY-MM-DD)
        """
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        lifespan_years = random.randint(20, 90)
        lifespan_days = random.randint(0, 364)  # Add random days within the year
        death = birth + timedelta(days=lifespan_years * 365 + lifespan_days)
        return death.strftime("%Y-%m-%d")

    def _generate_place(self) -> str:
        """
        Generate a location in "City, State" or "City, Country" format.

        Returns:
            str: Place string in standard genealogy format
        """
        city = self.faker.city()
        # Mix of US states and international locations
        if random.random() < 0.7:  # 70% US locations
            state = self.faker.state_abbr()
            return f"{city}, {state}"
        else:  # 30% international
            country = self.faker.country()
            return f"{city}, {country}"

    def _generate_gender(self) -> str:
        """
        Generate gender with distribution: 48% M, 48% F, 4% U (unknown).

        Returns:
            str: Gender code (M, F, or U)
        """
        return random.choices(["M", "F", "U"], weights=[48, 48, 4])[0]
