import json
import re
import time

import requests


def dump(useragent, target: str) -> None:
    dumplist = []
    print(f'\n[+] Looking for Dumps...', end='')
    rqst = requests.get(
        f'https://haveibeenpwned.com/api/v3/pasteaccount/{target}',
        headers=useragent,
        timeout=10
    )
    sc = rqst.status_code

    if sc == 429:
        retry_sleep = float(rqst.headers['Retry-After'])
        print(f'[ retry in {retry_sleep}s]')
        time.sleep(retry_sleep)
        dump(useragent, target)
    elif sc != 200:
        print(f' [ No Dumps Found ]')
    else:
        print(f' [ Dumps Found ]\n')
        json_out = rqst.content.decode('utf-8', 'ignore')
        simple_out = json.loads(json_out)

        for item in simple_out:
            if (item['Source']) == 'Pastebin':
                link = item['Id']
                try:
                    url = 'https://www.pastebin.com/raw/{}'.format(link)
                    page = requests.get(url, timeout=10)
                    sc = page.status_code
                    if sc == 200:
                        dumplist.append(url)
                        print(f'[+] Dumps Found : {len(dumplist)}', end='\r')
                    if len(dumplist) == 0:
                        print(f'[-] Dumps are not Accessible...')
                except requests.exceptions.ConnectionError:
                    pass
            elif (item['Source']) == 'AdHocUrl':
                url = item['Id']
                try:
                    page = requests.get(url, timeout=10)
                    sc = page.status_code
                    if sc == 200:
                        dumplist.append(url)
                        print(f'[+] Dumps Found : {len(dumplist)}', end='\r')
                    if len(dumplist) == 0:
                        print(f'[-] Dumps are not Accessible...')
                except Exception:
                    pass

    if len(dumplist) != 0:
        print(f'\n\n[+] Passwords : \n')
        for entry in dumplist:
            time.sleep(1.1)
            try:
                page = requests.get(entry, timeout=10)
                dict = page.content.decode('utf-8', 'ignore')
                passwd = re.search('{}:(\w+)'.format(target), dict)
                if passwd:
                    print(f'[+] {passwd.group(1)}')
                elif not passwd:
                    for line in dict.splitlines():
                        passwd = re.search('(.*{}.*)'.format(target), line)
                        if passwd:
                            print(f'[+] {passwd.group(0)}')
            except requests.exceptions.ConnectionError:
                pass
