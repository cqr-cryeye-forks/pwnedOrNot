import json

import requests
from html2text import html2text

from app.constants import response_codes


def domain_check(useragent, check_domain):
    print(f'[+] Domain Name : {check_domain}', end='')
    rqst = requests.get(
        f'https://haveibeenpwned.com/api/v3/breaches?domain={check_domain}',
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
                    for item in simple_out:
                        print(f'\n')
                        print(f'[+] Breach      : {str(item["Title"])}\n')
                        print(f'[+] Domain      : {str(item["Domain"])}\n')
                        print(f'[+] Date        : {str(item["BreachDate"])}\n')
                        print(f'[+] Pwn Count   : {str(item["PwnCount"])}\n')
                        print(f'[+] Fabricated  : {str(item["IsFabricated"])}\n')
                        print(f'[+] Verified    : {str(item["IsVerified"])}\n')
                        print(f'[+] Retired     : {str(item["IsRetired"])}\n')
                        print(f'[+] Spam        : {str(item["IsSpamList"])}\n')
                        print(f'[+] Data Types  : {str(item["DataClasses"])}')
                        print(f'[+] Description : {html2text(str(item["Description"]))}')
                else:
                    print(f' [ Not Breached ]')
            elif sc == 404:
                print(f' [ Not Breached ]')
            else:
                print(f'\n[-] Status {code} : {desc}')
