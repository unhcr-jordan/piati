from datetime import datetime, timezone

import pytz

from dateutil.parser import parse as parse_datetime

from flask import url_for

from .helpers import getDateType, getRoleType, getStatus, getTiedStatus,\
    getFlowType, getAidType, getAidCategory, xrate, getDocumentCategoryLabel,\
    getTransactionType


class Project(object):

    def __init__(self, app, xml):
        self._xml = xml
        self._app = app

    def _text(self, selector):
        return self._xml.findtext(selector)

    def _activity_date(self, type):
        el = self._xml.xpath('activity-date[@type="{0}"]'.format(type))
        if el:
            return parse_datetime(el[0].attrib.get('iso-date'))

    @property
    def id(self):
        return self._text('iati-identifier')

    @property
    def name(self):
        return self._text('title')

    @property
    def description(self):
        return self._text('description')

    @property
    def status(self):
        return getStatus(self.status_code) or self._text('activity-status')

    @property
    def status_code(self):
        try:
            return int(self._xml.xpath('activity-status')[0].attrib.get('code'))
        except IndexError:
            return None

    @property
    def tied_status(self):
        return getTiedStatus(self.tied_status_code) \
            or self._text('default-tied-status')

    @property
    def tied_status_code(self):
        return int(self._xml.xpath('default-tied-status')[0].attrib.get('code'))

    @property
    def flow(self):
        return getFlowType(self.flow_code) or self._text('default-flow-type')

    @property
    def flow_code(self):
        return int(self._xml.xpath('default-flow-type')[0].attrib.get('code'))

    @property
    def aid_type(self):
        return getAidType(self.aid_code) or self._text('default-aid-type')

    @property
    def aid_category(self):
        return getAidCategory(self.aid_code) or self._text('default-aid-type')

    @property
    def aid_code(self):
        return self._xml.xpath('default-aid-type')[0].attrib.get('code')

    @property
    def is_active(self):
        return self.status_code in [2, 3]

    @property
    def url(self):
        return url_for('show_project', iati_identifier=self.id)

    @property
    def last_updated(self):
        d = self._xml.attrib.get('last-updated-datetime')
        if d is None:
            d = datetime.now(tz=timezone.utc)
        else:
            d = parse_datetime(d)
        if d.tzinfo is None:
            tz = pytz.timezone(self._app.config['DEFAULT_TIMEZONE'])
            d = tz.localize(d)
        return d

    @property
    def currency(self):
        return self._xml.attrib.get('default-currency')

    @property
    def start_actual(self):
        return self._activity_date('start-actual')

    @property
    def start_date(self):
        return self._activity_date('start-actual') or self._activity_date('start-planned')

    @property
    def end_date(self):
        return self._activity_date('end-actual') or self._activity_date('end-planned')

    @property
    def participating_org(self):
        def make(node):
            return {
                "name": node.text,
                "ref": node.attrib.get('ref'),
                "role": getRoleType(node.attrib.get('role')),
                "type": node.attrib.get('type'),
            }
        return [make(node) for node in self._xml.xpath('participating-org')]

    @property
    def collaboration(self):
        return self._text('collaboration-type')

    @property
    def reporting_org(self):
        org = self._xml.find('reporting-org')
        if org is not None:
            return {
                "name": org.text,
                "ref": org.attrib.get('ref'),
                "role": getRoleType("Reporting"),
                "type": org.attrib.get('type'),
            }

    @property
    def locations(self):
        def make(node):
            return {
                "lat": node.find('coordinates').attrib['latitude'],
                "lng": node.find('coordinates').attrib['longitude'],
                "precision": int(node.find('coordinates').attrib['precision']),
                "name": node.findtext('name'),
            }
        return [make(location) for location in self._xml.xpath('location[child::coordinates]')]

    @property
    def sectors(self):
        def make(node):
            return {
                "code": node.attrib.get('code'),
                "percentage": node.attrib.get('percentage'),
                "vocabulary": node.attrib.get('vocabulary'),
                "name": node.text,
            }
        path = 'sector[@vocabulary="{0}"]'.format(self._app.config['SECTOR_VOCABULARY'])
        return [make(node) for node in self._xml.xpath(path)]

    @property
    def default_sector(self):
        return self.sectors[0]

    @property
    def budget(self):
        budget = 0
        for node in self._xml.findall('budget'):
            value = node.find('value')
            budget += xrate(value.text, value.attrib.get('currency', self.currency))
        return int(budget)

    @property
    def topics(self):
        return [node.text for node in self._xml.findall('policy-marker') if node.text]

    @property
    def dates(self):
        def make(node):
            return {
                "value": parse_datetime(node.attrib.get('iso-date')),
                "label": getDateType(node.attrib['type'])
            }
        return [make(node) for node in self._xml.xpath('activity-date')]

    @property
    def transactions(self):
        def make(node):
            value = node.find('value')
            currency = value.attrib.get('currency', self.currency)
            code = node.find('transaction-type').attrib.get('code')
            return {
                "type": getTransactionType(code),
                "code": code,
                "provider": node.findtext('provider-org'),
                "receiver": node.findtext('receiver-org'),
                "value": xrate(value.text or 0, currency),
                "currency": currency,
                "date": parse_datetime(node.find('transaction-date').attrib['iso-date']),
            }
        return [make(node) for node in self._xml.xpath('transaction')]

    @property
    def total_commitment(self):
        return int(sum(t['value'] for t in self.transactions if t['code'] == 'C'))

    @property
    def total_disbursment(self):
        return int(sum(t['value'] for t in self.transactions if t['code'] in ['D', 'E']))

    @property
    def total_budget(self):
        return self.budget or self.total_commitment

    @property
    def results(self):
        def make_indicator(node):
            return {
                "label": node.findtext('title'),
                "start": parse_datetime(node.findtext('period/period-start')),
                "end": parse_datetime(node.findtext('period/period-end')),
            }

        def make_result(node):
            return {
                'label': node.findtext('title'),
                'indicators': [make_indicator(subnode) for subnode in node.findall('indicator')]
            }
        return [make_result(node) for node in self._xml.xpath('result')]

    @property
    def documents(self):
        def make(node):
            return {
                "title": node.findtext('title'),
                "format": node.attrib.get('format'),
                "url": node.attrib.get('url'),
                "categories": [getDocumentCategoryLabel(n.attrib['code']) for n in node.xpath('category')]
            }
        return [make(node) for node in self._xml.xpath('document-link')]

    def for_json(self):
        """Javascript ready version of the data."""
        return {
            "id": self.id,
            "url": self.url,
            "name": self.name,
            "status": self.status,
            "locations": [l for l in self.locations if l['precision'] < 6],
            "sectors": self.sectors,
            "orgs": self.participating_org + [self.reporting_org],
            "source": self.reporting_org,
            "budget": self.total_budget,
            "dates": self.dates,
            "topics": self.topics,
            "flow": self.flow,
            "aid_type": self.aid_type,
        }


class DataGouvFrProject(Project):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ns = self._xml.nsmap['fr']

    @property
    def beneficiaries_fr(self):
        return self._xml.find('{%s}beneficiaires' % self.ns).text

    @property
    def progress_fr(self):
        return self._xml.find('{%s}avancement' % self.ns).text

    @property
    def cofunding_fr(self):
        return self._xml.find('{%s}cofinancement' % self.ns).text


def get_model(app):
    try:
        key = app.config['PROJECT_MODEL']
    except KeyError as e:
        e.args += ('You must configure the PROJECT_MODEL setting', )
        raise
    else:
        try:
            return globals()[key]
        except KeyError as e:
            e.args += ('is not a correct Project name', )
            raise
