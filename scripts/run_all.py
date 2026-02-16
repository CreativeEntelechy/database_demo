import subprocess
import sys
from pathlib import Path


SCRIPTS = [
    "part1_prep.py",
    "part2_ipeds_prep.py",
    "part3_geo_audit.py",
    "part4_sqlite.py",
]


def main() -> None:
    scripts_dir = Path(__file__).parent

    for script in SCRIPTS:
        script_path = scripts_dir / script
        result = subprocess.run([sys.executable, str(script_path)], check=False)
        if result.returncode != 0:
            raise SystemExit(f"Failed running {script}")


if __name__ == "__main__":
    main()
