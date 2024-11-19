#!/bin/bash

# Activate virtual environment
source ./venv/Scripts/activate

date=$(date +'%Y-%m-%d')
# datetime=$(date +'%Y-%m-%d %H:%M')


# Description of file names: 
fn_log="logs/log_${date}.csv"

fn_aws_data="sources/data_aws.xlsx"
fn_azure_data="sources/data_azure.xlsx"
fn_p--_data="sources/data_p--.xlsx"
fn_m--_all="intermediate_results/m--_all.csv"
fn_m--_and_p--_all="intermediate_results/m--_and_p--.csv"
fn_ado_data='sources/pbi_control_tower.xlsx'
fn_ado_enriched="intermediate_results/control_tower_enriched.csv"



# Run Python scripts
# python _merge_m--_reports.py $fn_aws_data $fn_azure_data $fn_m--_all
# python _add_p--_to_m--.py $fn_m--_all $fn_p--_data $fn_m--_and_p--_all


# fn_ado_data='../work_with_json/sources_v2/test_control_tower.xlsx'
# fn_m--_and_p--_all='../work_with_json/sources_v2/test_all_servers.csv'
# python _compare_ado_w_reports.py $fn_ado_data $fn_m--_and_p--_all $fn_ado_enriched

python _sync_ado_w_servers_data.py $fn_ado_enriched $fn_log
