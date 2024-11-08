import pandas as pd
import requests
import json

organization = "_"
project = "_"
pat = "_"
server_workitem = ""

# Function to create child work items (servers)
def create_child(workitemtype, title, parent_id):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/${workitemtype}?api-version=7.0"
    
    headers = {
        "Content-Type": "application/json-patch+json"
    }

    body = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title  # Set the server title
        },
        {
            "op": "add",
            "path": "/fields/System.Parent",
            "value": parent_id  # Set the parent work item ID (application ID)
        },
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel":"System.LinkTypes.Hierarchy-Reverse",
                "url":get_app_url(parent_id)
                }
        }
    ]

    response = requests.post(
        url,
        data=json.dumps(body),
        headers=headers,
        auth=("", pat)
    )

    if response.status_code == 200:
        work_item_id = response.json()['id']
        print(f"Server Work Item ID: {work_item_id}")
        return work_item_id  # Return the server work_item_id if successful
    else:
        print(f"Failed to create server work item. Status code: {response.status_code}")
        print(response.text)
        return None  # Return None if the creation fails


def get_app_url(parent_id):   
    '''
    Get the link of the parent
    '''

    url = 'https://dev.azure.com/' + organization + '/_apis/wit/workItems/' + str(parent_id) + '?$expand=all'
    
    headers = {
        "Content-Type": "application/json-patch+json"
    }

    response = requests.get(
        url = url,
        headers=headers,
        auth=("", pat), 
    )
    lnk = response.json()["url"]
    return lnk


# Read the CSV file into a Pandas DataFrame
csv_file_path = 'sources/test_server_list.csv'  # Replace with the path to your CSV file
df = pd.read_csv(csv_file_path)




# Iterate through the CSV data to create servers for each application
for index, row in df.iterrows():
    app_title = row['app_sys_id']  # Assuming 'app_sys_id' is the column with application titles
    server_title = row['servers']  # Assuming 'servers' is the column with server titles
    parent_id = row['env_id_ado']

    # Create the child work item (server) for the application
    create_child(server_workitem, server_title, parent_id)
