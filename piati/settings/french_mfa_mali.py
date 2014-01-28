from piati.settings.default import *

DEFAULT_MAP_CENTER = [15, -5]
DEFAULT_MAP_ZOOM = 6
SITE_NAME = "L'aide française au Mali"
SITE_BASELINE = "Suivez l'aide au développement au Mali"
BABEL_DEFAULT_LOCALE = "fr"
DATA = {
    "FR-99_ML": "http://iati-datastore.herokuapp.com/api/1/access/activity.xml?reporting-org=FR-99&recipient-country=ML",
    "FR-6_ML": "http://iati-datastore.herokuapp.com/api/1/access/activity.xml?reporting-org=FR-6&recipient-country=ML",
    "FR-3_ML": "http://iati-datastore.herokuapp.com/api/1/access/activity.xml?reporting-org=FR-3&recipient-country=ML",
}
SECTOR_VOCABULARY = "RO"
DOWNLOAD_LINK = "http://www.data.gouv.fr/fr/dataset/projets-d-aide-de-la-france-au-mali"
FREEZER_DESTINATION = os.path.join(PROJECT_DIR, 'build', 'mali')
FEEDBACK_POST_URL = "http://www.ambafrance-ml.org/spip.php?action=transparence_mail"
FEEDBACK_SMS_NUMBER = "+22373013232"
PROJECT_MODEL = "DataGouvFrProject"
CURRENCY_FORMAT = '#,##0 \xa4'
PARENT_SITE = {
    "label": "Ambassade de France au Mali",
    "url": "http://www.ambafrance-ml.org/"
}
