import os
import re

from collections import Counter

import requests


def fetch_remote_data(url, filepath):
    try:
        print('Getting data from', url)
        r = requests.get(url)
    except requests.exceptions.RequestException:
        print('Problem in the request')
    else:
        if r.status_code != 200:
            print('Problem in the request')
        with open(filepath, mode="w", encoding="utf-8") as f:
            f.write(r.text)
            print('Content successfully fetched and saved to', filepath)


def get_data_filepath(app, name):
    return os.path.join(app.config['DATA_DIR'], '{0}.xml'.format(name))


def get_main_sectors(data, items=10):
    counter = Counter()
    names = {}
    for project in data.values():
        for sector in project.sectors:
            counter[sector['code']] += 1
            names[sector['code']] = sector['name']
    return [(code, names[code]) for code, count in counter.most_common(items)]


def getTransactionType(value):
    types = {
        'C': 'Commitment',
        'D': 'Disbursement',
        'E': 'Expenditure',
        'IF': 'Incoming Funds',
        'IR': 'Interest Repayment',
        'LR': 'Loan Repayment',
        'R': 'Reimbursement',
        'QP': 'Purchase of Equity',
        'QS': 'Sale of Equity',
        'CG': 'Credit Guarantee'
    }
    try:
        return types[value]
    except KeyError:
        return ""


def getDateType(value):
    types = {
        'start-planned': 'Planned start',
        'start-actual': 'Actual start',
        'end-planned': 'Planned end',
        'end-actual': 'Actual end'
    }
    try:
        return types[value]
    except KeyError:
        return ""


def makeIdentifierSafe(identifier):
    identifier = re.sub("/", "___", identifier)
    identifier = re.sub(":", ">>>", identifier)
    return identifier


def reverseSafeIdentifier(identifier):
    identifier = re.sub("___", "/", identifier)
    identifier = re.sub(">>>", ":", identifier)
    return identifier
