from django import forms

from fir_nuggets.models import NuggetForm
from incidents import models as incident_models


class LandingForm(NuggetForm):
	new = forms.BooleanField(initial=True, required=False)
	event = forms.ModelChoiceField(queryset=incident_models.Incident.objects.exclude(status='C'), required=False)

	status = forms.CharField(required=True, widget=forms.HiddenInput, initial='O')
	subject = forms.CharField(required=False)
	concerned_business_lines = forms.ModelMultipleChoiceField(required=False, queryset=incident_models.BusinessLine.objects.all())
	category = forms.ModelChoiceField(queryset=incident_models.IncidentCategory.objects.all(), required=False)
	detection = forms.ModelChoiceField(required=False, queryset=incident_models.Label.objects.filter(group__name='detection'))
	severity = forms.ChoiceField(required=False, choices=incident_models.SEVERITY_CHOICES)
	description = forms.CharField(required=False, widget=forms.Textarea)
	is_incident = forms.BooleanField(initial=False, required=False)
	confidentiality = forms.ChoiceField(required=False, choices=incident_models.CONFIDENTIALITY_LEVEL, initial='1')

	is_major = forms.BooleanField(initial=False, required=False)
	actor = forms.ModelChoiceField(required=False, queryset=incident_models.Label.objects.filter(group__name='actor'))
	plan = forms.ModelChoiceField(required=False, queryset=incident_models.Label.objects.filter(group__name='plan'))

	def __init__(self, *args, **kwargs):
		super(LandingForm, self).__init__(*args, **kwargs)
		self.fields['raw_data'].widget.attrs['readonly'] = True
