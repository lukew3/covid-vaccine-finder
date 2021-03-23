import json, requests, time, math, configparser


config = configparser.ConfigParser()
config.read('config.ini')


def main():
    state = config['CONFIG']['state']
    desired_distance = int(config['CONFIG']['desired_distance'])
    zip_code = config['CONFIG']['zip_code']
    refresh_time = int(config['CONFIG']['refresh_time'])
    home_coords = zip_to_coords(zip_code)
    while True:
        accepted_results = []
        r = requests.get(f'https://www.vaccinespotter.org/api/v0/states/{state}.json')
        my_dict = r.json()
        for item in my_dict["features"]:
            site_coords = item["geometry"]["coordinates"]
            try:
                dist = round(coords_distance(home_coords, site_coords) * 0.62137, 2)
                if dist <= desired_distance and item["properties"]["appointments_available"]:
                    props = item["properties"]
                    full_address = f"{props['address']}, {props['city']}, {state}"
                    location = [full_address, dist, props["url"], props["name"]]
                    accepted_results.append(location)
            except Exception as e:
                pass
        # Sort by distance
        accepted_results = sorted(accepted_results, key=lambda x: x[1])
        print_results(accepted_results)
        print("Waiting...")
        time.sleep(refresh_time)
        print("===========================================")

def coords_distance(pt1, pt2):
    lat1, lon1 = pt1 
    lat2, lon2 = pt2 
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d

def zip_to_coords(zip_code):
    r = requests.get(f'https://public.opendatasoft.com/api/records/1.0/search/?dataset=us-zip-code-latitude-and-longitude&q={zip_code}&facet=state&facet=timezone&facet=dst')
    zip_dict = r.json()
    coords = zip_dict["records"][0]["geometry"]["coordinates"]
    return coords


def print_results(results):
    if results != []:
        for result in results:
            print("------------------------------------------")
            print(f"Appointment available")
            print(f"Location: {result[3]} at {result[0]}")
            print(f"Distance: {result[1]} miles away")
            print(f"URL: {result[2]}")
    else:
        print("No appointments found")


if __name__ == '__main__':
    main()
