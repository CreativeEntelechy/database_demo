from pathlib import Path
import pandas as pd


HD_PATH = Path("data/Part2/IPEDS/hd2022.csv")
OM_PATH = Path("data/Part2/IPEDS/om2022.csv")
GR_PATH = Path("data/Part2/IPEDS/gr2022.csv")
GR200_PATH = Path("data/Part2/IPEDS/gr200_22.csv")
EF_PATH = Path("data/Part2/IPEDS/ef2022d.csv")
OUTPUT_DIR = Path("outputs")


def read_csv_with_fallback(path: Path) -> pd.DataFrame:
    """Read CSV with encoding fallback for non-UTF8 files."""
    try:
        return pd.read_csv(path, dtype=str)
    except UnicodeDecodeError:
        return pd.read_csv(path, dtype=str, encoding="cp1252")


def process_hd(hd: pd.DataFrame) -> pd.DataFrame:
    """Extract institutional characteristics linking table."""
    # Filter to degree-granting using IPEDS 2022 definitions
    # SECTOR: 1=Public 4yr, 2=Private nonprofit 4yr, 3=Private for-profit 4yr,
    #         4=Public 2yr, 5=Private nonprofit 2yr, 6=Private for-profit 2yr
    if "DEGGRANT" in hd.columns:
        hd = hd[hd["DEGGRANT"].astype(str) == "1"].copy()
    else:
        hd = hd[hd["SECTOR"].astype(str).isin({"1", "2", "3", "4", "5", "6"})].copy()
    
    hd = hd[["UNITID", "INSTNM", "STABBR", "SECTOR"]].copy()
    hd["UNITID"] = hd["UNITID"].astype(str)
    hd.rename(columns={
        "INSTNM": "Institution_Name",
        "STABBR": "State",
        "SECTOR": "Sector_Code"
    }, inplace=True)
    
    return hd


def process_om(om: pd.DataFrame) -> pd.DataFrame:
    """Extract Outcome Measures (8-year tracking)."""
    # Keep UNITID and select available columns
    # Award columns decomposed by type (Certificate, Associate, Bachelor)
    # Enrollment and outcome tracking
    keep_cols = ["UNITID", "OMCHRT"]
    
    # 4-year awards
    for col in ["OMCERT4", "OMASSC4", "OMBACH4"]:
        if col in om.columns:
            keep_cols.append(col)
    
    # 6-year awards
    for col in ["OMCERT6", "OMASSC6", "OMBACH6"]:
        if col in om.columns:
            keep_cols.append(col)
    
    # 8-year awards and outcomes
    for col in ["OMCERT8", "OMASSC8", "OMBACH8", "OMENRYI", "OMENRAI", "OMENRUN", "OMNOAWD"]:
        if col in om.columns:
            keep_cols.append(col)
    
    om = om[keep_cols].copy()
    om["UNITID"] = om["UNITID"].astype(str)
    
    # Convert to numeric, handling "R" (redacted) and empty strings
    numeric_cols = [col for col in om.columns if col != "UNITID" and col != "OMCHRT"]
    for col in numeric_cols:
        om[col] = pd.to_numeric(om[col], errors="coerce").fillna(0).astype(int)
    
    # Create aggregated award columns
    if "OMCERT4" in om.columns or "OMASSC4" in om.columns or "OMBACH4" in om.columns:
        om["Award_4Year"] = om[["OMCERT4", "OMASSC4", "OMBACH4"]].fillna(0).astype(int).sum(axis=1)
    
    if "OMCERT6" in om.columns or "OMASSC6" in om.columns or "OMBACH6" in om.columns:
        om["Award_6Year"] = om[["OMCERT6", "OMASSC6", "OMBACH6"]].fillna(0).astype(int).sum(axis=1)
    
    if "OMCERT8" in om.columns or "OMASSC8" in om.columns or "OMBACH8" in om.columns:
        om["Award_8Year"] = om[["OMCERT8", "OMASSC8", "OMBACH8"]].fillna(0).astype(int).sum(axis=1)
    
    om.rename(columns={
        "OMCHRT": "Cohort_Type",
        "OMCERT4": "Award_4Year_Cert",
        "OMASSC4": "Award_4Year_Assoc",
        "OMBACH4": "Award_4Year_Bach",
        "OMCERT6": "Award_6Year_Cert",
        "OMASSC6": "Award_6Year_Assoc",
        "OMBACH6": "Award_6Year_Bach",
        "OMCERT8": "Award_8Year_Cert",
        "OMASSC8": "Award_8Year_Assoc",
        "OMBACH8": "Award_8Year_Bach",
        "OMENRYI": "Still_Enrolled_8Year",
        "OMENRAI": "Transfer_Out_8Year",
        "OMENRUN": "Attrition_Unknown_8Year",
        "OMNOAWD": "No_Award_8Year"
    }, inplace=True)
    
    return om


def process_gr(gr: pd.DataFrame) -> pd.DataFrame:
    """Extract standard graduation rates (150% normal time)."""
    # Filter to Bachelor's degree, full cohort (GRTYPE=2, CHRTSTAT=12)
    gr = gr[(gr["GRTYPE"].astype(str) == "2") & 
            (gr["CHRTSTAT"].astype(str) == "12")].copy()
    
    # Keep UNITID and total cohort size
    gr = gr[["UNITID", "GRTOTLT", "GRTOTLM", "GRTOTLW"]].copy()
    gr["UNITID"] = gr["UNITID"].astype(str)
    
    numeric_cols = ["GRTOTLT", "GRTOTLM", "GRTOTLW"]
    for col in numeric_cols:
        gr[col] = pd.to_numeric(gr[col], errors="coerce").fillna(0).astype(int)
    
    gr.rename(columns={
        "GRTOTLT": "GR_Cohort_Total",
        "GRTOTLM": "GR_Cohort_Male",
        "GRTOTLW": "GR_Cohort_Female"
    }, inplace=True)
    
    return gr


def process_gr200(gr200: pd.DataFrame) -> pd.DataFrame:
    """Extract 200% completion (8-year) Bachelor's rates."""
    # Focus on Bachelor's degree cohort
    gr200 = gr200[["UNITID", "BAREVCT", "BAEXCLU", "BAAC200", 
                    "BANC200", "BAGR200", "BASTEND"]].copy()
    gr200["UNITID"] = gr200["UNITID"].astype(str)
    
    numeric_cols = ["BAREVCT", "BAEXCLU", "BAAC200", "BANC200", "BAGR200", "BASTEND"]
    for col in numeric_cols:
        gr200[col] = pd.to_numeric(gr200[col], errors="coerce").fillna(0).astype(int)
    
    gr200.rename(columns={
        "BAREVCT": "BA_Cohort_200Pct",
        "BAEXCLU": "BA_200Pct_Exclusions",
        "BAAC200": "BA_Still_Enrolled_200Pct",
        "BANC200": "BA_Still_Enrolled_Count_200Pct",
        "BAGR200": "BA_200Pct_Completers",
        "BASTEND": "BA_Persistence_200Pct"
    }, inplace=True)
    
    return gr200


def process_ef(ef: pd.DataFrame) -> pd.DataFrame:
    """Extract retention outcomes (1-year return rate)."""
    ef = ef[["UNITID", "RET_PCF", "RET_PCP"]].copy()
    ef["UNITID"] = ef["UNITID"].astype(str)
    
    # Convert percentages to numeric
    for col in ["RET_PCF", "RET_PCP"]:
        ef[col] = pd.to_numeric(ef[col], errors="coerce").fillna(0)
    
    ef.rename(columns={
        "RET_PCF": "Retention_Rate_FullTime_Pct",
        "RET_PCP": "Retention_Rate_PartTime_Pct"
    }, inplace=True)
    
    return ef


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load all datasets
    hd = read_csv_with_fallback(HD_PATH)
    om = read_csv_with_fallback(OM_PATH)
    gr = read_csv_with_fallback(GR_PATH)
    gr200 = read_csv_with_fallback(GR200_PATH)
    ef = read_csv_with_fallback(EF_PATH)

    # Process each dataset
    hd = process_hd(hd)
    om = process_om(om)
    gr = process_gr(gr)
    gr200 = process_gr200(gr200)
    ef = process_ef(ef)

    # Merge all on UNITID
    merged = hd.copy()
    merged = merged.merge(om, on="UNITID", how="left")
    merged = merged.merge(gr, on="UNITID", how="left")
    merged = merged.merge(gr200, on="UNITID", how="left")
    merged = merged.merge(ef, on="UNITID", how="left")

    # Fill NaN with 0 for numeric outcome columns
    numeric_outcome_cols = [
        "Award_4Year", "Award_6Year", "Award_8Year", 
        "Award_4Year_Cert", "Award_4Year_Assoc", "Award_4Year_Bach",
        "Award_6Year_Cert", "Award_6Year_Assoc", "Award_6Year_Bach",
        "Award_8Year_Cert", "Award_8Year_Assoc", "Award_8Year_Bach",
        "Transfer_Out_8Year", "Still_Enrolled_8Year", "Attrition_Unknown_8Year", "No_Award_8Year",
        "GR_Cohort_Total", "GR_Cohort_Male", "GR_Cohort_Female",
        "BA_Cohort_200Pct", "BA_200Pct_Exclusions", "BA_Still_Enrolled_200Pct", 
        "BA_Still_Enrolled_Count_200Pct", "BA_200Pct_Completers", "BA_Persistence_200Pct",
        "Retention_Rate_FullTime_Pct", "Retention_Rate_PartTime_Pct"
    ]
    
    for col in numeric_outcome_cols:
        if col in merged.columns:
            merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0)

    # Export
    merged.to_csv(OUTPUT_DIR / "IPEDS_Cleaned_For_Tableau.csv", index=False)
    
    # Generate metadata
    notes = f"""IPEDS 2022 Academic Success Dataset
=====================================

Institution Base (HD2022):
- Filtered to degree-granting institutions (Sectors 1-6)
- Includes: Institution Name, State, Sector Code

Outcome Measures (OM2022):
- 8-year tracking of all student cohorts
- Award rates at 4, 6, and 8 years
- Transfer-out and persistence outcomes

Graduation Rates (GR2022):
- Standard Bachelor's cohort tracking
- 100% (normal time) and 150% completion rates
- Demographic breakdown by gender

Extended Completion (GR200_22):
- 200% normal time (8-year) Bachelor's completion
- Persistence and enrollment outcomes

Retention (EF2022D):
- 1-year return rates for full-time and part-time students

Total Records: {len(merged)}
"""
    
    (OUTPUT_DIR / "part2_ipeds_metadata.txt").write_text(notes)


if __name__ == "__main__":
    main()
