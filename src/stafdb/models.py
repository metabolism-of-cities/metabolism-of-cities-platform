from django.db import models
from django.urls import reverse
# Used for image resizing
from stdimage.models import StdImageField
from django.conf import settings
from django.utils.text import slugify

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
import uuid

# We leave this because a certain migration needs it...
def shapefile_directory(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uuid/<filename>
    return "stafdb/{0}/{1}".format(instance.session.uuid, filename)
