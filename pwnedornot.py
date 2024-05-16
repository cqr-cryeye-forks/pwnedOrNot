#!/usr/bin/env python3
import argparse
import pathlib
from typing import Final

from html2text import html2text
import os
import requests
import re
import time
import json

parse = argparse.ArgumentParser()

parse.add_argument('--email', required=False, help='Email Address You Want to Test')
# parse.add_argument('--file', required=False, help='Load a File with Multiple Email Addresses')
parse.add_argument('--output', required=False, help='Output file for pawned mail addresses')
parse.add_argument('--domain', required=False, help='Filter Results by Domain Name')
parse.add_argument('--breach', required=False, help='Get Info about breach')
parse.add_argument('--nodumps', required=False, action='store_true', help='Only Check Breach Info and Skip Password Dumps')
parse.add_argument('--list', required=False, action='store_true', help='Get List of all pwned Domains')
parse.add_argument('--check', required=False, help='Check if your Domain is pwned')

args = parse.parse_args()

# --email example@gmail.com --list --output data.json

target = args.email
output = args.output

domain = args.domain
breach_name = args.breach
nodumps = args.nodumps
list_domain = args.list
check_domain = args.check

MAIN_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent
output_json: Final[pathlib.Path] = MAIN_DIR / output


R = '\033[31m'  # red
G = '\033[32m'  # green
C = '\033[36m'  # cyan
W = '\033[0m'  # white
Y = '\033[33m'  # yellow

os.system("color")

conf_path = MAIN_DIR / 'config.json'

response_codes = {
    200: "OK",
    400: "Bad request — the account does not comply with an acceptable format (i.e. it's an empty string)",
    401: "Unauthorised — either no API key was provided or it wasn't valid",
    403: "Forbidden — no user agent has been specified in the request",
    404: "Not Pwned",
    429: "Too many requests — the rate limit has been exceeded",
    503: "Service unavailable — usually returned by Cloudflare if the underlying service is not available",
}


def read_config():
    global key, useragent
    try:
        with open(conf_path, 'r') as config_jf:
            json_cnf = json.loads(config_jf.read())
            key = json_cnf['api_key']
    except Exception as e:
        print(f'{R}[-] {C}API Key Not Found...{W}\n')
        print(f'{G}[+] {C}Get your API Key : {W}https://haveibeenpwned.com/API/Key \n')
        enter_key = input(f'{G}[+]' + C + ' Enter your API Key : ' + W)
        enter_key = enter_key.strip()

        with open(conf_path, 'w') as key_jf:
            key_dict = {'api_key': enter_key}
            json_data = json.dumps(key_dict)
            key_jf.write(json_data)
        print(f'{G}[+] {C}Saved API Key in : {W}{conf_path}\n')

    if len(key) > 0:
        print(f'{G}[+] {C}API Key Found...{W}\n')
        useragent = {'User-Agent': 'pwnedOrNot', 'hibp-api-key': key}


def main():
    global target, start
    start = time.time()

    read_config()

    if list_domain is True:
        domains_list()
    elif check_domain:
        domain_check()
    elif breach_name:
        breach_info()
    elif target is not None and domain is not None:
        filtered_check()
    elif target is not None and domain is None:
        check()
    else:
        print(f'{R}[-] {C}Error : {W}Atleast 1 Argument is Required, Try : {G}python3 pwnedornot.py -h{W}')
        exit()


def check():
    print(f'{G}[+] {C}Checking Breach status for {W}{target}', end='')
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
                print(f' {G}[ pwned ]{W}')
                json_out = rqst.content.decode('utf-8', 'ignore')
                simple_out = json.loads(json_out)
                print(f'\n{G}[+] {C}Total Breaches : {W}{len(simple_out)}')
                for item in simple_out:
                    print(f'\n')
                    print(f'{G}[+] {C}Breach      : {W}{str(item["Title"])} \n')
                    print(f'{G}[+] {C}Domain      : {W}{str(item["Domain"])} \n')
                    print(f'{G}[+] {C}Date        : {W}{str(item["BreachDate"])} \n')
                    print(f'{G}[+] {C}BreachedInfo: {W}{str(item["DataClasses"])} \n')
                    print(f'{G}[+] {C}Fabricated  : {W}{str(item["IsFabricated"])} \n')
                    print(f'{G}[+] {C}Verified    : {W}{str(item["IsVerified"])} \n')
                    print(f'{G}[+] {C}Retired     : {W}{str(item["IsRetired"])} \n')
                    print(f'{G}[+] {C}Spam        : {W}{str(item["IsSpamList"])}')
                print(f'-----\n')
                if nodumps != True:
                    dump()
                if output_json is not None:
                    with open(output_json, 'a') as jf:
                        jf.write('' + target + '\n')
            elif sc == 404:
                print(f' {R}[ not pwned ]{W}')
                if nodumps is False:
                    dump()
            elif sc == 429:
                retry_sleep = float(rqst.headers['Retry-After'])
                print(f' {Y}[ retry in {retry_sleep}s]{W}')
                time.sleep(retry_sleep)
                check()
            else:
                print(f'\n\n{R}[-] {C}Status {code} : {W}{desc}')


def filtered_check():
    print(f'\n{G}[+] {C}Checking Breach status for {W}{target}', end='')
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
                print(f' {G}[ pwned ]{W}')
                json_out = rqst.content.decode('utf-8', 'ignore')
                simple_out = json.loads(json_out)

                for item in simple_out:
                    print(f'\n')
                    print(f'{G}[+] {C}Breach      : {W}{str(item["Title"])} \n')
                    print(f'{G}[+] {C}Domain      : {W}{str(item["Domain"])} \n')
                    print(f'{G}[+] {C}Date        : {W}{str(item["BreachDate"])} \n')
                    print(f'{G}[+] {C}BreachedInfo: {W}{str(item["DataClasses"])} \n')
                    print(f'{G}[+] {C}Fabricated  : {W}{str(item["IsFabricated"])} \n')
                    print(f'{G}[+] {C}Verified    : {W}{str(item["IsVerified"])} \n')
                    print(f'{G}[+] {C}Retired     : {W}{str(item["IsRetired"])} \n')
                    print(f'{G}[+] {C}Spam        : {W}{str(item["IsSpamList"])}')
                if nodumps is not True:
                    dump()
            elif sc == 404:
                print(f' {R}[ not pwned ]{W}')
                if nodumps is not True:
                    dump()
            elif sc == 429:
                retry_sleep = float(rqst.headers['Retry-After'])
                print(f' {Y}[ retry in {retry_sleep}s]{W}')
                time.sleep(retry_sleep)
                check()
            else:
                print(f'\n{R}[-] {C}Status {code} : {W}{desc}')


def dump():
    dumplist = []
    print(f'\n{G}[+] {C}Looking for Dumps...{W}', end='')
    rqst = requests.get(
        f'https://haveibeenpwned.com/api/v3/pasteaccount/{target}',
        headers=useragent,
        timeout=10
    )
    sc = rqst.status_code

    if sc == 429:
        retry_sleep = float(rqst.headers['Retry-After'])
        print(f' {Y}[ retry in {retry_sleep}s]{W}')
        time.sleep(retry_sleep)
        dump()
    elif sc != 200:
        print(f' {R}[ No Dumps Found ]{W}')
    else:
        print(f' {G}[ Dumps Found ]{W}\n')
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
                        print(f'{G}[+] {C}Dumps Found : {W}{len(dumplist)}', end='\r')
                    if len(dumplist) == 0:
                        print(f'{R}[-] {C}Dumps are not Accessible...{W}')
                except requests.exceptions.ConnectionError:
                    pass
            elif (item['Source']) == 'AdHocUrl':
                url = item['Id']
                try:
                    page = requests.get(url, timeout=10)
                    sc = page.status_code
                    if sc == 200:
                        dumplist.append(url)
                        print(f'{G}[+] {C}Dumps Found : {W}{len(dumplist)}', end='\r')
                    if len(dumplist) == 0:
                        print(f'{R}[-] {C}Dumps are not Accessible...{W}')
                except Exception:
                    pass

    if len(dumplist) != 0:
        print(f'\n\n{G}[+] {C}Passwords : {W}\n')
        for entry in dumplist:
            time.sleep(1.1)
            try:
                page = requests.get(entry, timeout=10)
                dict = page.content.decode('utf-8', 'ignore')
                passwd = re.search('{}:(\w+)'.format(target), dict)
                if passwd:
                    print(f'{G}[+] {W}{passwd.group(1)}')
                elif not passwd:
                    for line in dict.splitlines():
                        passwd = re.search('(.*{}.*)'.format(target), line)
                        if passwd:
                            print(f'{G}[+] {W}{passwd.group(0)}')
            except requests.exceptions.ConnectionError:
                pass


def breach_info():
    print(f'{G}[+] {C}Breach Name : {W}{breach_name}', end='')
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
                    print(f' {G}[ pwned ]{W}')
                    print(f'\n')
                    print(f'{G}[+] {C}Breach      : {W}{str(simple_out["Title"])}\n')
                    print(f'{G}[+] {C}Domain      : {W}{str(simple_out["Domain"])}\n')
                    print(f'{G}[+] {C}Date        : {W}{str(simple_out["BreachDate"])}\n')
                    print(f'{G}[+] {C}Pwn Count   : {W}{str(simple_out["PwnCount"])}\n')
                    print(f'{G}[+] {C}Fabricated  : {W}{str(simple_out["IsFabricated"])}\n')
                    print(f'{G}[+] {C}Verified    : {W}{str(simple_out["IsVerified"])}\n')
                    print(f'{G}[+] {C}Retired     : {W}{str(simple_out["IsRetired"])}\n')
                    print(f'{G}[+] {C}Spam        : {W}{str(simple_out["IsSpamList"])}\n')
                    print(f'{G}[+] {C}Data Types  : {W}{str(simple_out["DataClasses"])}')
                else:
                    print(f' {R}[ Not Breached ]{W}')
            elif sc == 429:
                retry_sleep = float(rqst.headers['Retry-After'])
                print(f' {Y}[ retry in {retry_sleep}s]{W}')
                time.sleep(retry_sleep)
                breach_info()
            elif sc == 404:
                print(f' {R}[ Not Breached ]{W}')
            else:
                print(f'\n{R}[-] {C}Status {code} : {W}{desc}')


def domains_list():
    domains = []
    print(f'{G}[+] {C}Fetching List of Breached Domains...{W}\n')
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
                        print(G + '[+] ' + W + str(domain_name))
                        domains.append(domain_name)
                print(f'\n{G}[+] {C}Total : {W}{len(domains)}')
            else:
                print(f'\n{R}[-] {C}Status {code} : {W}{desc}')


def domain_check():
    print(f'{G}[+] {C}Domain Name : {W}{check_domain}', end='')
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
                    print(f' {G}[ pwned ]{W}')
                    for item in simple_out:
                        print(f'\n')
                        print(f'{G}[+] {C}Breach      : {W}{str(item["Title"])}\n')
                        print(f'{G}[+] {C}Domain      : {W}{str(item["Domain"])}\n')
                        print(f'{G}[+] {C}Date        : {W}{str(item["BreachDate"])}\n')
                        print(f'{G}[+] {C}Pwn Count   : {W}{str(item["PwnCount"])}\n')
                        print(f'{G}[+] {C}Fabricated  : {W}{str(item["IsFabricated"])}\n')
                        print(f'{G}[+] {C}Verified    : {W}{str(item["IsVerified"])}\n')
                        print(f'{G}[+] {C}Retired     : {W}{str(item["IsRetired"])}\n')
                        print(f'{G}[+] {C}Spam        : {W}{str(item["IsSpamList"])}\n')
                        print(f'{G}[+] {C}Data Types  : {W}{str(item["DataClasses"])}')
                        print(f'{G}[+] {C}Description : {W}{html2text(str(item["Description"]))}')
                else:
                    print(f' {R}[ Not Breached ]{W}')
            elif sc == 404:
                print(f' {R}[ Not Breached ]{W}')
            else:
                print(f'\n{R}[-] {C}Status {code} : {W}{desc}')


def quit():
    print(f'\n{G}[+] {C}Completed in {W}{str(time.time() - start)} {C}seconds.{W}')
    exit()


if __name__ == "__main__":
    idle_time = 1.6
    try:
        main()
        quit()
    except KeyboardInterrupt:
        print(f'\n{R}[!] {C}Keyboard Interrupt.{W}')
        exit()
