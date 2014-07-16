import os

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir))
FREEZER_RELATIVE_URLS = True
FREEZER_DESTINATION = os.path.join(PROJECT_DIR, 'build')
DATA = {
    "FR_ML": "",
}
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DEFAULT_MAP_CENTER = [15, -5]
DEFAULT_MAP_ZOOM = 6
SITE_NAME = "Support Projects in Jordan "
SITE_BASELINE = "Support Projects in Jordan "
BABEL_DEFAULT_LOCALE = "en"
OPENEXCHANGERATES_ID = os.environ.get('OPENEXCHANGERATES_ID')
SECTOR_VOCABULARY = "DAC"
DOWNLOAD_LINK = ""
DEFAULT_TIMEZONE = 'UTC'
FEEDBACK_POST_URL = ""
FEEDBACK_SMS_NUMBER = ""
PROJECT_MODEL = "Project"
CURRENCY_FORMAT = None
PARENT_SITE = {
    "label": "UNHCR Jordan",
    "url": "http://www.unhcr.jo/projects"
}
