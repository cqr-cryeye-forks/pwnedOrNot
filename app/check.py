import json
import pathlib
import time

import requests

from app.dump import dump
from app.constants import response_codes


def check(useragent, target: str, output_json: pathlib.Path, nodumps):
    print(f'[+] Checking Breach status for {target}', end='')
    rqst = requests.get(
        f'https://haveibeenpwned.com/api/v3/breachedaccount/{target}',
        headers=useragent,
        params={'truncateResponse': 'false'},
        timeout=10
    )
    sc = rqst.status_code

    for code, desc in response_codes.items():
        if sc == code:
            if sc == 200:
                print(f' [ pwned ]')
                json_out = rqst.content.decode('utf-8', 'ignore')
                simple_out = json.loads(json_out)

                print(f'\n[+] Total Breaches : {len(simple_out)}')

                for item in simple_out:
                    print(f'\n')
                    print(f'[+] Breach      : {str(item["Title"])} \n')
                    print(f'[+] Domain      : {str(item["Domain"])} \n')
                    print(f'[+] Date        : {str(item["BreachDate"])} \n')
                    print(f'[+] BreachedInfo: {str(item["DataClasses"])} \n')
                    print(f'[+] Fabricated  : {str(item["IsFabricated"])} \n')
                    print(f'[+] Verified    : {str(item["IsVerified"])} \n')
                    print(f'[+] Retired     : {str(item["IsRetired"])} \n')
                    print(f'[+] Spam        : {str(item["IsSpamList"])}')
                print(f'-----\n')

                if nodumps != True:
                    dump(useragent, target)
                if output_json is not None:
                    with open(output_json, 'a') as jf:
                        jf.write('' + target + '\n')

            elif sc == 404:
                print(f' [ not pwned ]')
                if nodumps is False:
                    dump(useragent, target)

            elif sc == 429:
                retry_sleep = float(rqst.headers['Retry-After'])
                print(f'[ retry in {retry_sleep}s]')
                time.sleep(retry_sleep)
                check(useragent, target, output_json, nodumps)

            else:
                print(f'\n\n[-] Status {code} : {desc}')
