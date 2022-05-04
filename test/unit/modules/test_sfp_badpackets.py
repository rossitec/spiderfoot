# test_sfp_badpackets.py
import pytest
import unittest

from modules.sfp_badpackets import sfp_badpackets
from sflib import SpiderFoot
from spiderfoot import SpiderFootEvent, SpiderFootTarget


@pytest.mark.usefixtures
class TestModulebadpackets(unittest.TestCase):
    """
    Test modules.sfp_badpackets
    """

    def test_opts(self):
        module = sfp_badpackets()
        self.assertEqual(len(module.opts), len(module.optdescs))

    def test_setup(self):
        """
        Test setup(self, sfc, userOpts=dict())
        """
        sf = SpiderFoot(self.default_options)

        module = sfp_badpackets()
        module.setup(sf, dict())

    def test_watchedEvents_should_return_list(self):
        module = sfp_badpackets()
        self.assertIsInstance(module.watchedEvents(), list)

    def test_producedEvents_should_return_list(self):
        module = sfp_badpackets()
        self.assertIsInstance(module.producedEvents(), list)

    def test_parseApiResponse_nonfatal_http_response_code_should_not_set_errorState(self):
        sf = SpiderFoot(self.default_options)

        http_codes = ["200", "400"]
        for code in http_codes:
            with self.subTest(code=code):
                module = sfp_badpackets()
                module.setup(sf, dict())
                result = module.parseApiResponse({"code": code, "content": None})
                self.assertIsNone(result)
                self.assertFalse(module.errorState)

    def test_parseApiResponse_fatal_http_response_error_code_should_set_errorState(self):
        sf = SpiderFoot(self.default_options)

        http_codes = ["401", "403"]
        for code in http_codes:
            with self.subTest(code=code):
                module = sfp_badpackets()
                module.setup(sf, dict())
                result = module.parseApiResponse({"code": code, "content": None})
                self.assertIsNone(result)
                self.assertTrue(module.errorState)

    def test_handleEvent_no_api_key_should_set_errorState(self):
        """
        Test handleEvent(self, event)
        """
        sf = SpiderFoot(self.default_options)

        module = sfp_badpackets()
        module.setup(sf, dict())

        target_value = 'example target value'
        target_type = 'IP_ADDRESS'
        target = SpiderFootTarget(target_value, target_type)
        module.setTarget(target)

        event_type = 'ROOT'
        event_data = 'example data'
        event_module = ''
        source_event = ''
        evt = SpiderFootEvent(event_type, event_data, event_module, source_event)

        result = module.handleEvent(evt)

        self.assertIsNone(result)
