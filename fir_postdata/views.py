
from django.core.urlresolvers import resolve
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from json import loads
from datetime import datetime

from incidents import models
from incidents import views as incidents_views
from fir_nuggets.models import NuggetForm
from fir_nuggets import views as nuggets_views

from django import forms
class LandingForm(NuggetForm):
	new = forms.BooleanField(initial=True, required=False)
	event = forms.ModelChoiceField(queryset=models.Incident.objects.exclude(status='C'), required=False)

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

	def __init__(self, *args, **kwargs):
		super(LandingForm, self).__init__(*args, **kwargs)
		self.fields['raw_data'].widget.attrs['readonly'] = True

def get_external_values(querydict):
	formatted = u""
	for k, v in querydict.items():
		formatted += u"{0}: {1}\n".format(k, v)
	return formatted

@csrf_exempt
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
				else:
					form.errors.update(incident_form.errors)
	else:
		formatted = get_external_values(request.GET)
		form = LandingForm(initial={'raw_data':formatted, 'new': True, 'date': datetime.now(), 'start_timestamp': datetime.now(),'source':request.META.get('HTTP_REFERER', None)})
	return render(request, 'postdata/landing.html', {'form': form})
