import pandas as pd
import sys


if len(sys.argv) > 1:
    fn_mpi_all = sys.argv[1]
    fn_pod_data = sys.argv[2]
    fn_mpi_and_pod_all = sys.argv[3]


# Load data from CSV
csv_data = pd.read_csv(fn_mpi_all)

# Load data from Excel
excel_data = pd.read_excel(fn_pod_data)

# Rename columns in Excel data to match the CSV data
# excel_data.rename(columns={'Name': 'target_server', 'Sys ID service': 'silva_id'}, inplace=True)

excel_data = excel_data.iloc[:, [4, 39, 2]]  # Select columns 5, 2, and 3 (Python is 0-indexed)
excel_data.columns = ['target_server', 'silva_id', 'csp']  # Rename the columns


excel_data['csp'] = 'pod'  # Set the 'csp' column to 'pod' for all rows in the Excel data


# Union the two datasets
unioned_data = pd.concat([csv_data, excel_data])

# Select only the required columns
unioned_data = unioned_data[['target_server', 'silva_id', 'csp']]
unioned_data.columns = ['servers', 'app_sys_id', 'csp']

# Save the unioned data to a CSV file
unioned_data.to_csv(fn_mpi_and_pod_all, index=False)
