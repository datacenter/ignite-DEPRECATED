from django.db import Error
from django.http import JsonResponse
from rest_framework import status

from administration.models import AAAServer
from bootstrap.models import SwitchBootDetail
from config.models import Profile as ConfigProfile
from config.models import Configlet
from discovery.models import DiscoveryRule
from fabric.models import Link, Switch, Topology, SwitchConfig
from feature.models import Profile as FeatureProfile
from feature.models import Feature
from image.models import ImageProfile
from pool.models import Pool
from switch.models import LineCard, SwitchModel
from utils.exception import IgniteException, TokenException
from utils.exception import UnauthorizedException
from workflow.models import Workflow, Task
from group.models import *

import logging
logger = logging.getLogger(__name__)


# error messages
ERR_MSG = "error_message"


class ExceptionMiddleware(object):

    def process_exception(self, request, exception):
        msg = ""
        code = status.HTTP_500_INTERNAL_SERVER_ERROR

        # database exceptions
        if isinstance(exception, Error):
            msg = exception.message
            code = status.HTTP_500_INTERNAL_SERVER_ERROR
        # model exceptions
        elif isinstance(exception, AAAServer.DoesNotExist):
            msg = "AAAServer does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, ConfigProfile.DoesNotExist):
            msg = "Config Profile does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, DiscoveryRule.DoesNotExist):
            msg = "Discovery Rule does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, FeatureProfile.DoesNotExist):
            msg = "Feature Profile does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, ImageProfile.DoesNotExist):
            msg = "Image Profile does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, LineCard.DoesNotExist):
            msg = "Line Card does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Link.DoesNotExist):
            msg = "Link does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Pool.DoesNotExist):
            msg = "Pool does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Switch.DoesNotExist):
            msg = "Switch does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, SwitchBootDetail.DoesNotExist):
            msg = "Switch Boot Detail does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, SwitchModel.DoesNotExist):
            msg = "Switch Model does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Task.DoesNotExist):
            msg = "Task does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Topology.DoesNotExist):
            msg = "Topology does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Workflow.DoesNotExist):
            msg = "Workflow does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Group.DoesNotExist):
            msg = "Group does not exist"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, GroupSwitch.DoesNotExist):
            msg = "switch does not exist in the group"
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Job.DoesNotExist):
            msg = "Job does not exist "
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Task.DoesNotExist):
            msg = "Task does not exist "
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Feature.DoesNotExist):
            msg = "Feature does not exist "
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, Configlet.DoesNotExist):
            msg = "Configlet does not exist "
            code = status.HTTP_404_NOT_FOUND
        elif isinstance(exception, SwitchConfig.DoesNotExist):
            msg = "Switch Running Config does not exist "
            code = status.HTTP_404_NOT_FOUND

        # ignite exceptions
        elif isinstance(exception, IgniteException):
            msg = exception.message
            code = status.HTTP_400_BAD_REQUEST
        # Token exception
        elif isinstance(exception, TokenException):
            msg = exception.message
            code = status.HTTP_401_UNAUTHORIZED
        # Unauthorized exception
        elif isinstance(exception, UnauthorizedException):
            msg = exception.message
            code = status.HTTP_403_FORBIDDEN

        if msg:
            logger.debug(msg)
            return JsonResponse({ERR_MSG: msg}, status=code)

        return None
