#!/usr/bin/env python3
"""
Genealogy CSV Processor
Processes incoming CSV files with person records, validates and transforms them.
"""

import csv
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

INCOMING_DIR = "data/incoming"
PROCESSED_DIR = "data/processed"
ARCHIVE_DIR = "data/archive"
OUTPUT_FILE = "data/processed/genealogy_records.json"


def process_file(csv_path):
    """
    Process a single CSV file (Issue #9: Monolithic 100+ line function)

    Issues:
    - Everything in one function: validation, transformation, I/O
    - No error propagation, silent failures
    - Loads entire file into memory
    """
    print(f"Processing {csv_path}")

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        records = list(reader)

    processed_records = []

    for record in records:
        if not record.get('firstName') or not record.get('lastName'):
            continue

        try:
            birth_year = int(record['birthYear'])

            if birth_year < 1600 or birth_year > 2024:
                continue 

        except (ValueError, KeyError):
            continue

        # Process death year
        death_year = None
        age = None
        if record.get('deathYear') and record.get('deathYear').strip():
            try:
                death_year = int(record['deathYear'])
                age = death_year - birth_year

            except ValueError:
                pass

        birth_place = record.get('birthPlace', '')
        if birth_place:
            # Simple transformation: add comma if missing
            if ',' not in birth_place:
                parts = birth_place.split()
                if len(parts) >= 2:
                    birth_place = f"{parts[0]}, {' '.join(parts[1:])}"

        processed_record = {
            'firstName': record['firstName'],
            'lastName': record['lastName'],
            'birthYear': birth_year,
            'deathYear': death_year,
            'age': age,
            'birthPlace': birth_place,
            'processedAt': datetime.utcnow().isoformat() + 'Z'
        }

        processed_records.append(processed_record)

    existing_records = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            # Loads entire file into memory
            for line in f:
                existing_records.append(json.loads(line))

    all_records = existing_records + processed_records

    with open(OUTPUT_FILE, 'w') as f:
        for rec in all_records:
            f.write(json.dumps(rec) + '\n')

    archive_path = os.path.join(ARCHIVE_DIR, os.path.basename(csv_path))
    shutil.move(csv_path, archive_path)

    print(f"Completed {csv_path}: {len(processed_records)} records")  # Issue #16: No metrics


def scan_and_process():
    """
    Scan incoming directory and process files

    Issues:
    - No concurrency (Issue #3)
    - No file locking (Issue #6)
    - No retry on errors (Issue #5)
    """
    # Ensure directories exist
    os.makedirs(INCOMING_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    for filename in os.listdir(INCOMING_DIR):
        if filename.endswith('.csv'):
            csv_path = os.path.join(INCOMING_DIR, filename)

            try:
                process_file(csv_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

def main():
    """Main entry point"""
    print("Starting genealogy processor")
    scan_and_process()
    print("Processing complete")


if __name__ == "__main__":
    main()
