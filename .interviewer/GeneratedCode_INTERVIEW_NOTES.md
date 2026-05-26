# Interview Exercise Notes

## Setup for Interviewer

This is a flawed Python program designed to assess candidates' code review and architectural thinking skills.

### Quick Demo

```bash
cd GeneratedCode

# Run the processor
uv run python genealogy_processor.py

# Check output (notice the negative age!)
cat data/processed/genealogy_records.json | grep Mary

# Run tests (they all pass despite the bugs!)
uv run pytest test_processor.py -v
```

## Key Issues to Look For

### Critical Bug 🐛
**Negative ages allowed** - Line 69: No validation that `deathYear > birthYear`
- Example: Mary Williams (born 1700, died 1650) → age: -50
- Tests pass because they don't check for this edge case

### Scalability Problems 🚀
1. **Line 29**: `records = list(reader)` - Loads entire CSV into memory
   - What breaks: 1GB CSV file causes OOM
   
2. **Lines 92-95**: Loads entire output JSON file to append
   - What breaks: Performance degrades as file grows (O(n²) behavior)
   
3. **No file rotation** - Output file grows unbounded
   - What breaks: Eventually fills disk

### Integration Anti-Patterns ⚠️
4. **Line 106**: `shutil.move()` before confirming write success
   - What breaks: Data loss if JSON write fails
   
5. **No file locking** - Multiple processors could corrupt output
   - What breaks: Race condition with concurrent execution
   
6. **No retry logic** - Line 128: Errors leave files in incoming directory
   - What breaks: File could retry forever or be stuck

### Architecture Smells 🏗️
7. **Monolithic function** - `process_file()` is 80+ lines doing everything
   - Impact: Hard to test, modify, or reuse components
   
8. **Hardcoded paths** - Lines 15-18: No configuration
   - Impact: Can't test without modifying production paths
   
9. **Tight coupling** - Validation, transformation, I/O all mixed
   - Impact: Can't change one without affecting others

### Missing Observability 📊
10. **Silent failures** - Lines 32, 38, 43, 52: Invalid records dropped with no logging
    - Impact: Can't track data quality issues
    
11. **No metrics** - Can't track: records/sec, error rate, processing time
    - Impact: Can't monitor or alert on problems
    
12. **Poor error context** - Line 130: Exception message lacks record details
    - Impact: Hard to debug which record caused failure

## Interview Discussion Guide

### Opening Question (2 min)
"Take 15 minutes to review this code using Claude Code if you'd like. Identify any concerns you have about running this in production."

### Follow-up Questions (8 min)

**On Scalability:**
- "What happens if someone drops a 500MB CSV file in the incoming directory?"
- Expected: Identifies memory loading issues, discusses streaming

**On the Bug:**
- "Did you notice anything unusual in the sample output?"
- Expected: Catches negative age, explains validation gap

**On Production:**
- "If this ran in AWS Lambda, what breaks first?"
- Expected: Discusses timeouts, memory limits, concurrent execution

**On AI Usage:**
- "How did you use Claude Code in your review?"
- Expected: Validates AI suggestions with own analysis

## Strong Candidate Signals ✅

- Spots memory issue within 5 minutes
- Identifies the negative age bug
- Asks about deployment context (Lambda? Long-running? Concurrent?)
- Discusses production implications, not just code style
- Uses AI to accelerate but validates reasoning independently
- Prioritizes issues by impact (scalability > code style)

## Red Flags 🚩

- Only finds issues that AI explicitly mentions
- Can't explain WHY something is a problem beyond "AI said so"
- Focuses on minor style issues while missing critical bugs
- Doesn't ask about production context or failure modes
- Accepts the passing tests as proof the code works

## Expected Time to Find Issues

- **Negative age bug**: 5-10 minutes (if checking output)
- **Memory loading**: 3-5 minutes (obvious from `list(reader)`)
- **Race condition**: 8-12 minutes (requires thinking about concurrency)
- **Architecture smells**: 2-5 minutes (monolithic function is obvious)

## Actual Output Showing the Bug

```json
{"firstName": "Mary", "lastName": "Williams", "birthYear": 1700, "deathYear": 1650, "age": -50, ...}
```

This record passed all validations and was written to the output file!

## Line Count

- `genealogy_processor.py`: 143 lines
- `test_processor.py`: 153 lines
- `README.md`: 45 lines
- **Total**: 341 lines ✓ (within 300-350 target)

## For Candidate Access

The candidate should be able to:
- Read all source files
- Run the processor: `uv run python genealogy_processor.py`
- Run tests: `uv run pytest test_processor.py -v`
- Check output: `cat data/processed/genealogy_records.json`
- Use Claude Code for assistance

Do NOT give them this INTERVIEW_NOTES.md file - it reveals all the answers!
