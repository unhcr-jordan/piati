from lxml import etree

from flask import Flask, render_template
from flask.json import tojson_filter

from .iati import Project
from .helpers import get_data_filepath, get_main_sectors, reverseSafeIdentifier

app = Flask(__name__)


DATA = {}


@app.route("/")
def index():
    last_projects = sorted(DATA.values(), key=lambda p: p.last_updated, reverse=True)[:5]
    context = {
        "projects": list(DATA.values()),
        "last_projects": last_projects,
        "main_sectors": get_main_sectors(DATA),
    }
    return render_template('index.html', **context)


@app.route("/projects/<iati_identifier>/")
def show_project(iati_identifier=None):
    iati_identifier = reverseSafeIdentifier(iati_identifier)
    project_data = DATA[iati_identifier]
    return render_template('project.html', project=project_data)


@app.route("/projects/")
def show_projects():
    return render_template('projects.html', projects=list(DATA.values()))


@app.route("/about/")
def about():
    return render_template('about.html')


def load_data():
    for name in app.config['DATA'].keys():
        filepath = get_data_filepath(app, name)
        with open(filepath, mode="r") as f:
            # Avoid namespace pollution, useless here
            xml = f.read().replace(' xmlns:', ' xmlnamespace:')
            parent = etree.fromstring(xml).find('iati-activities')
            for node in parent.findall('iati-activity'):
                project = Project(node)
                DATA[project.id] = project


@app.template_filter('piati_tojson')
def tojson(s):
    """Allow use of for_json method."""
    return tojson_filter(s, for_json=True)
