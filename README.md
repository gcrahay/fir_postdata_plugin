# External data plugin for FIR - Fast Incident Response

[FIR](https://github.com/certsocietegenerale/FIR) (Fast Incident Response by [CERT Société générale](https://cert.societegenerale.com/)) is an cybersecurity incident management platform designed with agility and speed in mind. It allows for easy creation, tracking, and reporting of cybersecurity incidents.

# Features

This plugin allows an external application to add "[nuggets](https://github.com/certsocietegenerale/FIR/tree/master/fir_nuggets)" to events via a `POST` or `GET` request. 

# Install

Follow the generic plugin installation instructions in [the FIR wiki](https://github.com/certsocietegenerale/FIR/wiki/Plugins).
Make sur the following line is included in the `urlpatterns` variable in `fir/urls.py`:

```
url(r'^postdata/', include('fir_postdata.urls', namespace='postdata')),
```