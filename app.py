import streamlit as st
import pandas as pd
from io import BytesIO

def expand_turbine_data(df):
    df = df.dropna(axis=0).copy()
    df['Stop Date'] = pd.to_datetime(df['Stop Date'], errors='coerce')
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')

    expanded_rows = []

    for _, row in df.iterrows():
        if pd.notna(row['Stop Date']) and pd.notna(row['Start Date']):
            if row['Stop Date'].date() != row['Start Date'].date():
                date_range = pd.date_range(row['Stop Date'].date(), row['Start Date'].date())

                for i, current_date in enumerate(date_range):
                    new_row = row.copy()
                    new_row['Stop Date'] = current_date
                    new_row['Start Date'] = current_date

                    if i == 0:
                        new_row['StopTime'] = row['StopTime']
                        new_row['Start Time'] = pd.to_datetime("23:59:59", format='%H:%M:%S').time()
                    elif i == len(date_range) - 1:
                        new_row['StopTime'] = pd.to_datetime("00:00:00", format='%H:%M:%S').time()
                        new_row['Start Time'] = row['Start Time']
                    else:
                        new_row['StopTime'] = pd.to_datetime("00:00:00", format='%H:%M:%S').time()
                        new_row['Start Time'] = pd.to_datetime("23:59:59", format='%H:%M:%S').time()

                    expanded_rows.append(new_row)
            else:
                expanded_rows.append(row)
        else:
            expanded_rows.append(row)

    expanded_df = pd.DataFrame(expanded_rows)
    expanded_df['Stop Date'] = pd.to_datetime(expanded_df['Stop Date']).dt.strftime('%d-%m-%Y')
    expanded_df['Start Date'] = pd.to_datetime(expanded_df['Start Date']).dt.strftime('%d-%m-%Y')
    return expanded_df

# Streamlit UI
st.title("Turbine Downtime Expander Dashboard")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("File uploaded successfully!")
    st.write("Preview of Uploaded Data:")
    st.dataframe(df.head())

    if st.button(" Expand Downtime Rows"):
        result_df = expand_turbine_data(df)
        st.success("Done! Here's a preview:")
        st.dataframe(result_df.head())

        # Convert to downloadable Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            result_df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="📥 Download Expanded Excel",
            data=output,
            file_name="expanded_turbine_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )