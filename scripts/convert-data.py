import sys
import csv
import json
from glob import glob
from pathlib import Path
from collections import defaultdict
import gzip
import time

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
    'CITP_VelRelEarth_Mag': None,
    'CITP_DistMoon_Mag': None,
    'CITP_DistEarth_Mag': None,
    'CITP_CabTemp_Zone1': 'CITP_CabTemp',
    'CITP_CabTemp_Zone2': 'CITP_CabTemp',
    'CITP_CabTemp_Zone3': 'CITP_CabTemp',
    'CITP_CabTemp_Avg': 'CITP_CabTemp',
    'CITP_ExtTemp_Wing_1': 'CITP_ExtTemp',
    'CITP_ExtTemp_Wing_2': 'CITP_ExtTemp',
    'CITP_ExtTemp_Wing_3': 'CITP_ExtTemp',
    'CITP_ExtTemp_Wing_4': 'CITP_ExtTemp',
    'CITP_CabPress': None,
    'CITP_OrnSpinSpeed': None,
    'CITP_BatC1aSOC': 'CITP_BatSOC',
    'CITP_BatC1bSOC': 'CITP_BatSOC',
    'CITP_BatC2aSOC': 'CITP_BatSOC',
    'CITP_BatC2bSOC': 'CITP_BatSOC',
    'CITP_BatC1aVolt': 'CITP_BatVolt',
    'CITP_BatC1bVolt': 'CITP_BatVolt',
    'CITP_BatC2aVolt': 'CITP_BatVolt',
    'CITP_BatC2bVolt': 'CITP_BatVolt',

    'CITP_ServiceFuelRemain': 'CITP_Fuel',
    'CITP_CrewFuelRemain': 'CITP_Fuel',
    'CITP_TotalFuelRemain': 'CITP_Fuel',
}

json_group_description = {
    'CITP_VelRelEarth_Mag': 'Orion velocity (km/h)',
    'CITP_DistMoon_Mag': 'Orion current distance to the surface of the Moon (km)',
    'CITP_DistEarth_Mag': 'Orion current distance to the surface of the Earth (km)',
    'CITP_CabTemp': 'Max cabin temparatures in each zone and avg (??C)',
    'CITP_ExtTemp': 'Max temperature reading between 2 sensors for each of the 4 solar array wings (??C)',
    'CITP_CabPress': 'Average value between 2 pressure sensors. (kPa)',
    'CITP_OrnSpinSpeed': 'Orion\'s current spin speed (degrees per minute)',
    'CITP_BatSOC': 'The percent of life left in each of the 4 batteries onboard (%)',
    'CITP_BatVolt': 'The voltages of each of the 4 batteries onboard (volts)',
    'CITP_Fuel': 'Fuel remaining in service module, crew module and total fuel both modules (kg)',
}


def mile2km(x):
    return round(x * 1.609344)


def fahrenheit2celsius(x):
    return round((x - 32) * 5/9, 2)


def psi2kpa(x):
    return round(x * 6.895, 4)


def slug2kg(x):
    return round(x * 14.59390, 3)


def pound2kg(x):
    return round(x * 0.45359237, 3)


json_convert_to_metrics = {
    'CITP_VelRelEarth_Mag': mile2km,
    'CITP_DistMoon_Mag': mile2km,
    'CITP_DistEarth_Mag': mile2km,
    'CITP_CabTemp_Zone1': fahrenheit2celsius,
    'CITP_CabTemp_Zone2': fahrenheit2celsius,
    'CITP_CabTemp_Zone3': fahrenheit2celsius,
    'CITP_CabTemp_Avg': fahrenheit2celsius,
    'CITP_ExtTemp_Wing_1': fahrenheit2celsius,
    'CITP_ExtTemp_Wing_2': fahrenheit2celsius,
    'CITP_ExtTemp_Wing_3': fahrenheit2celsius,
    'CITP_ExtTemp_Wing_4': fahrenheit2celsius,
    'CITP_CabPress': psi2kpa,

    'CITP_ServiceFuelRemain': slug2kg,
    'CITP_CrewFuelRemain': pound2kg,
    'CITP_TotalFuelRemain': pound2kg,
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
        csv_writer = csv.DictWriter(f, fieldnames=[
                                    time_column, *fieldnames], delimiter=';', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writeheader()
        csv_writer.writerows(sorted(rows, key=lambda x: x[time_column]))


def get_timestamp(f):
    return int(Path(f).stem)


src_directory, output_file_json, output_file_csv = sys.argv[1:]


files = map(lambda f: (f, get_timestamp(f)), glob(src_directory + '/*.json'))
files = sorted(files, key=lambda x: x[1])

json_timestamps = list(map(lambda x: x[1], files))
json_values = defaultdict(lambda: [None]*len(json_timestamps))
json_last_time = max(json_timestamps)

rows = []
for index, (f, _) in enumerate(files):
    data = load_json(f)
    row = {time_column: json_timestamps[index]}

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
            if readable_name in json_convert_to_metrics:
                value = json_convert_to_metrics[readable_name](value)

        json_values[readable_name][index] = value

    if row:
        rows.append(row)

groups = defaultdict(list)
for k, v in json_fields_whitelist.items():
    if v is None:
        groups[k] = [k]
    else:
        groups[v].append(k)

save_json(output_file_json, {'last_time': json_last_time,  'groups': groups,
          'groups_desc': json_group_description, 'timestamps': json_timestamps, 'values': json_values})
save_csv_auto_fields(output_file_csv, rows)

print('work done, last update:', round(
    (time.time()-json_last_time) / 60 / 60, 2), 'hour ago', json_last_time)
