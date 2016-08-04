# -*- coding=utf8 -*-
"""
    寮傛浠诲姟绫�
"""
import logging
import requests
from celery import Celery

from zhihu.settings import BROKER_URL

app = Celery('image_downloader', broker=BROKER_URL)
LOGGER = logging.getLogger(__name__)


@app.task
def download_pic(image_url, image_path):
    """寮傛涓嬭浇鍥剧墖

    Args:
        image_url (string): 鍥剧墖閾炬帴
        image_path (string): 鍥剧墖璺緞
    """
    if not (image_url and image_path):
        LOGGER.INFO('illegal parameter')

    try:
        image = requests.get(image_url, stream=True)
        with open(image_path, 'wb') as img:
            img.write(image.content)
    except Exception as exc:
        LOGGER.ERROR(exc)
