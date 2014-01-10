import os
import re

from collections import Counter

import requests

from flask.ext.babel import gettext as _

RATES = {}


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


def fetch_exchange_rates(app):
    params = {
        'app_id': app.config['OPENEXCHANGERATES_ID']
    }
    r = requests.get("https://openexchangerates.org/api/latest.json", params=params)
    filepath = get_rates_filepath(app)
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write(r.text)
        print('Rates successfully fetched and saved to', filepath)


def get_rates_filepath(app):
    return os.path.join(app.config['DATA_DIR'], 'rates.json')


def xrate(amount, currency):
    amount = float(amount)
    if currency == "EUR":
        return amount
    if currency not in RATES:
        return 0
    if currency != "USD":
        amount = amount / RATES[currency]
    return amount * RATES['EUR']


def get_main_sectors(data, items=10):
    counter = Counter()
    names = {}
    for project in data.values():
        for sector in project.sectors:
            counter[sector['code']] += 1
            names[sector['code']] = sector['name']

    def make(code, count):
        return {
            "value": count,
            "label": names[code],
            "code": code
        }

    return [make(code, count) for code, count in counter.most_common(items)]


def getStatus(c):
    # http://iatistandard.org/codelists/activity_status/
    status = {
        1: _("Pipeline/identification"),
        2: _('Implementation'),
        3: _('Completion'),
        4: _('Post-completion'),
        5: _('Cancelled'),
    }
    return status.get(c)


def getTransactionType(value):
    types = {
        'C': _('Commitment'),
        'D': _('Disbursement'),
        'E': _('Expenditure'),
        'IF': _('Incoming Funds'),
        'IR': _('Interest Repayment'),
        'LR': _('Loan Repayment'),
        'R': _('Reimbursement'),
        'QP': _('Purchase of Equity'),
        'QS': _('Sale of Equity'),
        'CG': _('Credit Guarantee'),
    }
    try:
        return types[value]
    except KeyError:
        return ""


def getDateType(value):
    types = {
        'start-planned': _('Planned start'),
        'start-actual': _('Actual start'),
        'end-planned': _('Planned end'),
        'end-actual': _('Actual end')
    }
    try:
        return types[value]
    except KeyError:
        return ""


def getRoleType(role):
    roles = {
        'Funding': _('funding'),
        'Extending': _('extending'),
        'Implementing': _('implementing'),
        'Reporting': _('reporting'),
    }
    return roles.get(role, role)


def getTiedStatus(c):
    # http://iatistandard.org/codelists/tied_status/
    status = {
        3: _("partially tied"),
        4: _("tied"),
        5: _("untied")
    }
    return status.get(c)


def getFlowType(c):
    # http://iatistandard.org/codelists/flow_type/
    types = {
        10: _("ODA Official Development Assistance"),
        20: _('OOF Other Official Flows'),
        30: _('Private Grants'),
        35: _('Private Market'),
        40: _('Non flow'),
        50: _('Other flows'),
    }
    return types.get(c)


def getAidType(c):
    # http://iatistandard.org/codelists/aid_type/
    types = {
        "A01": _("General budget support"),
        "A02": _("Sector budget support"),
        "B01": _("Core support to NGOs, other private bodies, PPPs and research institutes"),
        "B02": _("Core contributions to multilateral institutions"),
        "B03": _("Contributions to specific-purpose programmes and funds managed by international organisations (multilateral, INGO)"),
        "B04": _("Basket funds/pooled funding"),
        "C01": _("Project-type interventions"),
        "D01": _("Donor country personnel"),
        "D02": _("Other technical assistance"),
        "E01": _("Scholarships/training in donor country"),
        "E02": _("Imputed student costs"),
        "F01": _("Debt relief"),
        "G01": _("Administrative costs not included elsewhere"),
        "H01": _("Development awareness"),
        "H02": _("Refugees in donor countries"),
    }
    return types.get(c)


def getAidCategory(c):
    types = {
        "A": _("Budget support"),
        "B": _("Core contributions and pooled programmes and funds"),
        "C": _("Project-type interventions"),
        "D": _("Experts and other technical assistance"),
        "E": _("Scholarships and student costs in donor countries"),
        "F": _("Debt relief"),
        "G": _("Administrative costs not included elsewhere"),
        "H": _("Other in-donor expenditures"),
    }
    return types.get(c[0])


def getDocumentCategoryLabel(c):
    labels = {
        "A01": _("Pre- and post-project impact appraisal"),
        "A02": _("Objectives / Purpose of activity"),
        "A03": _("Intended ultimate beneficiaries"),
        "A04": _("Conditions"),
        "A05": _("Budget"),
        "A06": _("Summary information about contract"),
        "A07": _("Review of project performance and evaluation"),
        "A08": _("Results, outcomes and outputs"),
        "A09": _("Memorandum of understanding (If agreed by all parties)"),
        "A10": _("Tender"),
        "A11": _("Contract"),
        "B01": _("Annual report"),
        "B02": _("Institutional Strategy paper"),
        "B03": _("Country strategy paper"),
        "B04": _("Aid Allocation Policy"),
        "B05": _("Procurement Policy and Procedure"),
        "B06": _("Institutional Audit Report"),
        "B07": _("Country Audit Report"),
        "B08": _("Exclusions Policy"),
        "B09": _("Institutional Evaluation Report"),
        "B10": _("Country Evaluation Report")
    }
    return labels.get(c)


def makeIdentifierSafe(identifier):
    identifier = re.sub("/", "___", identifier)
    identifier = re.sub(":", ">>>", identifier)
    return identifier


def reverseSafeIdentifier(identifier):
    identifier = re.sub("___", "/", identifier)
    identifier = re.sub(">>>", ":", identifier)
    return identifier
