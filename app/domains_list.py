import json
import pathlib

import requests

from app.constants import response_codes


def domains_list(output_json: pathlib.Path, useragent):
    domains = []
    print(f'[+] Fetching List of Breached Domains...\n')
    rqst = requests.get(
        'https://haveibeenpwned.com/api/v3/breaches',
        headers=useragent,
        timeout=10
    )
    sc = rqst.status_code

    for code, desc in response_codes.items():
        if sc == code:
            if sc == 200:
                json_out = rqst.content.decode('utf-8', 'ignore')
                simple_out = json.loads(json_out)
                with open(output_json, "w") as jf:
                    json.dump(simple_out, jf , indent=2)
                for item in simple_out:
                    domain_name = item['Domain']
                    if len(domain_name) != 0:
                        print('[+] '+ str(domain_name))
                        domains.append(domain_name)
                print(f'\n[+] Total : {len(domains)}')
            else:
                print(f'\n[-] Status {code} : {desc}')

