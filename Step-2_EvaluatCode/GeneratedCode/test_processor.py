#!/usr/bin/env python3
"""
Tests for genealogy_processor.py

These tests pass but miss many edge cases and production issues.
"""

import pytest
import tempfile
import os
import csv
import json
import shutil
from pathlib import Path
import genealogy_processor


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing"""
    temp_dir = tempfile.mkdtemp()
    incoming = os.path.join(temp_dir, "incoming")
    processed = os.path.join(temp_dir, "processed")
    archive = os.path.join(temp_dir, "archive")

    os.makedirs(incoming)
    os.makedirs(processed)
    os.makedirs(archive)

    # Patch the module constants
    original_incoming = genealogy_processor.INCOMING_DIR
    original_processed = genealogy_processor.PROCESSED_DIR
    original_archive = genealogy_processor.ARCHIVE_DIR
    original_output = genealogy_processor.OUTPUT_FILE

    genealogy_processor.INCOMING_DIR = incoming
    genealogy_processor.PROCESSED_DIR = processed
    genealogy_processor.ARCHIVE_DIR = archive
    genealogy_processor.OUTPUT_FILE = os.path.join(processed, "genealogy_records.json")

    yield {
        'incoming': incoming,
        'processed': processed,
        'archive': archive,
        'temp_dir': temp_dir
    }

    # Restore original values
    genealogy_processor.INCOMING_DIR = original_incoming
    genealogy_processor.PROCESSED_DIR = original_processed
    genealogy_processor.ARCHIVE_DIR = original_archive
    genealogy_processor.OUTPUT_FILE = original_output

    # Cleanup
    shutil.rmtree(temp_dir)


def test_valid_csv_processing(temp_dirs):
    """Test basic CSV processing with valid data - PASSES"""
    csv_file = os.path.join(temp_dirs['incoming'], 'test.csv')

    # Create test CSV
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['firstName', 'lastName', 'birthYear', 'deathYear', 'birthPlace'])
        writer.writeheader()
        writer.writerow({
            'firstName': 'John',
            'lastName': 'Smith',
            'birthYear': '1842',
            'deathYear': '1923',
            'birthPlace': 'Boston MA'
        })

    # Process
    genealogy_processor.scan_and_process()

    # Check output exists
    output_file = genealogy_processor.OUTPUT_FILE
    assert os.path.exists(output_file)

    # Read and validate
    with open(output_file, 'r') as f:
        records = [json.loads(line) for line in f]

    assert len(records) == 1
    assert records[0]['firstName'] == 'John'
    assert records[0]['lastName'] == 'Smith'
    assert records[0]['birthYear'] == 1842
    assert records[0]['age'] == 81

    # Check file was archived
    assert not os.path.exists(csv_file)
    assert os.path.exists(os.path.join(temp_dirs['archive'], 'test.csv'))


def test_missing_required_fields(temp_dirs):
    """Test that records without firstName/lastName are skipped - PASSES"""
    csv_file = os.path.join(temp_dirs['incoming'], 'incomplete.csv')

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['firstName', 'lastName', 'birthYear'])
        writer.writeheader()
        writer.writerow({'firstName': '', 'lastName': 'Smith', 'birthYear': '1842'})
        writer.writerow({'firstName': 'Jane', 'lastName': '', 'birthYear': '1856'})
        writer.writerow({'firstName': 'Valid', 'lastName': 'Person', 'birthYear': '1900'})

    genealogy_processor.scan_and_process()

    output_file = genealogy_processor.OUTPUT_FILE
    with open(output_file, 'r') as f:
        records = [json.loads(line) for line in f]

    # Only the valid record should be processed
    assert len(records) == 1
    assert records[0]['firstName'] == 'Valid'


def test_invalid_birth_year(temp_dirs):
    """Test that invalid birth years are skipped - PASSES"""
    csv_file = os.path.join(temp_dirs['incoming'], 'invalid_years.csv')

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['firstName', 'lastName', 'birthYear'])
        writer.writeheader()
        writer.writerow({'firstName': 'Too', 'lastName': 'Old', 'birthYear': '1500'})
        writer.writerow({'firstName': 'Too', 'lastName': 'Young', 'birthYear': '2025'})
        writer.writerow({'firstName': 'Invalid', 'lastName': 'Text', 'birthYear': 'abc'})
        writer.writerow({'firstName': 'Valid', 'lastName': 'Year', 'birthYear': '1800'})

    genealogy_processor.scan_and_process()

    output_file = genealogy_processor.OUTPUT_FILE
    with open(output_file, 'r') as f:
        records = [json.loads(line) for line in f]

    # Only the valid year should be processed
    assert len(records) == 1
    assert records[0]['birthYear'] == 1800


def test_place_transformation(temp_dirs):
    """Test that place names are transformed correctly - PASSES"""
    csv_file = os.path.join(temp_dirs['incoming'], 'places.csv')

    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['firstName', 'lastName', 'birthYear', 'birthPlace'])
        writer.writeheader()
        writer.writerow({'firstName': 'Test', 'lastName': 'Person', 'birthYear': '1900', 'birthPlace': 'Boston MA'})

    genealogy_processor.scan_and_process()

    output_file = genealogy_processor.OUTPUT_FILE
    with open(output_file, 'r') as f:
        records = [json.loads(line) for line in f]

    assert records[0]['birthPlace'] == 'Boston, MA'
