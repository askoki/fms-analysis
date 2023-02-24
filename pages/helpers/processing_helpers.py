from datetime import datetime

import numpy as np
import pandas as pd
import streamlit


@streamlit.cache_data
def get_processed_df(_worksheet) -> pd.DataFrame:
    rows = _worksheet.get_all_values()
    df = pd.DataFrame(rows)
    df.columns = df.iloc[0]
    df = df.iloc[1:]

    df['Datum rođenja'] = pd.to_datetime(df['Datum rođenja']).dt.date
    today = datetime.now().date()
    df.loc[:, 'Starost'] = (today - df['Datum rođenja']).dt.total_seconds() / 3600 / 24 / 365
    df.Starost = df.Starost.astype(int)
    df.loc[:, 'date'] = pd.to_datetime(df.Timestamp).dt.date
    df = df.drop(columns=['Datum rođenja', '', 'Timestamp'])

    cols2convert = [
        'Visina (cm)', 'Težina (kg)', 'BMI',
        '% masti', '% mišića', 'CMJ I', 'CMJ II', 'CMJ III', 'Starost'
    ]
    for c in cols2convert:
        df.loc[:, c] = df[c].astype(float)
    df.loc[:, 'CMJ mean'] = df.apply(lambda r: np.mean([r['CMJ I'], r['CMJ II'], r['CMJ III']]), axis=1)
    df.loc[:, 'CMJ mean'] = df.loc[:, 'CMJ mean'].round(2)
    df.loc[:, 'CMJ std'] = df.apply(lambda r: np.std([r['CMJ I'], r['CMJ II'], r['CMJ III']]), axis=1)
    df.loc[:, 'CMJ std'] = df.loc[:, 'CMJ std'].round(2)
    df = df.sort_values('date')
    df = df.reset_index(drop=True)
    return df
