import gspread
import numpy as np
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

from pages.helpers.plots import draw_2axis_plot, MPE_EVENTS_COLOR, MAX_SPEED_COLOR, LimitsDoubleAxis
from pages.helpers.processing_helpers import get_processed_df
from pages.helpers.utils import authenticate, add_download_image_button, convert_df2csv

st.title("FMS - analysis")

status = authenticate()

if status:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": st.secrets.google_api.type,
        "project_id": st.secrets.google_api.project_id,
        "private_key_id": st.secrets.google_api.private_key_id,
        "private_key": st.secrets.google_api.private_key,
        "client_email": st.secrets.google_api.client_email,
        "client_id": st.secrets.google_api.client_id,
        "auth_uri": st.secrets.google_api.auth_uri,
        "token_uri": st.secrets.google_api.token_uri,
        "auth_provider_x509_cert_url": st.secrets.google_api.auth_provider_x509_cert_url,
        "client_x509_cert_url": st.secrets.google_api.client_x509_cert_url,
    }, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheets document
    sheet = client.open('[DIF] Testiranje-proba (Responses)').sheet1
    df = get_processed_df(sheet)

    st.title('Individual analysis')
    jmbg_choices = df.JMBG.unique()
    picked_player_jmbg = st.selectbox('Select JMBG', jmbg_choices, index=0)
    df_num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    param1_select = st.selectbox('Select param1', df_num_cols, index=df_num_cols.index('% masti'))
    param2_select = st.selectbox('Select param1', df_num_cols, index=df_num_cols.index('% mišića'))

    param1_limits = (df[param1_select].min(), df[param1_select].max())
    param2_limits = (df[param2_select].min(), df[param2_select].max())

    p_df = df[df.JMBG == picked_player_jmbg]
    player_info = p_df.iloc[0]
    fig, ax1, ax2 = draw_2axis_plot(
        p_df,
        ('Dates', param1_select),
        ('Dates', param2_select),
        (param1_select, param2_select),
        (param1_select, param2_select),
        (MPE_EVENTS_COLOR, MAX_SPEED_COLOR),
        LimitsDoubleAxis(param1_limits, param2_limits),
        x_param='date'
    )
    fig.suptitle(f'{player_info["Ime"]} {player_info["Prezime"]}')
    st.pyplot(fig)
    add_download_image_button(
        fig=fig,
        button_text='Download image',
        filename=f'{player_info["JMBG"]}_{player_info["Ime"]}_{player_info["Prezime"]}.png'
    )
    st.header('CSV files')
    st.subheader('Individual')
    st.dataframe(p_df)
    csv = convert_df2csv(p_df)
    st.download_button(
        "Download as csv",
        csv,
        f'{player_info["JMBG"]}_{player_info["Ime"]}_{player_info["Prezime"]}.csv',
        "text/csv",
        key='download-csv-player'
    )

    st.subheader('All')
    st.dataframe(df)
    csv = convert_df2csv(df)
    st.download_button(
        "Download as csv",
        csv,
        f'all_data.csv',
        "text/csv",
        key='download-csv-all'
    )


    # ------------------------------------------------------
