import os
import pandas as pd

# Determine absolute path to the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data")


def safe_read_csv(filename):
  """Helper function to safely read CSV files relative to the project data directory."""
  file_path = os.path.join(DATA_PATH, filename)

  if not os.path.exists(file_path):
    # Return an empty DataFrame with iso3 column if file is missing to prevent total app failure
    return pd.DataFrame(columns=["iso3"])

  try:
    return pd.read_csv(file_path)
  except pd.errors.ParserError:
    return pd.read_csv(file_path, on_bad_lines="skip", engine="python")


def load_data():
  """Loads raw CSV datasets and merges them on ISO3 code."""
  countries = safe_read_csv("countries.csv")
  fatf = safe_read_csv("fatf.csv")
  eu = safe_read_csv("eu_amlr.csv")
  effectiveness = safe_read_csv("effectiveness.csv")
  structural = safe_read_csv("structural.csv")
  sanctions = safe_read_csv("sanctions.csv")

  # Merge datasets on iso3
  df = countries.merge(fatf, on="iso3", how="left")
  df = df.merge(eu, on="iso3", how="left")
  df = df.merge(effectiveness, on="iso3", how="left")
  df = df.merge(structural, on="iso3", how="left")
  df = df.merge(sanctions, on="iso3", how="left")

  # Load sources table if available
  sources = safe_read_csv("sources.csv")

  return df, sources
