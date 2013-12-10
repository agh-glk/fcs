from fcs.manager.models import ServiceUnitPrice, Service
import datetime
from django.db.models import Q
from django.utils import timezone


class PriceCalculator():

    def __init__(self):
        pass

    @staticmethod
    def get_current_price(service_type):
        _results = ServiceUnitPrice.objects.filter(Q(service_type=service_type)
                                                   & Q(date_to__gt=timezone.now()) & Q(date_from__lt=timezone.now()))
        if len(_results) < 1:
            raise Exception('Missing entry in db for ServiceUnitPrice!')
        return sorted(_results, key=lambda x: x.price)[0]

    def calculate_price_increase_quota(self, service_type, additional_resource_pool):
        _price = self.get_current_price(service_type).price *\
                 (additional_resource_pool > 0 and additional_resource_pool or 1)
        return _price




