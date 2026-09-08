import os
import pandas as pd

DATA_PATH = "data/"


def safe_read_csv(file_path):
  """Helper function to read CSVs reliably even if minor line formatting issues exist.

  """
  try:
    return pd.read_csv(file_path)
  except pd.errors.ParserError:
    return pd.read_csv(file_path, on_bad_lines="skip", engine="python")


def load_data():
  """Loads raw CSV datasets and merges them on ISO3 code."""
  countries = safe_read_csv(os.path.join(DATA_PATH, "countries.csv"))
  fatf = safe_read_csv(os.path.join(DATA_PATH, "fatf.csv"))
  eu = safe_read_csv(os.path.join(DATA_PATH, "eu_amlr.csv"))
  effectiveness = safe_read_csv(os.path.join(DATA_PATH, "effectiveness.csv"))
  structural = safe_read_csv(os.path.join(DATA_PATH, "structural.csv"))
  sanctions = safe_read_csv(os.path.join(DATA_PATH, "sanctions.csv"))

  # Merge datasets on iso3
  df = countries.merge(fatf, on="iso3", how="left")
  df = df.merge(eu, on="iso3", how="left")
  df = df.merge(effectiveness, on="iso3", how="left")
  df = df.merge(structural, on="iso3", how="left")
  df = df.merge(sanctions, on="iso3", how="left")

  # Load sources table if available
  sources_path = os.path.join(DATA_PATH, "sources.csv")
  if os.path.exists(sources_path):
    sources = safe_read_csv(sources_path)
  else:
    sources = pd.DataFrame()

  return df, sources
