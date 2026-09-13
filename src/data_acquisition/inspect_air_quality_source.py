"""Inspect raw air-quality files and summarize available Delhi records."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DELHI_TOKENS = ("delhi", "new delhi")


def read_table(path: Path) -> pd.DataFrame:
    suffixes = "".join(path.suffixes)
    if suffixes.endswith(".csv.gz") or path.suffix == ".csv":
        return pd.read_csv(path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported file type: {path}")


def find_delhi_rows(df: pd.DataFrame) -> pd.DataFrame:
    text_cols = [
        col
        for col in df.columns
        if df[col].dtype == "object"
        or "string" in str(df[col].dtype).lower()
    ]
    if not text_cols:
        return df.iloc[0:0].copy()

    mask = pd.Series(False, index=df.index)
    for col in text_cols:
        values = df[col].astype("string").str.lower()
        col_mask = pd.Series(False, index=df.index)
        for token in DELHI_TOKENS:
            col_mask = col_mask | values.str.contains(token, na=False, regex=False)
        mask = mask | col_mask
    return df.loc[mask].copy()


def summarize(path: Path) -> None:
    df = read_table(path)
    delhi = find_delhi_rows(df)

    print(f"file: {path}")
    print(f"rows: {len(df):,}")
    print(f"columns: {len(df.columns):,}")
    print("column_names:")
    for col in df.columns:
        print(f"  - {col}")
    print(f"delhi_candidate_rows: {len(delhi):,}")

    for col in df.columns:
        lowered = col.lower()
        if any(token in lowered for token in ["date", "time", "timestamp"]):
            values = pd.to_datetime(df[col], errors="coerce")
            if values.notna().any():
                print(f"{col}_min: {values.min()}")
                print(f"{col}_max: {values.max()}")

    if len(delhi):
        print("delhi_sample:")
        print(delhi.head(5).to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    summarize(Path(args.path))


if __name__ == "__main__":
    main()
