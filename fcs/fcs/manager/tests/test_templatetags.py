from django.forms.forms import BoundField
from django.forms.widgets import PasswordInput
from django import forms
from fcs.manager.templatetags.custom_tags import is_class, alert_tag
from accounts.forms import LoginForm


class TestTemplateTags:
    def test_is_class(self):
        form = LoginForm()
        field = BoundField(form, forms.CharField(), 'name')
        assert is_class(field, 'TextInput')
        field = BoundField(form, forms.CharField(widget=PasswordInput()), 'name')
        assert is_class(field, 'PasswordInput')

    def test_alert_tag(self):
        assert alert_tag('debug') == ''
        assert alert_tag('info') == 'alert-info'
        assert alert_tag('success') == 'alert-success'
        assert alert_tag('warning') == 'alert-warning'
        assert alert_tag('error') == 'alert-danger'
        assert alert_tag('bad_tag') == 'alert-info'