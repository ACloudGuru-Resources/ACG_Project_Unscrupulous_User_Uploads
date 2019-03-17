from json import load as json_load
from wand.image import Image
from google.cloud import storage

with open('config.json') as json_data_file:
    cfg = json_load(json_data_file)

client = storage.Client()

def make_thumbnail(data, context):
    # Get the image from GCS
    bucket = client.get_bucket(data['bucket'])
    blob = bucket.get_blob(data['name'])
    imagedata = blob.download_as_string()

    # Create a new image object and resample it
    newimage = Image(blob=imagedata)
    newimage.sample(300,300)

    # Upload the resampled image to the thumbnails bucket
    bucket = client.get_bucket(cfg['THUMBNAIL_BUCKET'])
    newblob = bucket.blob('thumbnail-' + data['name'])
    newblob.upload_from_string(newimage.make_blob())
