import certifi
import urllib3
from configparser import ConfigParser, ExtendedInterpolation
import argparse
import sys
import json
import os
from datetime import datetime

def parse_cli_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_keys_path', type=str, required=True)
    parser.add_argument('--config_path', type=str, required=True)
    parser.add_argument('--print_config', action='store_true')
    parser.add_argument('--task', type=str, required=True)
    args = parser.parse_args()
    return args


def generate_configs():
    args = parse_cli_inputs()
    api_keys_path = args.api_keys_path
    config_path = args.config_path
    
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config["DEFAULT"] = {"task": args.task}
    config.read([config_path,api_keys_path])

    if args.print_config:
        print("Running with config:\n")
        config.write(sys.stdout)

    return config


class HTTPRequestManager():
    def __init__(self):
        self.url = None
        self.headers = None
        self.pool_manager = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())
    
    def configure(self, api_endpoint_url, api_key):
        self.url = api_endpoint_url
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/graphql",
            "digitransit-subscription-key": api_key,
            }
    
    def post_request(self, data):
        req = self.pool_manager.request("POST", 
                                  self.url, 
                                  body=bytes(data.encode("utf-8")), 
                                  headers=self.headers
                                  )
        return req


def do_task(config):

    task = config.get("DEFAULT","task")

    if task == "generate_stop_mappings":
        generate_and_save_stop_mappings(config)
    elif task == "get_live_departures":
        get_live_departures(config)
    else:
        raise ValueError(f"Task {task} not supported!")


def get_query(config):
    
    task = config.get("DEFAULT","task")
    query_path = config.get("PATHS", f"path_to_{task}_query")
    print()
    print(query_path)
    with open(query_path, "r") as file:
        query = file.read()

    return query

def post_query(url, api_key, query):

    http = HTTPRequestManager()
    http.configure(
        api_endpoint_url=url,
        api_key=api_key
    )
    query = query.replace("{{","{").replace("}}","}")
    print(f"Running query: \n {query}")
    return http.post_request(query)
    

def generate_and_save_stop_mappings(config):

    query = get_query(config)

    url = config.get("DIGITRANSIT","API_ENDPOINT_URL")
    api_key = config.get("DIGITRANSIT","PRIMARY_KEY")
    response = post_query(url, api_key, query)
    
    status_code = str(response.status)
    if status_code == "200":
        save_path = config.get("PATHS","path_to_stop_mappings_data")
        print(f"Query successful, writing data to {save_path}")
        data = response.json()["data"]["stops"]
        with open(save_path, 'w', encoding='utf-8-sig') as f:
            json.dump(data, f)
    else:
        raise ValueError(f"HTTP POST failed with {status_code} status code")

    return



def load_stop_mappings(path, list_of_stops_to_query):
    if not os.path.isfile(path):
        raise ValueError("Mapping file doesn't exist! Recheck the location or run task `generate_stop_mappings` to generate it")
    else:
        with open(path,encoding='utf-8-sig') as f:
            data = json.load(f)
        stop_mappings = [stop for stop in data if stop["code"] in list_of_stops_to_query]

        if len(stop_mappings) < len(list_of_stops_to_query):
            print("Warning! Not all requested stops were found.")
            available_stop_ids = [s["code"] for s in stop_mappings]
            missing_stops = [stop for stop in list_of_stops_to_query if stop not in available_stop_ids]
            print(f"Missing stops: {missing_stops}")

        if len(stop_mappings) == 0:
            raise ValueError("No input stops were found in the mapping data! Exiting")

        return stop_mappings


def parse_stops_to_query(input_from_config):
    return [_.replace(" ","") for _ in input_from_config.split(",")]

def get_live_departures(config):

    list_of_stops_to_query = parse_stops_to_query(config.get("STOPS","stops_to_query"))
    mappings_path = config.get("PATHS","path_to_stop_mappings_data")

    stop_id_mappings = load_stop_mappings(mappings_path, list_of_stops_to_query)

    stops = Stops()
    stops.init_stop_data(stop_id_mappings)

    raw_query = get_query(config)
    url = config.get("DIGITRANSIT","API_ENDPOINT_URL")
    api_key = config.get("DIGITRANSIT","PRIMARY_KEY")
    stops.get_live_stop_data(url, api_key, raw_query)
    stops.display()


    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print("Current Time =", current_time)

    # stops = create_live_departures(stops)
    
class Stops():
    def __init__(self):
        self.stops = []
    
    def add(self, new_stop):
        self.stops.append(new_stop)

    def init_stop_data(self, data):
        # Generate stop objects
        for available_stop in data:
            stop = Stop(
                name=available_stop["name"],
                gtfsId=available_stop["gtfsId"],
                code=available_stop["code"],
            )
            self.add(stop)

    def display(self):
        for s in self.stops:
            print(s)


    def get_live_stop_data(self, url, api_key, raw_query):
        for stop in self.stops:
            stop.generate_query(raw_query)
            response = post_query(url, api_key, stop.query)
            status_code = str(response.status)
            if status_code == "200":
                stop.raw_data = response.json()["data"]["stop"]["stoptimesWithoutPatterns"]



class Stop():
    def __init__(self, name, gtfsId, code):
        self.name = name
        self.gtfsId = gtfsId
        self.code = code
        self.query = None
        self.raw_data = None

    def __str__(self):
        return f"From str method of Stop: \n name: {self.name}, gtfsId: {self.gtfsId}, code: {self.code} \n raw_data: {self.raw_data} \n query: {self.query}"

    def generate_query(self, raw_query):
        self.query = raw_query.format(input_stop_id=self.gtfsId) 
    
    

# d = req.json()
# print(d)

# trains = d["data"]["stop"]["stoptimesWithoutPatterns"]
# for train in trains:
#     today_ux = train["serviceDay"]
#     arrival_time_ux = train["realtimeArrival"]
#     destination = train["headsign"]
#     t = datetime.fromtimestamp(train["serviceDay"] + train["realtimeArrival"])
#     t_str = t.strftime("%H:%M")
#     time_diff = (t - now).total_seconds()
#     time_diff_minutes = divmod(time_diff, 60)[0]
#     time_str = str(int(time_diff_minutes))
#     print(f"Train to {destination} is in {time_str} minutes at {t_str}")