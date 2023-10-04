import asyncio
import json
from collections import defaultdict

import aiomqtt

from helper import loop_forever, run_program, check_installed, ReconTopics
from log import LOGGER, extra


async def msg_handler(payload: dict, client: aiomqtt.Client) -> None:
    trace_id = payload['trace_id']
    domain = payload['domain']

    LOGGER.debug('Enumerating subdomains',
                 extra=extra(trace_id, domain=domain))

    async with asyncio.TaskGroup() as tg:
        amass_task = tg.create_task(run_program(
            'amass',
            'enum',
            '-passive',
            '-norecursive',
            '-silent',
            '-d',
            domain,
            trace_id=trace_id))

        subfinder_task = tg.create_task(run_program(
            'subfinder',
            '-silent',
            '-d',
            domain,
            trace_id=trace_id))

        findomain_task = tg.create_task(
            run_program('findomain', '-q', '-t', domain, trace_id=trace_id))

    subdomains = defaultdict(list)

    for subdomain in amass_task.result():
        subdomains[subdomain].append('amass')

    for subdomain in subfinder_task.result():
        subdomains[subdomain].append('subfinder')

    for subdomain in findomain_task.result():
        subdomains[subdomain].append('findomain')

    for subdomain, found_by in subdomains.items():
        found_by = ' '.join(found_by)
        LOGGER.info(
            'Subdomain found',
            extra=extra(trace_id, subdomain=subdomain, found_by=found_by))

    LOGGER.debug('Finished enumerating subdomains', extra=extra(trace_id))

    await client.publish(ReconTopics.SUBDOMAINS_INFO_GATHERING, json.dumps({
        'trace_id': trace_id,
        'subdomains': subdomains,
    }))


async def run_main_loop():
    LOGGER.debug('Checking if tools are installed')

    tools_ok = await check_installed('amass', 'subfinder', 'findomain')

    if not tools_ok:
        LOGGER.critical('Some tools are not installed')
        return

    await loop_forever(
        topic_name=ReconTopics.SUBDOMAIN_ENUMERATION,
        step_name='subdomain-enumeration',
        msg_handler=msg_handler)
