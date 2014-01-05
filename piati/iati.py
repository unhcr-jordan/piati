from datetime import datetime

from flask import url_for

from .helpers import getDateType, getRoleType


class Project(object):

    def __init__(self, xml):
        self._xml = xml

    def _text(self, selector):
        return self._xml.findtext(selector)

    def _activity_date(self, type):
        el = self._xml.xpath('activity-date[@type="{0}"]'.format(type))[0]
        if el is not None:
            return el.attrib.get('iso-date')

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
        return self._text('activity-status')

    @property
    def status_code(self):
        return self._xml.xpath('activity-status').attrib.get('code')

    @property
    def url(self):
        return url_for('show_project', iati_identifier=self.id)

    @property
    def last_updated(self):
        return datetime.strptime(self._xml.attrib['last-updated-datetime'], "%Y-%m-%dT%H:%M:%S")

    @property
    def currency(self):
        return self._xml.attrib.get('default-currency')

    @property
    def start_date(self):
        return self._activity_date('start-actual') or self._activity_date('start-planned')

    @property
    def end_date(self):
        return self._activity_date('end-actual') or self._activity_date('end-planned')

    def render_start_date(self):
        return self._activity_date('start-actual') or '{0} (planned)'.format(self._activity_date('start-planned'))

    def render_end_date(self):
        return self._activity_date('end-actual') or '{0} (planned)'.format(self._activity_date('end-planned'))

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
        return [make(location) for location in self._xml.xpath('location')]

    @property
    def sectors(self):
        def make(node):
            return {
                "code": node.attrib.get('code'),
                "percentage": node.attrib.get('percentage'),
                "vocabulary": node.attrib.get('vocabulary'),
                "name": node.text,
            }
        return [make(node) for node in self._xml.xpath('sector')]

    @property
    def budget(self):
        budget = 0
        for node in self._xml.findall('budget'):
            budget += int(node.findtext('value'))
        return budget

    @property
    def topics(self):
        return [node.text for node in self._xml.findall('policy-marker') if node.text]

    @property
    def dates(self):
        def make(node):
            return {
                "value": node.attrib.get('iso-date'),
                "label": getDateType(node.attrib['type'])
            }
        return [make(node) for node in self._xml.xpath('activity-date')]

    @property
    def transactions(self):
        def make(node):
            return {
                "type": node.findtext('transaction-type'),
                "provider": node.findtext('provider-org'),
                "receiver": node.findtext('receiver-org'),
                "value": int(node.findtext('value') or 0),
                "currency": self.currency,
                "date": node.find('transaction-date').attrib['iso-date'],
            }
        return [make(node) for node in self._xml.xpath('transaction')]

    @property
    def results(self):
        def make_indicator(node):
            return {
                "label": node.findtext('title'),
                "start": node.findtext('period-start'),
                "end": node.findtext('period-end'),
            }

        def make_result(node):
            return {
                'label': node.findtext('title'),
                'indicators': [make_indicator(subnode) for subnode in node.findall('indicator')]
            }
        return [make_result(node) for node in self._xml.xpath('result')]

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
            "budget": self.budget or sum(t['value'] for t in self.transactions),
            "dates": self.dates,
            "topics": self.topics,
        }
