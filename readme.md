# Higher Education Database Skills Assessment

A comprehensive data pipeline demonstrating database design, SQL query optimization, geospatial analysis, and IPEDS data integration for the higher education sector.

## Project Overview

This project fulfills six core competencies:
1. **Data Cleaning & Feature Engineering** - Analyze Fall-to-Spring student attrition concentrations
2. **Data Integration** - Merge five IPEDS survey files into a unified academic success dataset
3. **Geospatial Analysis** - Demonstrate ZIP-based state inference with regex limitations discussion
4. **Relational Database Design** - Build SQLite database with constraint-based data validation
5. **SQL Query Optimization** - Execute LEFT JOIN identifying students with enrollment gaps
6. **Professional Reporting** - Generate Quarto HTML report with code, visualizations, and narrative

## Environment Setup

Create the Conda environment from the included `environment.yml`:

```bash
conda env create -f environment.yml
conda activate db_assessment_env
```

## Project Structure

```
.
├── data/                              # Raw data sources
│   ├── Part1/                         # Fall-to-Spring enrollment data
│   ├── Part2/IPEDS/                   # 5 IPEDS survey files (HD, OM, GR, GR200, EF)
│   ├── Part3/                         # Student addresses with ZIP codes
│   └── Part4/                         # Students, Enrollments, Degrees CSVs
├── scripts/                           # Production Python scripts
│   ├── part1_prep.py                  # Attrition analysis with discipline categorization
│   ├── part2_ipeds_prep.py            # 5-file IPEDS merge (32 output columns)
│   ├── part3_geo_audit.py             # ZIP-to-state mapping with majority-state rule
│   ├── part4_sqlite.py                # SQLite DB with DDL constraints & LEFT JOIN query
│   └── run_all.py                     # Orchestrator running all parts sequentially
├── outputs/                           # Clean, BI-ready datasets
│   ├── summary_table.csv              # Part 1: Cleaned master dataset (2,000 students)
│   ├── part1_retention_insight.png    # Part 1: Discipline-based attrition visualization
│   ├── IPEDS_Cleaned_For_Tableau.csv  # Part 2: Merged outcomes (48,419 records × 32 columns)
│   ├── part3_address_state_audit.csv  # Part 3: ZIP-to-state mapping audit
│   ├── institutional_records.db       # Part 4: SQLite with Students, Enrollments, Degrees tables
│   └── part4_attrition_results.csv    # Part 4: Attrition query results (20 students with gaps)
├── images/                            # Supporting images (PowerBI sample)
├── assessment_report.qmd              # Quarto source document
├── assessment_report.html             # Rendered report with embedded Tableau
├── environment.yml                    # Conda dependency specification
└── user_requirements.md               # Original 6-part requirements

```

## Running the Pipeline

Execute the full pipeline:

```bash
cd c:\Users\diony\projects\database_demo
conda activate db_assessment_env
python scripts/run_all.py
```

This will:
- ✅ Clean Part 1 enrollment data and generate discipline-based attrition chart
- ✅ Merge 5 IPEDS surveys into unified academic success dataset
- ✅ Audit student addresses using ZIP-to-state lookup
- ✅ Create SQLite database with relational constraints and execute attrition query
- ✅ Save all outputs to `outputs/` directory

## Key Technical Decisions

### Part 1: Academic Discipline Categorization
Students are mapped to academic disciplines using program title regex:
- **STEM/Health**: Science, technology, engineering, mathematics, health sciences
- **Business**: Management, accounting, economics, business administration
- **Social Sciences**: Psychology, sociology, political science, criminal justice
- **Non-Degree**: Certificates, diplomas, non-credit programs
- **Arts/Humanities**: Literature, history, philosophy, performing arts

Athletic cohort flagging adds another dimension to retention analysis.

### Part 2: IPEDS Data Integration
Merges five surveys on UNITID:
- **HD2022** (hd2022.csv): Institutional characteristics
- **OM2022** (om2022.csv): Outcome measures (awards, certificates)
- **GR2022** (gr2022.csv): Graduation rates (6-year, full-time cohort)
- **GR200_22** (gr200_22.csv): Graduation rates (2-year extended completion, all ages)
- **EF2022D** (ef2022d.csv): Retention rates (full-time, part-time, cohorts)

Output: 48,419 institutions × 32 columns with descriptive naming (e.g., Cohort_Type, Retention_Rate_FullTime_Pct).

### Part 3: Geospatial Analysis with Regex Limitations
Demonstrates ZIP code state inference vs. simple regex extraction. The majority-state rule handles ambiguous ZIPs like Fort Campbell KY/TN border.

**Key Finding**: Regex patterns (`^\d{5}`) successfully extract ZIPs but cannot infer state—ZIP-to-state mapping requires external lookup data. This illustrates why geographic automation in higher education requires reference tables, not pattern matching alone.

### Part 4: Relational Database Design
SQLite tables with explicit constraints:
- **Students**: PRIMARY KEY student_id, CHECK athlete_flag IN ('Y','N')
- **Enrollments**: FOREIGN KEY student_id, CHECK registered_flag IN ('Y','N')
- **Degrees**: FOREIGN KEY student_id

Query identifies students enrolled Fall 2025 but absent Spring 2026 registration (20 records).

## Visualization Outputs

### Part 1: Discipline-Based Attrition Concentration
Stacked horizontal bar chart showing [Fall 2025 enrollment - Spring 2026 retention] by academic discipline and athletic cohort. Reveals which discipline × cohort combinations have highest attrition.

### Part 2: Tableau Dashboard (Embedded in Report)
Interactive visualization of IPEDS graduation rates, retention by institution type, and 8-year completion trends.

### Part 3: Address State Audit
Comparison of regex-extracted state vs. ZIP-based state mapping for address validation.

## Report Generation

Render the Quarto report:

```bash
quarto render assessment_report.qmd
```

This generates `assessment_report.html` with:
- Embedded SQL query and Python code execution
- Tableau JavaScript embed (interactive visualization)
- Local image references (PowerBI sample, Part 1 attrition chart)
- Narrative explanation of each part and technical decisions
- Code folding disabled for transparency

## Dependencies

- **Python 3.10+** with NumPy <2 (for pandas/pyarrow compatibility)
- **pandas**: Data manipulation
- **sqlite3**: Relational database
- **matplotlib/seaborn**: Visualization
- **geopy**: Geocoding (Part 3)
- **quarto**: Report generation

See `environment.yml` for full specification.

## Notes

- All outputs are clean, BI-ready datasets optimized for Power BI and Tableau import
- The SQLite database enforces data integrity through PRIMARY KEY, FOREIGN KEY, and CHECK constraints
- The Quarto report provides full transparency: all code (Part 1-3 Python, Part 4 SQL) is visible with execution results
- This pipeline is reproducible: clone the repo, create the environment, run `run_all.py`

## Author
Reece McDevitt | February 2026
