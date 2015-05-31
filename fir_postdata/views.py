from json import loads
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test

from django.core.urlresolvers import resolve
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from incidents.models import IncidentForm
from incidents import views as incidents_views
from fir_nuggets import views as nuggets_views

from fir_postdata.forms import LandingForm

def get_external_values(querydict):
	formatted = u""
	for k, v in querydict.items():
		formatted += u"{0}: {1}\n".format(k, v)
	return formatted

@csrf_exempt
@login_required
@user_passes_test(incidents_views.is_incident_handler)
def postdata_landing(request):
	if request.POST:
		form = LandingForm(request.POST)
		if form.is_valid():
			if not form.cleaned_data.get('new', False):
				event = form.cleaned_data.get('event', None)
				if event is not None:
					add_return =  nuggets_views.new(request, event.pk)
					try:
						result = loads(add_return)
					except:
						result = {'status':'error'}
					if isinstance(result, dict) and result.get('status', 'error') == 'success':
						messages.info(request, 'Nugget added to event')
					else:
						messages.error(request, "Cannot add nugget to event")
					return redirect('incidents:details', incident_id=event.id)
				else:
					messages.error(request, "You must choose an event or create one")
					if 'raw_data' not in request.POST:
						return redirect('dashboard:main')
			else:
				incident_form = IncidentForm(request.POST)
				if incident_form.is_valid():
					creation =  incidents_views.new_event(request)
					redirected = resolve(creation.url)
					print redirected
					if redirected.namespace in ['incidents', 'events'] and redirected.url_name == 'details':
						event_id = redirected.kwargs.get('incident_id')
						add_return =  nuggets_views.new(request, event_id)
						try:
							result = loads(add_return)
						except:
							result = {'status':'error'}
						if isinstance(result, dict) and result.get('status', 'error') == 'success':
							messages.info(request, 'Nugget added to event')
						else:
							messages.error(request, "Cannot add nugget to event")
						return creation
				else:
					form.errors.update(incident_form.errors)
		elif "raw_data" in form.errors:
			formatted = get_external_values(request.POST)
			form = LandingForm(initial={'raw_data':formatted, 'new': True,
										'date': datetime.now(), 'start_timestamp': datetime.now(),
										'source':request.META.get('HTTP_REFERER', None)})
	else:
		formatted = get_external_values(request.GET)
		form = LandingForm(initial={'raw_data':formatted, 'new': True,
									'date': datetime.now(), 'start_timestamp': datetime.now(),
									'source':request.META.get('HTTP_REFERER', None)})
	return render(request, 'postdata/landing.html', {'form': form})
