from piati.settings.default import *

DEFAULT_MAP_CENTER = [15, -5]
DEFAULT_MAP_ZOOM = 6
SITE_NAME = "L'aide française au Mali"
SITE_BASELINE = "Suivez l'aide au développement au Mali"
BABEL_DEFAULT_LOCALE = "fr"
DATA = {
    "FR_ML": "http://iati-datastore.herokuapp.com/api/1/access/activity.xml?reporting-org=FR-99|FR-6|FR-3&recipient-country=ML",
}
SECTOR_VOCABULARY = "RO"
DOWNLOAD_LINK = "http://www.data.gouv.fr/fr/dataset/projets-d-aide-de-la-france-au-mali"
FREEZER_DESTINATION = os.path.join(PROJECT_DIR, 'build', 'mali')
