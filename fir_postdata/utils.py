from json import loads

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from fir_nuggets import views as nuggets_views

from fir_postdata.settings import settings


def get_external_values(querydict):
	formatted = u""
	for k, v in querydict.items():
		if k not in settings.POSTDATA_KEY_BLACKLIST:
			formatted += u"{0}: {1}\n".format(k, v)
	return formatted

def add_nugget_to_event(request, event_id, redirect_object):
		add_return = nuggets_views.new(request, event_id)
		try:
			result = loads(add_return.content)
		except:
			result = {'status': 'error'}
		if isinstance(result, dict) and result.get('status', 'error') == 'success':
			messages.info(request, _('Nugget added to event'))
		else:
			messages.error(request, _('Cannot add nugget to event'))
		return redirect_object