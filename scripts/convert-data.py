import sys
import csv
import json
from glob import glob
from pathlib import Path
from collections import defaultdict
import gzip

param_mapping = {
    "Parameter_1": "CITP_VelRelEarth_Mag",
    "Parameter_2": "CITP_DistMoon_Mag",
    "Parameter_3": "CITP_DistEarth_Mag",
    "Parameter_4": "CITP_CabTemp_Zone1",
    "Parameter_5": "CITP_CabTemp_Zone2",
    "Parameter_6": "CITP_CabTemp_Zone3",
    "Parameter_7": "CITP_CabTemp_Avg",
    "Parameter_8": "CITP_ExtTemp_Wing_1",
    "Parameter_9": "CITP_ExtTemp_Wing_2",
    "Parameter_10": "CITP_ExtTemp_Wing_3",
    "Parameter_11": "CITP_ExtTemp_Wing_4",
    "Parameter_12": "CITP_CurTime_Hours",
    "Parameter_13": "CITP_CurTime_Mins",
    "Parameter_14": "CITP_CurTime_AMPM",
    "Parameter_15": "CITP_MET_Human_Readable",
    "Parameter_16": "CITP_MET_Days",
    "Parameter_17": "CITP_MET_Hours",
    "Parameter_18": "CITP_MET_Mins",
    "Parameter_19": "CITP_MET_Secs",
    "Parameter_20": "CITP_POE_Region",
    "Parameter_21": "CITP_CabPress",
    "Parameter_22": "CITP_PSIFail",
    "Parameter_23": "CITP_OrnSpinSpeed",
    "Parameter_24": "CITP_ServiceFuelRemain",
    "Parameter_25": "CITP_CrewFuelRemain",
    "Parameter_26": "CITP_TotalFuelRemain",
    "Parameter_27": "CITP_TotNitOnb",
    "Parameter_28": "CITP_BatC1aSOC",
    "Parameter_29": "CITP_BatC1bSOC",
    "Parameter_30": "CITP_BatC2aSOC",
    "Parameter_31": "CITP_BatC2bSOC",
    "Parameter_32": "CITP_BatSOC_Concat",
    "Parameter_33": "CITP_BatC1aVolt",
    "Parameter_34": "CITP_BatC1bVolt",
    "Parameter_35": "CITP_BatC2aVolt",
    "Parameter_36": "CITP_BatC2bVolt",
    "Parameter_37": "CITP_PS1A",
    "Parameter_38": "CITP_PS1B",
    "Parameter_39": "CITP_PS2A",
    "Parameter_40": "CITP_PS2B",
    "Parameter_500": "OCAVSWXTVMX0005Q",
    "Parameter_501": "OCAVSWXTVMX0006Q"
}

json_fields_whitelist = {
    'CITP_VelRelEarth_Mag', 
    'CITP_DistMoon_Mag', 
    'CITP_DistEarth_Mag',
    'CITP_CabTemp_Zone1',
    'CITP_CabTemp_Zone2',
    'CITP_CabTemp_Zone3',
    'CITP_CabTemp_Avg',
    'CITP_ExtTemp_Wing_1', 
    'CITP_ExtTemp_Wing_2', 
    'CITP_ExtTemp_Wing_3',
    'CITP_ExtTemp_Wing_4',
    'CITP_CabPress',
    'CITP_OrnSpinSpeed',
    'CITP_BatC1aSOC',
    'CITP_BatC1bSOC',
    'CITP_BatC2aSOC',
    'CITP_BatC2bSOC',
    'CITP_BatC1aVolt',
    'CITP_BatC1bVolt',
    'CITP_BatC2aVolt',
    'CITP_BatC2bVolt',
}

time_column = "Time"

def remap_param(k):
    if k in param_mapping:
        return param_mapping[k]
    return k

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, values):
    with open(path, 'w') as f:
        json.dump(values, f)

def save_csv_auto_fields(path, rows):
    fieldnames = set()
    for r in rows:
        fieldnames |= r.keys()
    
    fieldnames.remove(time_column)
    fieldnames = sorted(fieldnames)
    with gzip.open(path, mode='wt', newline='') as f:
        csv_writer = csv.DictWriter(f, fieldnames=[time_column, *fieldnames], delimiter=';', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writeheader()
        csv_writer.writerows(sorted(rows, key=lambda x: x[time_column]))


src_directory, output_file_json, output_file_csv = sys.argv[1:]

rows = []

json_last_time = 0 
json_values = defaultdict(list)

for f in glob(src_directory + '/*.json'):
    unix_time = int(Path(f).stem)
    if unix_time > json_last_time:
        json_last_time = unix_time

    data = load_json(f)
    row = {time_column: unix_time}

    for k, v in data.items():
        if not k.startswith('Parameter_'):
            continue
        readable_name = remap_param(k)
        row[readable_name] = v['Value']

        if not readable_name in json_fields_whitelist:
            continue
        value = v['Value']
        if v['Type'] == '2':
            value = float(value)
        json_values[readable_name].append([unix_time, value])

    if row:
        rows.append(row)

for idx, vals in json_values.items():
    json_values[idx] = sorted(vals, key=lambda v: v[0])

print(json_last_time)

save_json(output_file_json, {'last_time': json_last_time, 'values': json_values})
save_csv_auto_fields(output_file_csv, rows)

print('work done')