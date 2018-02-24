import json
import yaml
from shutil import copyfile

def buildAppliancesForSocket(medalIndex, socketIndex, entries, applianceIndex):
    socketName = 'socket_'+str(socketIndex)
    socketEntries = []

    for entry in entries:
        socketEntries.append({
            'appliance': entry[socketName],
            'start': entry['timestamp']
        })

    "remove duplicates ignoring the timestamp"
    st = set()
    for entry in socketEntries:
        if socketName in entry:
            if entry[socketName] in st:
                socketEntries.remove(entry)
            st.add(entry[socketName])

    for i, entry in enumerate(socketEntries):
        if (i+2) < len(socketEntries):
            entry['end'] = socketEntries[i+1]['start']
        else:
            entry['end'] = '2017-06-30T00-00-00'

    appliances = []
    for socket in socketEntries:
        if not socket['appliance']['appliance_name'] == None:
            appliances.append({
                'type': 'appliance',
                'instance': applianceIndex,
                'meters': [((medalIndex-1)*6)+socketIndex],
                'max_power': int(socket['appliance']['power'][:-1]) if socket['appliance']['power'] else 0,
                'original_name': str(socket['appliance']['appliance_name']) + ' - ' + str(socket['appliance']['class_name']),
                'dates_active': [{ 'start': str(socket['start']), 'end': str(socket['end']) }]
            })
            applianceIndex = applianceIndex + 1

    return appliances



def buildAppliancesForMedal(medalIndex, applianceIndex):
    entries = d['MEDAL-'+str(medalIndex)]['entries']
    appliances = []

    for i in range(1, 7):
        appliances = appliances + buildAppliancesForSocket(medalIndex, i, entries, applianceIndex)

    return appliances


with open('appliance_log.json') as json_data:
    d = json.load(json_data)
    applianceIndex = 1
    appliances = []

    for i in range(1, 16):
        appliances = appliances + buildAppliancesForMedal(i, applianceIndex)

    elec_meters = {}

    medal = { 'device_model': 'Medal' }

    for i in range(1, 90):
        elec_meters[i] = medal

    yaml_data = {
        'instance': 1,
        'original_name': 'office',
        'elec_meters': elec_meters,
        'appliances': appliances
    }

    with open('dist/building1.yml', 'w') as outfile:
        yaml.dump(yaml_data, outfile, default_flow_style=False)

    copyfile('dataset.yml', 'dist/dataset.yml')
    copyfile('meter_devices.yml', 'dist/meter_devices.yml')

