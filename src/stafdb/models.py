# We leave this because a certain migration needs it...
# When we reset the migrations, let's delete this
def shapefile_directory(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uuid/<filename>
    return "stafdb/{0}/{1}".format(instance.session.uuid, filename)
