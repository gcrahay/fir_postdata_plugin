
from django.core.urlresolvers import resolve
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponseRedirect

from json import loads
import base64
import shlex
from datetime import datetime

from incidents import models
from incidents import views as incidents_views
from fir_nuggets.models import NuggetForm
from fir_nuggets import views as nuggets_views

from django import forms
class LandingForm(NuggetForm):
	new = forms.BooleanField(initial=True, required=False)
	event = forms.ModelChoiceField(queryset=models.Incident.objects.exclude(status='C'), required=False)
	b64_values = forms.CharField(required=True, widget=forms.HiddenInput)

	status = forms.CharField(required=True, widget=forms.HiddenInput, initial='O')
	subject = forms.CharField(required=False)
	concerned_business_lines = forms.ModelMultipleChoiceField(required=False, queryset=models.BusinessLine.objects.all())
	category = forms.ModelChoiceField(queryset=models.IncidentCategory.objects.all(), required=False)
	detection = forms.ModelChoiceField(required=False, queryset=models.Label.objects.filter(group__name='detection'))
	severity = forms.ChoiceField(required=False, choices=models.SEVERITY_CHOICES)
	description = forms.CharField(required=False, widget=forms.Textarea)
	is_incident = forms.BooleanField(initial=False, required=False)
	confidentiality = forms.ChoiceField(required=False, choices=models.CONFIDENTIALITY_LEVEL, initial='1')

	is_major = forms.BooleanField(initial=False, required=False)
	actor = forms.ModelChoiceField(required=False, queryset=models.Label.objects.filter(group__name='actor'))
	plan = forms.ModelChoiceField(required=False, queryset=models.Label.objects.filter(group__name='plan'))
	#status = forms.ChoiceField(required=False, choices=models.STATUS_CHOICES, initial='O')

	def __init__(self, *args, **kwargs):
		super(LandingForm, self).__init__(*args, **kwargs)
		self.fields['raw_data'].widget.attrs['readonly'] = True

class DisplayLandingForm(models.IncidentForm, NuggetForm):
	pass


def addslashes(value):
	return value.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")

def get_external_values(querydict):
	base_64= u""
	formatted = u""
	for k, v in querydict.items():
		formatted += u"{0}: {1}\n".format(k, v)
		base_64 += u"{0}=\"{1}\" ".format(k, addslashes(v))
	if len(base_64) and base_64[-1] == ' ':
		base_64 = base_64[:-1]
	return base64.b64encode(base_64.encode("utf-8")), formatted

def b64_to_formatted(raw):
	formatted = u""
	base_64 = base64.b64decode(raw)
	pairs = dict(token.split('=', 1) for token in shlex.split(base_64))
	for k, v in pairs.items():
		formatted += u"{0}: {1}\n".format(k, v.decode('utf-8'))
	return formatted


@csrf_exempt
def postdata_landing(request):
	if request.POST:
		form = LandingForm(request.POST)
		if form.is_valid():
			if not form.cleaned_data.get('new', False):
				print "No create"
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
					if 'raw_data' in request.POST and 'b64_values' in request.POST:
						raw = request.POST.get('raw_data')
						formatted = request.POST.get('b64_values')
					else:
						return redirect('dashboard:main')
			else:
				incident_form = models.IncidentForm(request.POST)
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
					return redirect('events:new')
				else:
					form.errors.update(incident_form.errors)
	else:
		raw, formatted = get_external_values(request.GET)
		form = LandingForm(initial={'raw_data':formatted, 'new': True, 'b64_values': raw, 'date': datetime.now(), 'start_timestamp': datetime.now(),'source':request.META.get('HTTP_REFERER', None)})
	return render(request, 'postdata/landing.html', {'form': form})
