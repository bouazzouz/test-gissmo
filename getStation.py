#!/usr/bin/env python3

import requests
import json
import argparse
import os
from datetime import datetime



USER = os.environ["GISSMOUSER"]
PASS = os.environ["GISSMOPASS"]

HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json'
}


PATH_API = "https://gissmo-test.u-strasbg.fr/api/v2/"
#equipments = requests.get(PATH_API+"equipments/")
#channels = requests.get(PATH_API+"channels/")
CHANNEL_PARAMETRS = requests.get(PATH_API+"channel_parameters/", auth=(USER,PASS)).json()

def get_equipments(id_channel):

    equi_conf_list = list(filter( lambda x : x['channel'] == id_channel ,CHANNEL_PARAMETRS))
    equipments = []
    for equi_conf in equi_conf_list:
        equipment_link = requests.get(equi_conf['configuration'], auth=(USER,PASS)).json()['equipment']
        equipment = requests.get(equipment_link, auth=(USER, PASS)).json()
        equipments.append(equipment)

    return equipments

def get_locations(id_place):

    locations = requests.get(PATH_API+"locations/?place="+str(id_place),auth=(USER,PASS)).json()
    return locations

def get_info(json_station):
    """  """
    row = {}
    row['station'] = json_station['code']
    row['latitude'] = json_station['latitude']
    row['longitude'] = json_station['longitude']
    row['elevation'] = json_station['elevation']
    row['site'] = json_station['description']

    # get channels
    channels_stations = []


    for c in json_station['channels']:
        obj_channel = requests.get(c, auth=(USER,PASS)).json()
        channel = {}
        channel['code'] = requests.get(obj_channel['code'],auth=(USER,PASS)).json()['name']
        channel['frequency'] = obj_channel['sample_rate']
        channel['start'] = json.loads(obj_channel['span'])['lower']
        channel['end'] = json.loads(obj_channel['span'])['upper']
        equipments_list = get_equipments(obj_channel['id'])
        equipments = []
        for equip in equipments_list:
            equipment = {}
            equipment['Numerp de serie '] = equip['name']
            model = requests.get(equip['model'], auth=(USER,PASS)).json()
            equipment[' Modele'] = model['name']
            equipment[' Type '] = requests.get(model['type'], auth=(USER,PASS)).json()['name']
            configurations = equip['configurations']
            equipment['configurations'] = []
            for conf in configurations:
                conf_eq={}
                equi_conf = requests.get(conf,auth=(USER,PASS)).json()
                conf_eq[equi_conf['parameter']] = equi_conf['value']
                if (channel['end'] == None) :
                    if (datetime.strptime(equi_conf['start'],'%Y-%m-%dT%H:%M:%S') >=datetime.strptime(channel['start'],'%Y-%m-%dT%H:%M:%S')):
                        equipment['configurations'].append(conf_eq)

                elif (datetime.strptime(equi_conf['start'],'%Y-%m-%dT%H:%M:%S') <= datetime.strptime(channel['end'],'%Y-%m-%dT%H:%M:%S')
                    and datetime.strptime(equi_conf['start'],'%Y-%m-%dT%H:%M:%S')>= datetime.strptime(channel['start'],'%Y-%m-%dT%H:%M:%S')):
                    equipment['configurations'].append(conf_eq)

            equipments.append(equipment)

        channel['equipments'] = equipments
        channels_stations.append(channel)

    
    # get equipments


    row['channels'] = channels_stations

    return (row)
  

def get_info2(json_station):
    """ with start"""
    row = {}
    row['station'] = json_station['code']
    row['latitude'] = json_station['latitude']
    row['longitude'] = json_station['longitude']
    row['elevation'] = json_station['elevation']
    row['site'] = json_station['description']
    id_place = json_station['places'][0]['id']

    # get channels
    channels_stations = []


    for c in json_station['channels']:
        obj_channel = requests.get(c, auth=(USER,PASS)).json()
        channel = {}
        channel['code'] = requests.get(obj_channel['code'],auth=(USER,PASS)).json()['name']
        channel['frequency'] = obj_channel['sample_rate']
        channel['start'] = json.loads(obj_channel['span'])['lower']
        channel['end'] = json.loads(obj_channel['span'])['upper']
        equipments = []
        locations = get_locations(id_place)
        for loc in locations:
            if(loc['start'] == channel['start']):
                equip_obj = requests.get(loc['equipment'],auth=(USER,PASS)).json()
                equipment = {}
                equipment['Numerp de serie '] = equip_obj['name']
                model = requests.get(equip_obj['model'], auth=(USER,PASS)).json()
                equipment[' Modele'] = model['name']
                equipment[' Type '] = requests.get(model['type'], auth=(USER,PASS)).json()['name']
                configurations = equip_obj['configurations']
                equipment['configurations'] = []
                for conf in configurations:
                    conf_eq={}
                    equi_conf = requests.get(conf,auth=(USER,PASS)).json()
                    conf_eq[equi_conf['parameter']] = equi_conf['value']
                    if (channel['end'] == None) :
                        if (datetime.strptime(equi_conf['start'],'%Y-%m-%dT%H:%M:%S') >=datetime.strptime(channel['start'],'%Y-%m-%dT%H:%M:%S')):
                            equipment['configurations'].append(conf_eq)
                    elif (datetime.strptime(equi_conf['start'],'%Y-%m-%dT%H:%M:%S') <= datetime.strptime(channel['end'],'%Y-%m-%dT%H:%M:%S')
                        and datetime.strptime(equi_conf['start'],'%Y-%m-%dT%H:%M:%S')>= datetime.strptime(channel['start'],'%Y-%m-%dT%H:%M:%S')):
                            equipment['configurations'].append(conf_eq)

                equipments.append(equipment)

        channel['equipments'] = equipments
        channels_stations.append(channel)

    
    # get equipments


    row['channels'] = channels_stations

    return (row)
  



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Test Gissmo')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--STATION", help='get specific station ')
    group.add_argument("-a", "--ALL", action="store_true",
                       help=' get All stations')
    # retrieve All stations
    rs = requests.get(PATH_API+"stations" , auth=(USER,PASS))

    args = parser.parse_args()
    rows = []

    if args.ALL:
        for r in rs.json():
            rows.append(get_row(r))
    else:
        station_obj = requests.get("https://gissmo-test.u-strasbg.fr/api/v2/stations/?code="+args.STATION, auth=(USER,PASS)).json()
        if station_obj == []:
            print(" Station doesn't exist ")
            exit(-1)
        rows.append(get_info2(station_obj[0]))
    

    for r in rows:
        print(json.dumps(r, indent=4))
