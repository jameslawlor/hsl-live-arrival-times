from helpers import HTTPRequestManager, generate_configs

def main():

    config = generate_configs()
    print(config)
#     http = HTTPRequestManager()
#     http.configure(
#         config.get("DIGITRANSIT","API_ENDPOINT_URL"),
#         api_keys.get("DIGITRANSIT","PRIMARY_KEY")
#         )

#     if task == "generate_stop_mappings":
#         generate_stop_mappings(config)
#     elif task == "get_live_departures":
#         get_live_departures(config)
#     else:
#         Exception(f"Task {task} not supported!")

# if __name__ == "__main__":
#     main()