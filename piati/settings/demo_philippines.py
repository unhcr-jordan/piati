from piati.settings.default import *

DEFAULT_MAP_CENTER = [11.24, 125]
DEFAULT_MAP_ZOOM = 14
SITE_NAME = "Philippines Projects"
SITE_BASELINE = "Testing IATI data in the Philippines."
BABEL_DEFAULT_LOCALE = "en"
DATA = {
    "DEMO_PH": "http://iati-datastore.herokuapp.com/api/1/access/activity.xml?recipient-country=PH",
}
SECTOR_VOCABULARY = "DAC"
FREEZER_DESTINATION = os.path.join(PROJECT_DIR, 'build', 'demo')
