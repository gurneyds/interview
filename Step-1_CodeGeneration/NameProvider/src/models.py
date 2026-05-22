"""
Person data model for genealogy records.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Person(BaseModel):
    """
    Represents a genealogy person record with required and optional fields.

    Required fields:
    - firstName: Person's first name
    - lastName: Person's last name
    - recordId: Unique identifier for the record
    - generatedAt: Timestamp when record was generated

    Optional fields (each has 50% probability of being present):
    - birthDate: Date of birth in ISO 8601 format (YYYY-MM-DD)
    - deathDate: Date of death in ISO 8601 format (YYYY-MM-DD)
    - birthPlace: Place of birth (City, State/Country)
    - deathPlace: Place of death (City, State/Country)
    - gender: Gender (M=Male, F=Female, U=Unknown)
    """
    firstName: str
    lastName: str
    birthDate: Optional[str] = None
    deathDate: Optional[str] = None
    birthPlace: Optional[str] = None
    deathPlace: Optional[str] = None
    gender: Optional[str] = None
    recordId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    generatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "firstName": "John",
                "lastName": "Smith",
                "birthDate": "1842-03-15",
                "deathDate": "1923-11-02",
                "birthPlace": "Boston, MA",
                "deathPlace": "Seattle, WA",
                "gender": "M",
                "recordId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "generatedAt": "2026-05-20T10:30:00.000000Z"
            }]
        }
    }
