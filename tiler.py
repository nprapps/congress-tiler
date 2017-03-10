import logging
import os
import random
import requests

from PIL import Image
from cropped_thumbnail import cropped_thumbnail

BASE_WIDTH = 450
BASE_HEIGHT = 550
IMAGE_COLUMNS = 9
ASPECT_RATIO = 16/9.
DATA_URL = 'http://staging.project.wnyc.org/healthcare-stance/assets/data/all-states.json'
LOG_FORMAT = '%(levelname)s:%(name)s:%(asctime)s: %(message)s'
URL_TEMPLATE = 'https://theunitedstates.io/images/congress/{0}x{1}/%s.jpg'.format(BASE_WIDTH, BASE_HEIGHT)

logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_ids():
    resp = requests.get(DATA_URL)
    ids = [row['bioguideid'] for row in resp.json() if row.get('edited')]
    return ids


def calculate_rows():
    rows = 1 / ASPECT_RATIO * IMAGE_COLUMNS * BASE_WIDTH / BASE_HEIGHT
    return int(round(rows))


def get_image(id):
    imgpath = 'img/%s.jpg' % id

    if not os.path.isfile(imgpath):
        url = URL_TEMPLATE % id
        logger.info('Getting {0}'.format(url))
        os.system('wget -q %s -P img' % url)

    return imgpath


def make_promotion_thumb():
    rows = calculate_rows()

    image = Image.new('RGB', [IMAGE_COLUMNS * BASE_WIDTH, rows * BASE_HEIGHT])

    ids = get_ids()

    seen = []
    coordinates = [0, 0]

    i = 0

    while i < rows:
        j = 0

        while j < IMAGE_COLUMNS:
            id = random.choice(ids)
            if id in seen:
                continue
            seen.append(id)

            imgpath = get_image(id)

            try:
                congress_image = Image.open(imgpath)
            except IOError:
                continue

            logger.info('Pasting {0} at {1}, {2}'.format(imgpath, coordinates[0], coordinates[1]))

            image.paste(congress_image, tuple(coordinates))
            coordinates[0] += BASE_WIDTH
            j += 1

        coordinates[0] = 0
        coordinates[1] += BASE_HEIGHT
        i += 1

    image.save('congress-uncropped.jpg', quality=95)

    cropped = cropped_thumbnail(image, [4050, 2278])
    cropped.save('congress.jpg', quality=95)


if __name__ == '__main__':
    make_promotion_thumb()
