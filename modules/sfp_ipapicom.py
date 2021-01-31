# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         sfp_ipapicom
# Purpose:      SpiderFoot plug-in to identify the Geo-location of IP addresses
#               identified by other modules using ipapi.com
#
# Author:      Krishnasis Mandal <krishnasis@hotmail.com>
#
# Created:     29/01/2021
# Copyright:   (c) Steve Micallef
# Licence:     GPL
# -------------------------------------------------------------------------------

import json
import time

from spiderfoot import SpiderFootEvent, SpiderFootPlugin


class sfp_ipapicom(SpiderFootPlugin):

    meta = {
        'name': "ipapi.com",
        'summary': "Queries ipapi.com to identify geolocation of IP Addresses using ipapi.com API",
        'flags': ["apikey"],
        'useCases': ["Footprint", "Investigate", "Passive"],
        'categories': ["Real World"],
        'dataSource': {
            'website': "https://ipapi.com/",
            'model': "FREE_AUTH_LIMITED",
            'references': [
                "https://ipapi.com/documentation"
            ],
            'apiKeyInstructions': [
                "Visit https://ipapi.com/",
                "Register a free account",
                "Browse to https://ipapi.com/dashboard",
                "Your API Key will be listed under Your API Access Key",
            ],
            'favIcon': "https://ipapi.com/site_images/ipapi_shortcut_icon.ico",
            'logo': "https://ipapi.com/site_images/ipapi_icon.png",
            'description': "ipapi provides an easy-to-use API interface allowing customers "
            "to look various pieces of information IPv4 and IPv6 addresses are associated with. "
            "For each IP address processed, the API returns more than 45 unique data points, "
            "such as location data, connection data, ISP information, time zone, currency and security assessment data.",
        }
    }

    # Default options
    opts = {
        'api_key': '',
    }

    # Option descriptions
    optdescs = {
        'api_key': "API Key for ipapi.com",
    }

    results = None

    def setup(self, sfc, userOpts=dict()):
        self.sf = sfc
        self.results = self.tempStorage()

        for opt in list(userOpts.keys()):
            self.opts[opt] = userOpts[opt]

    # What events is this module interested in for input
    def watchedEvents(self):
        return [
            "IP_ADDRESS",
            "IPV6_ADDRESS"
        ]

    # What events this module produces
    # This is to support the end user in selecting modules based on events
    # produced.
    def producedEvents(self):
        return [
            "GEOINFO",
            "RAW_RIR_DATA"
        ]

    def query(self, qry):
        queryString = f"http://api.ipapi.com/api/{qry}?access_key={self.opts['api_key']}"

        res = self.sf.fetchUrl(queryString,
                               timeout=self.opts['_fetchtimeout'],
                               useragent=self.opts['_useragent'])

        if res['content'] is None:
            self.sf.info(f"No ipapi.com data found for {qry}")
            return None
        try:
            return json.loads(res['content'])
        except Exception as e:
            self.sf.debug(f"Error processing JSON response: {e}")
            return None

    # Handle events sent to this module
    def handleEvent(self, event):
        eventName = event.eventType
        srcModuleName = event.module
        eventData = event.data

        self.sf.debug(f"Received event, {eventName}, from {srcModuleName}")

        if self.opts['api_key'] == "":
            self.sf.error("You enabled sfp_ipapicom but did not set an API key!")
            self.errorState = True
            return

        # Don't look up stuff twice
        if eventData in self.results:
            self.sf.debug(f"Skipping {eventData}, already checked.")
            return None
        else:
            self.results[eventData] = True

        data = self.query(eventData)

        if data.get('country_name'):
            location = ', '.join(filter(None, [data.get('city'), data.get('region_name'), data.get('region_code'), data.get('country_name'), data.get('country_code')]))
            location += f"\n-Latitude: {data.get('latitude')}\n-Longitude: {data.get('longitude')}"
            evt = SpiderFootEvent('GEOINFO', location, self.__name__, event)
            self.notifyListeners(evt)

            evt = SpiderFootEvent('RAW_RIR_DATA', str(data), self.__name__, event)
            self.notifyListeners(evt)


# End of sfp_ipapicom class