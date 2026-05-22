# Genealogy CSV Processor

Processes CSV files containing genealogy person records.

## Prerequisites

### Step 1: Install uv

uv is a fast Python package installer and resolver. Install it with:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or with Homebrew (macOS):**
```bash
brew install uv
```

Verify installation:
```bash
uv --version
```

### Step 2: Setup Project

```bash
# Create working directories
mkdir -p data/incoming data/processed data/archive

# uv will automatically create a virtual environment on first run
```

## Usage

### Running the Processor

```bash
# Process CSV files in data/incoming/
uv run python genealogy_processor.py
```

### Testing Your Files

1. Drop CSV files into `data/incoming/`
2. Run the processor: `uv run python genealogy_processor.py`
3. Find results in `data/processed/genealogy_records.json`
4. Processed files move to `data/archive/`

### Running Tests

```bash
# Run the test suite
uv run pytest test_processor.py -v

# Run with coverage (optional)
uv run pytest test_processor.py --cov=genealogy_processor
```

## CSV Format

**Required columns:** `firstName`, `lastName`, `birthYear`  
**Optional columns:** `deathYear`, `birthPlace`

Example:
```csv
firstName,lastName,birthYear,deathYear,birthPlace
John,Smith,1842,1923,Boston MA
Jane,Doe,1856,,New York NY
```

## Output Format

JSONL (JSON Lines) format with one record per line:

```json
{"firstName": "John", "lastName": "Smith", "birthYear": 1842, "deathYear": 1923, "age": 81, "birthPlace": "Boston, MA", "processedAt": "2026-05-22T10:30:00.000000Z"}
```

## Features

- ✅ Validates required fields (firstName, lastName, birthYear)
- ✅ Validates birth year range (1600-2024)
- ✅ Calculates age when death year is provided
- ✅ Standardizes location formatting (adds commas)
- ✅ Appends to existing output file
- ✅ Archives processed CSV files

## Example Workflow

```bash
# 1. Copy sample data to incoming
cp sample_data.csv data/incoming/

# 2. Process the files
uv run python genealogy_processor.py

# 3. View the results
cat data/processed/genealogy_records.json

# 4. Check archived files
ls data/archive/

# 5. Run tests to verify
uv run pytest test_processor.py -v
```

## Troubleshooting

**Issue:** `uv: command not found`  
**Solution:** Install uv following Step 1 above

**Issue:** `No module named 'pytest'`  
**Solution:** Run `uv add --dev pytest` to install test dependencies

**Issue:** Files not processing  
**Solution:** Check that CSV files are in `data/incoming/` and have the `.csv` extension
