import CloudFlare #pip install cloudflare
import io
import json
import os
import pathlib
import pprint
import time
import traceback

#https://github.com/cloudflare/python-cloudflare/tree/master/examples
#https://github.com/cloudflare/python-cloudflare/blob/master/examples/example_page_rules.py
#https://github.com/cloudflare/python-cloudflare/blob/master/examples/example_list_api_from_web.py

#Files are automatically saved at the end of io.open,
#but you can use this function to save them on demand,
#such as during each iteration of a long loop
def save_file(file):
    file.flush()
    os.fsync(file.fileno())

def get_cf_object(token, raw):
    cf_object = CloudFlare.CloudFlare(token=token, raw=raw)
    return cf_object

def get_cf_zones(cf_object):
    return cf_object.zones.get(params = {'per_page': 1000})

#Add more data to the given Cloudflare zone dict like its DNS settings and page rules
def fetch_zone_data(cf_object, zone):
    zone_id = zone['id']
    zone_name = zone['name']

    #global cf_debug
    #cf_debug = cf_object
    #print(dir(cf_object.zones))
    #print(dir(cf_object.zones.email.routing))
    
    zone['dns_records'] = cf_object.zones.dns_records.get(zone_id)
    zone['email_routing'] = cf_object.zones.email.routing.get(zone_id)
    zone['filters'] = cf_object.zones.filters.get(zone_id)
    zone['firewall_rules'] = cf_object.zones.firewall.rules.get(zone_id)
    zone['pagerules'] = cf_object.zones.pagerules.get(zone_id)
    zone['settings'] = cf_object.zones.settings.get(zone_id)

def read_config(file_path):
    print('Reading query config file...')
    with open(file_path, 'r') as file:
        query_config = json.load(file)
    print('Successfully read query config file.')
    return query_config

def main():
    config = read_config('config.json')

    token = config['token']
    
    main_folder_path = 'cloudflare-sites-' + time.strftime("%b-%d-%Y-%H%M%S").lower()
    
    cf_object = get_cf_object(token, True)
    zones = get_cf_zones(cf_object)

    for zone in zones['result']:
        zone_id = zone['id']
        zone_name = zone['name']

        print("{} ({})".format(zone_name, zone_id))

        print("\tSuccessfully retrieved preliminary zone data.")
        print("\tFetching additional zone data...")
        
        fetch_zone_data(cf_object, zone)

        print("\tSuccessfully retrieved additional zone data.")
        print("\tWriting zone data to file...")

        folder_path = main_folder_path + '/' + zone_name
        file_name = 'test-' + time.strftime("%b-%d-%Y-%H%M%S").lower() + '.json'
        file_path = folder_path + '/' + file_name

        pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)

        with io.open(file_path, 'a', encoding="utf-8-sig", newline='\n') as zone_file:
            zone_file.write(json.dumps(zone, indent=4))
            save_file(zone_file)

        print("\tSuccessfully wrote zone data to file.")

if (__name__ == "__main__"):
    try:
        os.system('title {}'.format('CF backup maker'))
        main()
        input("\nThe script finished successfully. Press the Enter key to exit.")
    except Exception as ex:
        print('The script crashed at ' + time.ctime() + ' due to an unhandled {} exception.'.format(type(ex)))
        print('Full exception text: ' + str(ex))
        print(traceback.format_exc())
        input("\nPress the Enter key to exit.")
