import requests
import sys
import os
import json
import logging, logging.handlers
import time


t = time.localtime()
current_time = time.strftime('%Y-%m-%d', t)

def setup_logger(level):
    logger = logging.getLogger('download_results_logger')
    logger.propagate = False
    logger.setLevel(level)
    file_handler = logging.handlers.RotatingFileHandler(
        os.environ['SPLUNK_HOME'] + '/var/log/splunk/download_results_app.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger(logging.INFO)

def export_as_csv(session_key, sid, location, search_name):
    try:
        request_url = f'https://localhost:8089/services/search/jobs/{sid}/results'
        r = requests.get(
            request_url,
            headers={'Authorization': (f'Splunk {session_key}')},
            verify=False,
            data={'output_mode': 'csv'}
        )

        report_name = search_name.replace(' ', '-')
        filename = f'{location}/{report_name}_{current_time}.csv'
        with open(filename, 'wb') as f:
            f.write(r.content)
            f.close()

        logger.info(f'filetype:CSV filename:{filename}')
    
    except Exception as e:
        logger.exception(e)

def export_as_pdf(session_key, location, search_name):
    try:
        request_url = f'https://localhost:8089/services/pdfgen/render'
        r = requests.post(
            request_url,
            headers={'Authorization': (f'Splunk {session_key}')},
            verify=False,
            params={'input-report': search_name}
        )

        report_name = search_name.replace(' ', '-')
        filename = f'{location}/{report_name}_{current_time}.pdf'
        with open(filename, 'wb') as f:
            f.write(r.content)
            f.close()

        logger.info(f'filetype:PDF filename:{filename}')
    
    except Exception as e:
        logger.exception(e)

def main():
    if len(sys.argv) < 2 or sys.argv[1] != '--execute':
        sys.stderr.write('FATAL Unsupported execution mode (expected --execute flag)\n')
        logger.error('FATAL Unsupported execution mode (expected --execute flag)\n')
        sys.exit(1)

    payload = json.loads(sys.stdin.read())
    logger.info(payload)
    
    session_key = payload.get('session_key')
    sid = payload.get('sid')
    search_name = payload.get('search_name')
    config = payload.get('configuration')
    as_csv = config.get('as_csv')
    as_pdf = config.get('as_pdf')
    location = config.get('location')

    if as_csv == '1':
        export_as_csv(session_key, sid, location, search_name)
    if as_pdf == '1':
        export_as_pdf(session_key, location, search_name)


if __name__ == '__main__':
    main()
