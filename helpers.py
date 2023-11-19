import certifi
import urllib3
import configparser
import argparse
import sys

def parse_cli_inputs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_keys_path', type=str, required=True)
    parser.add_argument('--config_path', type=str, required=True)
    parser.add_argument('--print_config', action='store_true')
    parser.add_argument('--task', type=str, required=True)
    args = parser.parse_args()
    print(args)
    return args


def generate_configs():
    args = parse_cli_inputs()
    api_keys_path = args.api_keys_path
    config_path = args.config_path
    
    config = configparser.ConfigParser()
    print(config)
    config.set("task",args.task)
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
        print(data)
        req = self.pool_manager.request("POST", 
                                  self.url, 
                                  body=bytes(data.encode("utf-8")), 
                                  headers=self.headers
                                  )
        response = req.json()
        return response


def get_raw_query(query_path):
    """Load .gql file as plaintext"""
    with open(query_path, "r") as file:
        query = file.read()
    return query


def generate_query(task, query_path):

    query = generate_query(query_path=query_path)
    print(query)
    response = http.post_request(query.replace("{{","{"))
    print(response)
    query = get_raw_query(query_path)
    ## add arguments



def generate_stop_mappings():
    query_path = config.get("PATHS", f"path_to_{task}_query")

def get_all_stops_data():
    return

def save_all_stops_data(output_path):
    return

class Stop():
    def __init__(self):
        self.name = None
        self.gtfsId = None
        self.name = None
        self.code = None


# def send_post_request(cfg, query_path, extra_args=None):



#     data = """

#     """
#     req = http.request("POST", url, body=bytes(data.encode("utf-8")), headers=hdr)
#     return req


# class Stop:
#     def __init__(self):
#         self.name = None
#         self.



# from datetime import datetime

# now = datetime.now()
# current_time = now.strftime("%Y-%m-%d %H:%M:%S")
# print("Current Time =", current_time)

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