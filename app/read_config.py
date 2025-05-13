import json


def read_config(api_key: str, conf_path) -> dict:
    with open(conf_path, 'r') as config_jf:
        json_cnf = json.loads(config_jf.read())
        key = json_cnf['api_key']

    if len(key) > 0:
        print(f'[+] API Key Found...\n')
        return {'User-Agent': 'pwnedOrNot', 'hibp-api-key': key}

    if len(api_key) < 1:
        print("No API key found in config.json, please provide one.")
        exit(0)

    with open(conf_path, 'w') as key_jf:
        key_dict = {'api_key': api_key}
        json_data = json.dumps(key_dict)
        key_jf.write(json_data)
    print(f'[+] Saved API Key in : {conf_path}\n')

    return {'User-Agent': 'pwnedOrNot', 'hibp-api-key': api_key}
