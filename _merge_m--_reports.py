import pandas as pd
import sys


if len(sys.argv) > 1:
    fn_aws = sys.argv[1]
    fn_azure = sys.argv[2]
    fn_mpi_all = sys.argv[3]

# Read the data from the Excel files into pandas dataframes
data_aws = pd.read_excel(fn_aws)
data_azure = pd.read_excel(fn_azure)

# Select the required columns and add the 'csp' column
data_aws = data_aws[['hostname', 'appsysid']]
data_aws['csp'] = 'aws'

data_azure = data_azure[['local-vmfqdn', 'global-appserviceid']]
data_azure['csp'] = 'azure'

# Rename the columns to match the required output
data_aws.columns = ['target_server', 'silva_id', 'csp']
data_azure.columns = ['target_server', 'silva_id', 'csp']


# Filter out rows with missing target_server or silva_id values
data_aws = data_aws.dropna(subset=['target_server', 'silva_id'])
data_azure = data_azure.dropna(subset=['target_server', 'silva_id'])


# Concatenate the two dataframes into one
result = pd.concat([data_aws, data_azure])

# Save the resulting dataframe to a CSV file
result.to_csv(fn_mpi_all, index=False)
