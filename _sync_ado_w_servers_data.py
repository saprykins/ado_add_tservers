import pandas as pd
import requests
import json
import csv
import sys
import time
from datetime import datetime

if len(sys.argv) > 1:
    fn_ado_enriched = sys.argv[1]
    fn_log = sys.argv[2]

with open('config.json') as config_file:
    config = json.load(config_file)

organization = config["org_name"]
project = config["proj_name"]
pat = config["access_token"]
server_workitem = config["item_type"]


# Read the CSV file into a Pandas DataFrame
csv_file_path = fn_ado_enriched

def write_to_csv(*args):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp
    with open(fn_log, 'a', newline='') as file:  # Keep the append mode to add new entries
        writer = csv.writer(file)
        writer.writerow([timestamp] + list(args))  # Prepend the timestamp to the log entry


def get_app_url(parent_id):
    url = f"https://dev.azure.com/{organization}/_apis/wit/workItems/{parent_id}?$expand=all"
    headers = {
        "Content-Type": "application/json-patch+json"
    }
    
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.get(
                url=url,
                headers=headers,
                auth=("", pat),
                timeout=30  # Increase timeout
            )
            response.raise_for_status()
            return response.json()["url"]
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: Failed to get app URL: {e}")
            time.sleep(5)  # Wait for 5 seconds before retrying

    raise Exception("Failed to get app URL after multiple attempts.")



def create_child(workitemtype, title, parent_id, inf_src, target, server_title):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/${workitemtype}?api-version=7.0"

    headers = {
        "Content-Type": "application/json-patch+json"
    }

    body = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title
        },
        {
            "op": "add",
            "path": "/fields/System.Parent",
            "value": parent_id
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
            "value": inf_src
        },
        {
            "op": "add",
            "path": "/fields/Custom.Target",
            "value": target  # Set the Target field based on csp value
        }
    ]

    try:
        response = requests.post(
            url,
            data=json.dumps(body),
            headers=headers,
            auth=("", pat),
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to create server work item: {e}")
        write_to_csv("Server_ID", "", server_title, "creation_failed")
        return None

    work_item_id = response.json()['id']
    print(f"Server Work Item ID: {work_item_id} created successfully")
    write_to_csv("Server_ID", work_item_id, server_title, "created_successfully")
    return work_item_id


def modify_existing(workitemtype, title, work_item_id, inf_src, target, server_title):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{work_item_id}?api-version=7.0"

    headers = {
        "Content-Type": "application/json-patch+json"
    }

    body = [
        {
            "op": "replace",
            "path": "/fields/System.Title",
            "value": title
        },
        {
            "op": "replace",
            "path": "/fields/Information_source",
            "value": inf_src
        },
        {
            "op": "replace",
            "path": "/fields/Custom.Target",
            "value": target  # Update the Target field
        }
    ]

    try:
        response = requests.patch(
            url,
            data=json.dumps(body),
            headers=headers,
            auth=("", pat),
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to update server work item: {e}")
        write_to_csv("Server_ID", work_item_id, server_title, "update_failed")
        return None

    print(f"Server Work Item ID: {work_item_id} updated successfully")
    write_to_csv("Server_ID", work_item_id, server_title, "updated_successfully")
    return work_item_id



def map_csp_to_target(csp_value):
    """ Map the csp value to the corresponding target string. """
    if pd.isna(csp_value) or csp_value.strip() == "":
        return ""
    mapping = {
        "pod": "P--",
        "aws": "M---AWS",
        "azure": "M---Azure"
    }
    return mapping.get(csp_value.lower(), "")


df = pd.read_csv(csv_file_path)

# Iterate through the CSV data to create servers for each application

for index, row in df.iterrows():
    app_title = row['app_sys_id']
    server_title = row['servers']
    parent_id = row['env_id_ado']
    inf_src = row['inf_src']
    server_id_ado = row['server_id_ado']
    csp = row['csp']  # Assuming 'csp' is the column with CSP values

    # Map csp value to target
    target = map_csp_to_target(csp)

    if pd.notna(server_id_ado):
        server_id_ado = int(server_id_ado)
        modify_existing(server_workitem, server_title, server_id_ado, inf_src, target, server_title)
    else:
        parent_id = int(parent_id)
        create_child(server_workitem, server_title, parent_id, inf_src, target, server_title)
