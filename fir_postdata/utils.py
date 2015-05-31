from fir_postdata.settings import settings


def get_external_values(querydict):
	formatted = u""
	for k, v in querydict.items():
		if k not in settings.POSTDATA_KEY_BLACKLIST:
			formatted += u"{0}: {1}\n".format(k, v)
	return formatted