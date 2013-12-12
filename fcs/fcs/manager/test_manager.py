from models import User, Quota, User, QuotaException, Task, CrawlingType, ServiceUnitPrice, Service
import models
import datetime
from fcs.backend.price_calculator import PriceCalculator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_pytest.conftest import pytest_funcarg__client, pytest_funcarg__django_client

class TestTask:
    def get_user(self):
        if self.user is None:
            self.user = User.objects.get(username='test_user')
        return self.user

    def setup(self):
        self.user = User.objects.create_user(username='test_user', password='test_pwd', email='test@gmail.pl')
        CrawlingType.objects.create(type=CrawlingType.TEXT)
        CrawlingType.objects.create(type=CrawlingType.LINKS)
        CrawlingType.objects.create(type=CrawlingType.PICTURES)
        Quota.objects.create(max_priority=10, max_tasks=1, max_links=1000, user=self.user)

    def teardown(self):
        self.user.delete()
        CrawlingType.objects.all().delete()

    def test_successful_task_creation(self):
        Task.create_task(self.get_user(), 'Task1', 3, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        assert self.get_user().task_set.count() == 1, 'Task was not properly saved!'

    def test_failed_task_creation(self):
        try:
            Task.create_task(self.get_user(), 'Task1', 15, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message == 'Task priority exceeds user quota!', 'Wrong exception message!'

        try:
            Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=1400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message == 'Task link limit exceeds user quota!', 'Wrong exception message!'

        try:
            Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            Task.create_task(self.get_user(), 'Task2', 5, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message == 'User has too many opened tasks!', 'Wrong exception message!'

    def test_change_priority(self):
        task = Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        assert 5 == task.priority
        task.change_priority(10)
        assert 10 == task.priority
        try:
            task.change_priority(15)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message == 'Task priority exceeds user quota!', 'Wrong exception message!'
        assert 10 == task.priority

    def test_pause_and_resume(self):
        task = Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
        assert task.active
        task.pause()
        assert not task.active
        task.resume()
        assert task.active

    def test_finish(self):
        task = Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                                [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)

        try:
            Task.create_task(self.get_user(), 'Task1', 5, timezone.now(),
                             [CrawlingType.objects.get(type=CrawlingType.TEXT)], 'onet.pl', max_links=400)
            assert False, 'Exception should be raised!'
        except QuotaException as e:
            assert e.message == 'User has too many opened tasks!', 'Wrong exception message!'
        task.stop()
        assert task.finished
        Task.create_task(self.get_user(), 'Task2', 5, timezone.now(), [CrawlingType.objects.get(type=CrawlingType.TEXT)],
                         'onet.pl', max_links=400)


class TestUserDataModel:
    def get_user(self):
        if self.user is None:
            self.user = User.objects.get(username='test_user')
        return self.user

    def setup(self):
        self.user = User.objects.create_user(username='test_user', password='test_pwd', email='test@gmail.pl')
        CrawlingType.objects.create(type=CrawlingType.TEXT)
        CrawlingType.objects.create(type=CrawlingType.LINKS)
        CrawlingType.objects.create(type=CrawlingType.PICTURES)
        Quota.objects.create(max_priority=10, max_tasks=1, max_links=1000, user=self.user)

    def teardown(self):
        self.user.delete()
        CrawlingType.objects.all().delete()

    def test_create_user_data(self):
        _user = self.get_user()
        try:
            models.initialise_user_object(_user)
        except ValidationError:
            assert False, 'Exception occured'

        assert _user.user_data.key != ''


class TestPriceCalculator:

    def setup(self):
        ServiceUnitPrice.objects.create(service_type=Service.INCREASE_MAX_LINKS,
                                        date_from=(timezone.now() - datetime.timedelta(days=4)),
                                        date_to=(timezone.now() - datetime.timedelta(minutes=1)),
                                                                      price=1).save()
        ServiceUnitPrice.objects.create(service_type=Service.INCREASE_MAX_LINKS,
                                        date_from=(timezone.now() + datetime.timedelta(minutes=10)),
                                        date_to=(timezone.now() + datetime.timedelta(minutes=30)),
                                                                      price=2).save()
        ServiceUnitPrice.objects.create(service_type=Service.INCREASE_MAX_LINKS,
                                        date_from=timezone.now() - datetime.timedelta(days=5),
                                        date_to=timezone.now() + datetime.timedelta(days=1, minutes=1), price=3).save()

    def teardown(self):
        ServiceUnitPrice.objects.all().delete()

    def test_price_calculator(self):
        _price_calculator = PriceCalculator()
        assert _price_calculator.get_current_price(Service.INCREASE_MAX_LINKS).price == 3
