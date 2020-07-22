import logging

import requests
from clarifai.rest import ClarifaiApp
from googletrans import Translator

import config

logging.basicConfig(filename='bot.log', level=logging.INFO)


def what_is(filename):
    app = ClarifaiApp(api_key=config.CLARIFAI_API)
    model = app.public_models.general_model
    translator = Translator()
    values = []
    whatis_string = ''
    response = model.predict_by_filename(filename, max_concepts=5)
    if response['status']['code'] == 10000:
        for concept in response['outputs'][0]['data']['concepts']:
            name = translator.translate(concept['name'], dest='ru').text
            chance = float('{:.3f}'.format(concept['value'] * 100))
            value = 'С вероятностью в {}% на картинке {}'.format(chance, name)
            values.append(value)
    for val in values:
        whatis_string = '\n'.join(values)
    return whatis_string


def color_image(image_file):
    url = "https://api.deepai.org/api/colorizer"
    resp = requests.post(url, files={
        'image': image_file, },
                         headers={'api-key': config.IMAGE_API})
    url = resp.json()['output_url']
    return url

