import pandas as pd
import sys


if len(sys.argv) > 1:
    fn_ado_data = sys.argv[1]
    fn_mpi_and_pod_all = sys.argv[2]
    fn_ado_enriched = sys.argv[3]


# Read the current state file and latest version file into pandas DataFrames
current_state = pd.read_excel(fn_ado_data)
latest_version = pd.read_csv(fn_mpi_and_pod_all)


##
## Add filtering only the data 
# current_state = current_state.dropna(subset=['app_sys_id'])
##

# Set the 'inf_src' column with default values
current_state['inf_src'] = 'stay'

# Initialize an empty DataFrame to store the result
result = pd.DataFrame(columns=['env_id_ado', 'server_id_ado', 'app_sys_id', 'servers', 'csp', 'inf_src'])

# Create a dictionary mapping app_sys_id to env_id_ado
env_id_map = current_state[['app_sys_id', 'env_id_ado']].dropna().drop_duplicates().set_index('app_sys_id').to_dict()['env_id_ado']

# Iterate through each unique app_sys_id in the current state
for app_sys_id in current_state['app_sys_id'].unique():
    current_subset = current_state[current_state['app_sys_id'] == app_sys_id]
    latest_subset = latest_version[latest_version['app_sys_id'] == app_sys_id]
    
    # Check for servers that exist in both current and latest versions
    for _, current_row in current_subset.iterrows():
        matching_latest_row = latest_subset[latest_subset['servers'] == current_row['servers']]
        if not matching_latest_row.empty:
            result = pd.concat([result, pd.DataFrame([[
                current_row['env_id_ado'], current_row['server_id_ado'], current_row['app_sys_id'],
                current_row['servers'], matching_latest_row.iloc[0]['csp'], 'stay'
            ]], columns=result.columns)])
        else:
            result = pd.concat([result, pd.DataFrame([[
                current_row['env_id_ado'], current_row['server_id_ado'], current_row['app_sys_id'],
                current_row['servers'], '', 'delete'
            ]], columns=result.columns)])
    
    # Check for servers that exist in latest version but not in current state
    for _, latest_row in latest_subset.iterrows():
        if not current_subset[current_subset['servers'] == latest_row['servers']].empty:
            continue
        env_id_ado = env_id_map.get(app_sys_id, '')
        result = pd.concat([result, pd.DataFrame([[
            env_id_ado, '', latest_row['app_sys_id'], latest_row['servers'], latest_row['csp'], 'added'
        ]], columns=result.columns)])

# Filter out rows where the 'servers' value is empty or NaN
result = result.dropna(subset=['servers'])

# Write the updated DataFrame to a new CSV file
result.to_csv(fn_ado_enriched, index=False)
