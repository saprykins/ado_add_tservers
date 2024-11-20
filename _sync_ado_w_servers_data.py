import pandas as pd
import requests
import json
import csv
import sys


if len(sys.argv) > 1:
    fn_ado_enriched = sys.argv[1]
    fn_log = sys.argv[2]



organization = "g-"
project = "C-"
pat = "C"
server_workitem = "T-"


# Read the CSV file into a Pandas DataFrame
csv_file_path = fn_ado_enriched


def write_to_csv(*args):
    with open(fn_log, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(args)


def create_child(workitemtype, title, parent_id, inf_src):
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
                "rel": "System.LinkTypes.Hierarchy-Reverse",
                "url": get_app_url(parent_id)
            }
        },
        {
            "op": "add",
            "path": "/fields/Information_source",
            "value": inf_src  # Set the Information_source field to "delete"
        }
    ]

    try:
        response = requests.post(
            url,
            data=json.dumps(body),
            headers=headers,
            auth=("", pat),
            timeout=10  # Set a timeout
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to create server work item: {e}")
        write_to_csv("Server_ID", "", "server_name", "creation_failed")
        return None

    work_item_id = response.json()['id']
    print(f"Server Work Item ID: {work_item_id} created successfully")
    write_to_csv("Server_ID", work_item_id, "server_name", "created_successfully")
    return work_item_id  # Return the server work_item_id if successful


def get_app_url(parent_id):
    url = f"https://dev.azure.com/{organization}/_apis/wit/workItems/{parent_id}?$expand=all"

    headers = {
        "Content-Type": "application/json-patch+json"
    }

    response = requests.get(
        url=url,
        headers=headers,
        auth=("", pat),
        timeout=10  # Set a timeout
    )
    return response.json()["url"]


def modify_existing(workitemtype, title, work_item_id, inf_src):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{work_item_id}?api-version=7.0"

    headers = {
        "Content-Type": "application/json-patch+json"
    }

    body = [
        {
            "op": "replace",
            "path": "/fields/System.Title",
            "value": title  # Set the updated title
        },
        {
            "op": "replace",
            "path": "/fields/Information_source",
            "value": inf_src  # Set the updated Information_source field
        }
    ]

    try:
        response = requests.patch(
            url,
            data=json.dumps(body),
            headers=headers,
            auth=("", pat),
            timeout=10  # Set a timeout
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to update server work item: {e}")
        write_to_csv("Server_ID", work_item_id, "server_name", "update_failed")
        return None

    print(f"Server Work Item ID: {work_item_id} updated successfully")
    write_to_csv("Server_ID", work_item_id, "server_name", "updated_successfully")
    return work_item_id  # Return the server work_item_id if successful


df = pd.read_csv(csv_file_path)

# Iterate through the CSV data to create servers for each application
for index, row in df.iterrows():
    app_title = row['app_sys_id']  # Assuming 'app_sys_id' is the column with application titles
    server_title = row['servers']  # Assuming 'servers' is the column with server titles
    parent_id = row['env_id_ado']
    inf_src = row['inf_src']  # Assuming 'inf_src' is the column with Information_source values
    server_id_ado = row['server_id_ado']  # Assuming 'server_id_ado' is the column with server work_item_id

    if pd.notna(server_id_ado):  # Check if server_id_ado is not empty
        # Modify the existing work item (server) with the specified server_id_ado
        server_id_ado = int(server_id_ado)
        modify_existing(server_workitem, server_title, server_id_ado, inf_src)
    else:
        parent_id = int(parent_id)
        # Create the child work item (server) for the application
        create_child(server_workitem, server_title, parent_id, inf_src)
