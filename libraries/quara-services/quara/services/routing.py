from copy import deepcopy

import fastapi

from .mixins import BrokerMixin, DatabaseMixin, SchedulerMixin, StorageMixin


class ServiceRouter(
    BrokerMixin, DatabaseMixin, StorageMixin, SchedulerMixin, fastapi.routing.APIRouter
):
    pass


__FASTAPI_API_ROUTER__ = deepcopy(fastapi.routing.APIRouter)
fastapi.routing.APIRouter = ServiceRouter  # type: ignore
