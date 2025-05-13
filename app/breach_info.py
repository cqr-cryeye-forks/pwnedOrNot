import json
import time

import requests

from app.constants import response_codes


def breach_info(useragent, breach_name):
    print(f'[+] Breach Name : {breach_name}', end='')
    rqst = requests.get(
        f'https://haveibeenpwned.com/api/v3/breach/{breach_name}',
        headers=useragent,
        timeout=10
    )
    sc = rqst.status_code

    for code, desc in response_codes.items():
        if sc == code:
            if sc == 200:
                json_out = rqst.content.decode('utf-8', 'ignore')
                simple_out = json.loads(json_out)
                if len(simple_out) != 0:
                    print(f' [ pwned ]')
                    print(f'\n')
                    print(f'[+] Breach      : {str(simple_out["Title"])}\n')
                    print(f'[+] Domain      : {str(simple_out["Domain"])}\n')
                    print(f'[+] Date        : {str(simple_out["BreachDate"])}\n')
                    print(f'[+] Pwn Count   : {str(simple_out["PwnCount"])}\n')
                    print(f'[+] Fabricated  : {str(simple_out["IsFabricated"])}\n')
                    print(f'[+] Verified    : {str(simple_out["IsVerified"])}\n')
                    print(f'[+] Retired     : {str(simple_out["IsRetired"])}\n')
                    print(f'[+] Spam        : {str(simple_out["IsSpamList"])}\n')
                    print(f'[+] Data Types  : {str(simple_out["DataClasses"])}')
                else:
                    print(f' [ Not Breached ]')
            elif sc == 429:
                retry_sleep = float(rqst.headers['Retry-After'])
                print(f'[ retry in {retry_sleep}s]')
                time.sleep(retry_sleep)
                breach_info(useragent, breach_name)
            elif sc == 404:
                print(f' [ Not Breached ]')
            else:
                print(f'\n[-] Status {code} : {desc}')
