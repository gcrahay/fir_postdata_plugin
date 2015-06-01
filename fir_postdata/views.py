from datetime import datetime

from django.core.urlresolvers import resolve
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import ugettext_lazy as _

from incidents.models import IncidentForm
from incidents import views as incidents_views

from fir_postdata.forms import LandingForm
from fir_postdata.utils import get_external_values, add_nugget_to_event


@csrf_exempt
@login_required
@user_passes_test(incidents_views.is_incident_handler)
def postdata_landing(request):
	if request.method == 'POST':
		form = LandingForm(request.POST)
		if form.is_valid():
			if not form.cleaned_data.get('new', False):
				event = form.cleaned_data.get('event', None)
				if event is not None:
					if event.is_incident:
						redirect_object = redirect('incidents:details', incident_id=event.id)
					else:
						redirect_object = redirect('events:details', incident_id=event.id)
					return add_nugget_to_event(request, event.pk, redirect_object)
				else:
					messages.error(request, _('You must select an event or create one'))
					if 'raw_data' not in request.POST:
						return redirect('dashboard:main')
			else:
				incident_form = IncidentForm(request.POST)
				if incident_form.is_valid():
					creation = incidents_views.new_event(request)
					redirected = resolve(creation.url)
					if redirected.namespace in ['incidents', 'events'] and redirected.url_name == 'details':
						event_id = redirected.kwargs.get('incident_id')
						return add_nugget_to_event(request, event_id, creation)
				else:
					form.errors.update(incident_form.errors)
		elif 'raw_data' in form.errors:
			formatted = get_external_values(request.POST)
			form = LandingForm(initial={'raw_data': formatted, 'new': True,
										'source': request.META.get('HTTP_REFERER', None)})
	else:
		formatted = get_external_values(request.GET)
		form = LandingForm(initial={'raw_data': formatted, 'new': True,
									'date': datetime.now(), 'start_timestamp': datetime.now(),
									'source': request.META.get('HTTP_REFERER', None)})
	return render(request, 'postdata/landing.html', {'form': form})
