import pathlib
from typing import Final

from app.breach_info import breach_info
from app.check import check
from app.domain_check import domain_check
from app.domains_list import domains_list
from app.filtered_check import filtered_check
from app.init_args import init_args
from app.read_config import read_config


# --email example@gmail.com --list --output data.json
def main():
    args = init_args()

    emails_list = [args.email]
    file = args.file
    list_domain = args.list

    if file:
        emails_list = []
        with open(file, 'r') as f:
            emails = f.readlines()
        for line in emails:
            emails_list.append(line.strip())

    output_json: pathlib.Path = args.output

    api_key = args.api_key

    domain = args.domain
    breach_name = args.breach
    nodumps = args.nodumps
    check_domain = args.check

    MAIN_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent
    conf_path = MAIN_DIR / 'config.json'
    user_agent = read_config(api_key=api_key, conf_path=conf_path)

    if list_domain:
        domains_list(
            output_json=output_json,
            useragent=user_agent,
        )
    elif check_domain:
        domain_check(
            useragent=user_agent,
            check_domain=check_domain,
        )
    elif breach_name:
        breach_info(
            useragent=user_agent,
            breach_name=breach_name,
        )

    for email in emails_list:
        if email is not None and domain is not None:
            filtered_check(
                useragent=user_agent,
                target=email,
                domain=domain,
                nodumps=nodumps,
                output_json=output_json,
            )
        elif email is not None and domain is None:
            check(
                useragent=user_agent,
                target=email,
                output_json=output_json,
                nodumps=nodumps,
            )



if __name__ == '__main__':
    main()
