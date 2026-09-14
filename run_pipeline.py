"""Run the reproducible local pipeline after raw data is available."""

from __future__ import annotations

import subprocess
import sys
import argparse
from pathlib import Path


PYTHON = sys.executable

COMMANDS = [
    [PYTHON, "src/preprocessing/prepare_aqi_long.py"],
    [PYTHON, "src/preprocessing/prepare_weather.py"],
    [PYTHON, "-m", "src.analysis.audit_dataset"],
    [PYTHON, "-m", "src.analysis.reassess_stations"],
    [PYTHON, "-m", "src.analysis.extended_quality"],
    [PYTHON, "-m", "unittest", "discover", "-s", "tests"],
    [PYTHON, "-m", "src.models.run_episode_system"],
    [PYTHON, "-m", "src.evaluation.issued_episodes"],
    [PYTHON, "-m", "src.models.validate_missing_history"],
    [PYTHON, "-m", "src.models.train_missing_fallback"],
    [PYTHON, "-m", "src.evaluation.combine_fallback"],
    [PYTHON, "-m", "unittest", "discover", "-s", "tests"],
    [PYTHON, "-m", "src.analysis.report_missing_fallback"],
    [PYTHON, "-m", "src.analysis.report_system"],
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--report-only', action='store_true', help='Regenerate report from existing completed results')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if args.report_only:
        subprocess.run([PYTHON,'-m','src.evaluation.issued_episodes'],check=True,cwd=root)
        if (root/'experiments/results/combined_system/complete.json').exists():
            subprocess.run([PYTHON,'-m','src.analysis.report_missing_fallback'],check=True,cwd=root)
        subprocess.run([PYTHON,'-m','src.analysis.report_system'],check=True,cwd=root)
        return
    if not (root/'data/interim/delhi_pollutants_2017.parquet').exists():
        subprocess.run([PYTHON,'-m','src.data_acquisition.investigate_pollutants'],check=True,cwd=root)
    for command in COMMANDS:
        print("Running:", " ".join(command))
        subprocess.run(command, check=True,cwd=root)


if __name__ == "__main__":
    main()
