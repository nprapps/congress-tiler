#from urllib3.contrib import pyopenssl
#pyopenssl.inject_into_urllib3()

import logging
import os
import random
import requests

from PIL import Image


DATA_URL = 'http://staging.project.wnyc.org/healthcare-stance/assets/data/all-states.json'
IMAGE_COLUMNS = 10
LOG_FORMAT = '%(levelname)s:%(name)s:%(asctime)s: %(message)s'
PROMOTION_IMAGE_WIDTH = 3000
TOTAL_IMAGES = 40
URL_TEMPLATE = 'https://theunitedstates.io/images/congress/450x550/%s.jpg'

logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_ids():
    resp = requests.get(DATA_URL)
    ids = [row['bioguideid'] for row in resp.json() if row.get('edited')]
    return ids


def make_promotion_thumb():
    images_per_column = TOTAL_IMAGES / IMAGE_COLUMNS
    image_width = PROMOTION_IMAGE_WIDTH / IMAGE_COLUMNS
    max_height = int(image_width * images_per_column * 1.5)
    image = Image.new('RGB', [PROMOTION_IMAGE_WIDTH, max_height])

    ids = get_ids()

    seen = []

    coordinates = [0, 0]
    last_y = 0
    total_height = 0
    min_height = None
    column_multiplier = 0

    i = 0
    while i < TOTAL_IMAGES:
        id = random.choice(ids)
        if id in seen:
            continue

        imgpath = 'img/%s.jpg' % id

        if not os.path.isfile(imgpath):
            url = URL_TEMPLATE % id
            logger.info('Getting {0}'.format(url))
            os.system('wget -q %s -P img' % url)

        seen.append(id)

        try:
            congress_image = Image.open(imgpath)
        except IOError:
            continue

        if i % images_per_column == 0:
            if not min_height or total_height < min_height:
                min_height = total_height
            coordinates[0] = column_multiplier * image_width
            coordinates[1] = 0
            last_y = 0
            column_multiplier +=1
            total_height = 0

        width, height = congress_image.size
        ratio = width / float(image_width)
        new_height = int(height / ratio)
        resized = congress_image.resize((image_width, new_height), Image.ANTIALIAS)
        coordinates[1] = coordinates[1] + last_y

        image.paste(resized, tuple(coordinates))
        last_y = new_height
        total_height += new_height

        i += 1

    min_prop_width = min_height * 16 / float(9)
    # Make the proportion fit the highest full thumbnail width
    # that complies with the proportion
    final_width = int(min_prop_width / image_width) * image_width
    cropped = image.crop((0, 0, final_width, min_height))
    # via http://stackoverflow.com/questions/1405602/how-to-adjust-the-quality-of-a-resized-image-in-python-imaging-library
    cropped.save('congress.jpg', quality=95)


if __name__ == '__main__':
    make_promotion_thumb()
