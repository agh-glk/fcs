from django.forms.models import model_to_dict


def changed_fields(instance):
    """
    Returns list of names of model fields which has changed. If object is created, returns empty list
    """
    if instance.pk is not None:
        fields = model_to_dict(instance).keys()
        original = instance.__class__.objects.get(pk=instance.pk)
        changed = [field for field in fields if getattr(instance, field) != getattr(original, field)]
        return changed
    return []

