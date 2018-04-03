#!/usr/bin/env python3

import requests
import json
import sys
import os
import logging
import argparse

USER = os.environ["GISSMOUSER"]
PASS = os.environ["GISSMOPASS"]
HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json'
}


PATH_API = 'https://gissmo-test.u-strasbg.fr/api/v2/'
PLACE_TYPES = requests.get("https://gissmo-test.u-strasbg.fr/api/v2/place_types/", auth=(USER,PASS)).json()
CHANNELS_CODE = requests.get("https://gissmo-test.u-strasbg.fr/api/v2/channelcodes/", auth=(USER,PASS)).json()
DATATYPES = requests.get("https://gissmo-test.u-strasbg.fr/api/v2/datatypes/", auth=(USER,PASS)).json()
USER_API = "https://gissmo-test.u-strasbg.fr/api/v2/users/1/"
USER_API_ID = 1

"""ALL_STATION = requests.get(PATH_API+"stations", )
ALL_PLACES = requests.get(PATH_API+"places", )
CHANNELS_CODE = requests.get(PATH_API+"channelcodes")
NETWORKS_CODE = requests.get(PATH_API+"networks")
MODELS = requests.get(PATH_API+"/models/?name="CMG-40T)
AGENCIES = requests.get(PATH_API+"agencies")
SATATES = requests.get(PATH_API+"equipment_states")
EQUIPMENTS = requests.get(PATH_API+"equipments")
EQUIPMENTS_CONFIG = requests.get(PATH_API+'equipment_configurations')"""


def post_request(data, entity):
    rs = requests.post(PATH_API+entity+"/", auth=(USER,PASS),data = json.dumps(data) ,headers=HEADERS)

    if(rs.status_code == 201):
        print (f"----------------------------------------")
        print (f"         {entity} added                 ")
        print (f"----------------------------------------")
        if 'id' in rs.json():
            return str(rs.json()['id'])
    else :

        print(f"-----------------------------------------")
        print(f"    Add {entity} return ", str(rs.status_code))
        print(f"-----------------------------------------")
        print (rs.text)
        sys.exit(-1)


def get_link_model( model_name):
    # filtre ti get id of channel 
    model_obj = requests.get(PATH_API+"models/?name="+model_name, auth=(USER,PASS))
    if model_obj.json() == []:
        print (") model "+model_name+" doesn't exist" )
        exit(-1)
    return PATH_API+'models/'+str(model_obj.json()[0]['id'])+'/'

def get_link_agencie(agenci_name):

    agenci_obj = requests.get(PATH_API+"agencies/?name="+agenci_name, auth=(USER,PASS),headers=HEADERS)
    print(agenci_obj.json())
    if agenci_obj.json() == []:
        print (" agencie  "+agenci_name+" doesn't exist" )
        exit(-1)
    return PATH_API+'agencies/'+str(agenci_obj.json()[0]['id'])+'/'


def get_link_station(name):
    station_obj = requests.get(PATH_API+"stations/?code="+name,auth=(USER,PASS))
    if station_obj.json() == []:
        print (" Station  "+name+" doesn't exist" )
        exit(-1)
    return PATH_API+'stations/'+str(station_obj.json()[0]['id'])+'/'

def get_link_place(id): 
    return PATH_API+'places/'+id+'/'

def get_link_station(id): #to do pas de filtres
    return PATH_API+'stations/'+id+'/'


def get_link_place_type(name):
    types_obj = list(filter( lambda x : x['name'] ==name , PLACE_TYPES))
    if len(types_obj) == 0:
        print (" Type Place  "+name+" doesn't exist" )
        exit(-1)
    else:
        return PATH_API+'place_types/'+str(types_obj[0]['id'])+'/'

def get_link_network(name):

    network_obj = requests.get(PATH_API+"networks/?code="+name,auth=(USER,PASS))
    if network_obj.json() == []:
        print (" Network "+name+" doesn't exist" )
        exit(-1)
    return PATH_API+'networks/'+str(network_obj.json()[0]['id'])+'/'

def get_link_channel_type(name):
    type_obj = list(filter( lambda x : x['name'] ==name, CHANNELS_CODE))
    if len(type_obj) == 0:
        print (" Type channel  "+name+" doesn't exist" )
        exit(-1)
    else:
        return PATH_API+'channelcodes/'+str(type_obj[0]['id'])+'/'

def get_link_datatypes(name):
    type_obj = list(filter( lambda x : x['name'] ==name, DATATYPES))

    if len(type_obj) == 0:
        print (" Datatypes channel  "+name+" doesn't exist" )
        exit(-1)
    else:
        return PATH_API+'datatypes/'+str(type_obj[0]['id'])+'/'


def exist_equipment(name):
    EQUIPMENTS = requests.get(PATH_API+"equipments", auth=(USER,PASS)).json()
    eqp_obj = list(filter( lambda x : x['name'] == name, EQUIPMENTS))
    print(eqp_obj)
    if len(eqp_obj) == 0:
        return False, -1
    else:
        return True, str(eqp_obj[0]['id'])

# tets statique input 
# test models equipements 
# add station
# test agencie if exist alse create it 
# add place + add argument station in object
# 


if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Add Station in GISSMO')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--FILE", help='Json file  ')

    path = parser.parse_args().FILE
    if not os.path.exists(path):
        print(" Le fichier n'existe pas ")

    try:
        fl = open(path)
        data = json.load(fl)[0]

    except Exception as e:
        print(" Erreur dans le fichier Json")
        exit(-1)

    py_station = data['station']

    id_station = post_request(py_station, "stations")
    station = get_link_station(id_station)

    py_place = data['place']
    py_place['type'] = get_link_place_type(py_place['type'])
    list_agencie = py_place['agencies'] 
    py_place['agencies'] = []
    for agn in list_agencie:
        py_place['agencies'].append(get_link_agencie(agn))
    py_place['station'] = station


    # add place
    id_place = post_request(py_place, "places")

    # add Periodes
    place = get_link_place(id_place)

    periodes = data['periodes']

    for period  in  periodes:
        start = period['start']
        end = period['end']
        span = json.dumps({"upper": end, "lower": start, "bounds": "[)" })
        id_configurations = []
        equipments = period['equipments']

        for equipment in equipments:
            # add equipments
            exist, id_equipmnt = exist_equipment(equipment['name'])
            print(equipment, exist, id_equipmnt)
            if not exist :
                equipment['destination'] = place
                equipment['model'] = get_link_model(equipment['model'])
                equipment['owner'] = get_link_agencie(equipment['owner'])
                equipment['user'] = USER_API
                print("\n\n", equipment, "\n",start, end)
                id_equipmnt = post_request(equipment, "equipments")


            # add locations
            location = {}
            link_to_equi = PATH_API+"equipments/"+id_equipmnt+'/'
            logging.debug('equipment {equipment}')
            location['equipment'] = link_to_equi
            location['place'] = place
            location['start'] = start
            location['user'] = USER_API
            logging.debug(f'location {location}')
            print (location)
            post_request(location, "locations")

            # add configurations
            configurations = equipment['configuration']
            if len(configurations) !=0 :
                for conf in configurations:
                    conf['equipment'] = link_to_equi
                    conf['start'] = start
                    conf['user'] = USER_API
                    id_config = post_request(conf, "equipment_configurations")
                    id_configurations.append(id_config)
                    

        #add channels
        channels = period['channels']

        id_channels  = []
        for channel in channels:

            channel['network'] = get_link_network(channel['network'])
            channel['code'] = get_link_channel_type(channel['code'])
            channel['station'] = station
            channel['span'] = span
            channel_configs =  channel['configuration']
            channel['configuration'] = []

            datatypes = []
            for dt in channel['datatypes']:
                datatypes.append(get_link_datatypes(dt))
            channel['datatypes'] = datatypes
            id_channel = post_request(channel,'channels')

            for conf in channel_configs:
                conf['channel'] = id_channel
                conf['user'] = USER_API_ID
                id_conf_ch = post_request(conf,'channel_configurations')

            id_channels.append(id_channel)


        # add channel_parameters
        for id_ch in id_channels:
            pyl = {}
            pyl['channel'] = id_ch
            for conf in id_configurations:
                pyl['configuration'] = PATH_API+"equipment_configurations/"+conf+"/"
            post_request(pyl, "channel_parameters")





        



