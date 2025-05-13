import argparse


def init_args():
    parse = argparse.ArgumentParser()

    parse.add_argument('--api-key', required=True, help='Your API key for haveibeenpwned.com')

    parse.add_argument('--email', required=False, help='Email Address You Want to Test')
    parse.add_argument('--file', required=False, help='Load a File with Multiple Email Addresses')
    parse.add_argument('--output', required=False, help='Output file for pawned mail addresses')
    parse.add_argument('--domain', required=False, help='Filter Results by Domain Name')
    parse.add_argument('--breach', required=False, help='Get Info about breach')
    parse.add_argument('--nodumps', required=False, action='store_true',
                       help='Only Check Breach Info and Skip Password Dumps')
    parse.add_argument('--list', required=False, action='store_true', help='Get List of all pwned Domains')
    parse.add_argument('--check', required=False, help='Check if your Domain is pwned')

    return parse.parse_args()
