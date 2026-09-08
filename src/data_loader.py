import pandas as pd
import os

DATA_PATH = "data/"

def load_data():
    """
    Loads raw CSV datasets and merges them on ISO3 code.
    """
    countries = pd.read_csv(os.path.join(DATA_PATH, "countries.csv"))
    fatf = pd.read_csv(os.path.join(DATA_PATH, "fatf.csv"))
    eu = pd.read_csv(os.path.join(DATA_PATH, "eu_amlr.csv"))
    effectiveness = pd.read_csv(os.path.join(DATA_PATH, "effectiveness.csv"))
    structural = pd.read_csv(os.path.join(DATA_PATH, "structural.csv"))
    sanctions = pd.read_csv(os.path.join(DATA_PATH, "sanctions.csv"))
    
    # Merge datasets on iso3
    df = countries.merge(fatf, on="iso3", how="left")
    df = df.merge(eu, on="iso3", how="left")
    df = df.merge(effectiveness, on="iso3", how="left")
    df = df.merge(structural, on="iso3", how="left")
    df = df.merge(sanctions, on="iso3", how="left")
    
    # Load sources table if available
    sources_path = os.path.join(DATA_PATH, "sources.csv")
    if os.path.exists(sources_path):
        sources = pd.read_csv(sources_path)
    else:
        sources = pd.DataFrame()
        
    return df, sources
