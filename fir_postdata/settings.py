from django.conf import settings

def default_setting(name, default_value):
    value = getattr(settings, name, default_value)
    setattr(settings, name, value)


default_setting('POSTDATA_KEY_BLACKLIST', [])