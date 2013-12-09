from fcs.manager.models import ServiceUnitPrice
import datetime
from django.db.models import Q


class PriceCalculator():

    def __init__(self):
        pass

    @staticmethod
    def get_current_price(service_type):
        _results = ServiceUnitPrice.objects.filter(Q(service_type=service_type) & Q(date_to__gte=datetime.datetime.combine(datetime.datetime.now(),
                                                                                  datetime.time.min)))
        return list(_results)

    def calculate_price_increase_quota(self, service_type, additional_resource_pool):
        _price = self.get_current_price(service_type).price *\
                 (additional_resource_pool > 0 and additional_resource_pool or 1)
        return _price




