import re
from pathlib import Path

import pandas as pd


DATA_PATH = Path("data/Part3/sample_addresses.csv")
OUTPUT_DIR = Path("outputs")


ZIP_STATE_LOOKUP = {
    "46204": "IN",
    "60605": "IL",
    # Fort Campbell spans KY/TN. Majority-state rule for demo.
    "42223": "KY",
}


def extract_zip(address: str) -> str:
    if not isinstance(address, str):
        return ""
    match = re.search(r"\b\d{5}\b", address)
    return match.group(0) if match else ""


def infer_state_from_zip(zip_code: str) -> str:
    return ZIP_STATE_LOOKUP.get(str(zip_code).zfill(5), "NA")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH, dtype=str)

    df["ZIP_From_Address"] = df["Full_Address"].apply(extract_zip)
    df["ZIP_Effective"] = df["ZIP_Code"].fillna("").replace("nan", "")
    df.loc[df["ZIP_Effective"].eq(""), "ZIP_Effective"] = df["ZIP_From_Address"]

    df["State_From_ZIP"] = df["ZIP_Effective"].apply(infer_state_from_zip)

    df.to_csv(OUTPUT_DIR / "part3_address_state_audit.csv", index=False)


if __name__ == "__main__":
    main()
