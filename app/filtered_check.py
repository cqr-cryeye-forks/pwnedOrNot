import json
import pathlib
import time

import requests

from app.check import check
from app.dump import dump
from app.constants import response_codes


def filtered_check(useragent, target, domain, nodumps, output_json: pathlib.Path):
    print(f'\n[+] Checking Breach status for {target}', end='')
    rqst = requests.get(
        f'https://haveibeenpwned.com/api/v3/breachedaccount/{target}?domain={domain}',
        headers=useragent,
        params={'truncateResponse': 'false'},
        verify=True,
        timeout=10
    )
    sc = rqst.status_code

    for code, desc in response_codes.items():
        if sc == code:
            if sc == 200:
                print(f' [ pwned ]')
                json_out = rqst.content.decode('utf-8', 'ignore')
                simple_out = json.loads(json_out)

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
                if nodumps is not True:
                    dump(useragent, target)
            elif sc == 404:
                print(f' [ not pwned ]')
                if nodumps is not True:
                    dump(useragent, target)
            elif sc == 429:
                retry_sleep = float(rqst.headers['Retry-After'])
                print(f'[ retry in {retry_sleep}s]')
                time.sleep(retry_sleep)
                check(
                    useragent=useragent,
                    target=target,
                    output_json=output_json,
                    nodumps=nodumps,
                )
            else:
                print(f'\n[-] Status {code} : {desc}')
