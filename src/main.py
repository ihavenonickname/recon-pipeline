import argparse

import log
from helper import run_shell_command
from subdomain_enumeration import SourcesDupsStrategy, SubdomainEnumerator


def main():
    parser = argparse.ArgumentParser(
        prog='Recon Pipeline',
        description='My personal pipeline for recon operations')

    parser.add_argument(
        '--domain',
        help='Enumerate the subdomains under the given domain',
        required=True)

    parser.add_argument(
        '--recursive',
        help='Should enumerate subdomains recursively?',
        required=False,
        type=bool,
        default=False,
        choices=[True, False])

    args = parser.parse_args()

    log.configure()

    try:
        run_shell_command('amass', '--help')
    except FileNotFoundError:
        log.LOGGER.info('amass not found')
        return

    try:
        run_shell_command('subfinder', '--help')
    except FileNotFoundError:
        log.LOGGER.info('amass not found')
        return

    enumerator = SubdomainEnumerator(
        sources_dups_strategy=SourcesDupsStrategy.PREFER_AMASS)

    if args.recursive:
        subdomains = enumerator.recursively_enumerate_subdomains(args.domain)
    else:
        subdomains = enumerator.enumerate_subdomains(args.domain)

    for subdomain in subdomains:
        print('>', subdomain)


if __name__ == '__main__':
    main()
