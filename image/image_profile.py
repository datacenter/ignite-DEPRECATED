from django.db.models import ProtectedError

from constants import *
from models import ImageProfile
from utils.exception import IgniteException
from utils.encrypt import encrypt_data, decrypt_data
import logging
logger = logging.getLogger(__name__)

# image profile functions


def get_all_profiles(state):
    if state:
        return ImageProfile.objects.exclude(system_image__isnull=True)

    return ImageProfile.objects.all().order_by('profile_name')


def get_profile(id):
    return ImageProfile.objects.get(pk=id)


def add_profile(data, user, id=0):
    logger.debug("profile id = %d", id)

    if id:
        # update of an existing profile; fetch it
        profile = get_profile(id)
        logger.debug("password stored in db " + str(profile.image_server_password))
        if not profile.image_server_password == data[IMAGE_SERVER_PASSWORD]:
            password = encrypt_data(data[IMAGE_SERVER_PASSWORD])
            logger.debug("change in password, new encoded password " + str(password))
            profile.image_server_password = str(password)
            profile.is_encrypted = True

    else:
        # create new profile
        profile = ImageProfile()
        password = encrypt_data(data[IMAGE_SERVER_PASSWORD])
        profile.image_server_password = str(password)
        profile.is_encrypted = True

    profile.profile_name = data[PROFILE_NAME]
    profile.system_image = data[SYSTEM_IMAGE]
    profile.epld_image = data[EPLD_IMAGE]
    profile.kickstart_image = data[KICKSTART_IMAGE]
    profile.image_server_ip = data[IMAGE_SERVER_IP]
    profile.image_server_username = data[IMAGE_SERVER_USERNAME]
    profile.access_protocol = data[ACCESS_PROTOCOL]
    profile.updated_by = user

    if (profile.system_image is None and profile.epld_image is None and
       profile.kickstart_image is None):
        raise IgniteException(ERR_IMG_PRO_IMAGE_PATH_EMPTY)

    profile.save()
    return profile


def delete_profile(id):
    if id==1:
        raise IgniteException(ERR_CAN_NOT_DELETE_DEFAULT_IMAGE)
    try:
        ImageProfile.objects.get(pk=id).delete()
    except ProtectedError:
        raise IgniteException("Image profile is in use")
