from json import load as json_load
from google.cloud import storage, vision

with open('config.json') as json_data_file:
    cfg = json_load(json_data_file)

storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()

def check_images(data, context):
    uri = "gs://" + data['bucket'] + "/" + data['name']
    image = vision.types.Image()
    image.source.image_uri = uri

    # query the Cloud Vision API
    response = vision_client.safe_search_detection(image=image)
    safe = response.safe_search_annotation
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')

    # has the image been flagged?
    flagged = False
    for outcome in ['POSSIBLE', 'LIKELY', 'VERY_LIKELY']:
        for result in [likelihood_name[safe.adult], likelihood_name[safe.violence], likelihood_name[safe.racy]]:
            if result == outcome:
                flagged = True

    # get the actual image from GCS
    bucket = storage_client.get_bucket(data['bucket'])
    blob = bucket.get_blob(data['name'])

    # pick the new bucket based on how nsfw it is
    if flagged:
        newbucket = storage_client.get_bucket(cfg['FLAGGED_BUCKET'])
    else:
        newbucket = storage_client.get_bucket(cfg['IMAGES_BUCKET'])

    # rewrite the image and delete the original
    newblob = newbucket.blob(data['name'])
    newblob.rewrite(blob)
    blob.delete()
