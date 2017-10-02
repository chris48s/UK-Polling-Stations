# -*- coding: utf-8 -*-
import os
import shutil
import signal
import tempfile
from contextlib import contextmanager
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.management import call_command
from aloe import before, after, around, step, world
import aloe_webdriver.django
from selenium.webdriver import PhantomJS
from selenium.common.exceptions import TimeoutException
import vcr


class PhantomWithRetry(PhantomJS):

    def _dispatch(self, l_call, l_args, d_call, d_args):
        for i in range(2):
            try:
                return super()._dispatch(l_call, l_args, d_call, d_args)
            except TimeoutException:
                pass
        raise TimeoutException


selenium_vcr = vcr.VCR()
# We need to ignore localhost as selenium communicates over local http
# to interact with the 'browser'
selenium_vcr.ignore_localhost = True

temp_dir = tempfile.mkdtemp()


@before.all
def before_all():
    # build static assets into a temporary location
    settings.STATIC_ROOT=temp_dir
    call_command('collectstatic', interactive=False, verbosity=0)

@after.all
def after_all():
    try:
        # attempt to clean up static assets
        shutil.rmtree(temp_dir)
    except OSError:
        # if it fails, just leave our mess behind
        pass

@before.each_example
def setup(scenario, outline, steps):
    # TODO Set browser in django.conf.settings
    # world.browser = webdriver.Chrome()
    world.browser = PhantomWithRetry()
    world.browser.set_page_load_timeout(10)
    world.browser.set_script_timeout(10)

    with open(os.devnull, "w") as f:
        call_command('loaddata', 'test_routing.json', stdout=f)
        call_command('loaddata', 'newport_council.json', stdout=f)

@step('No errors were thrown')
def no_errors(step):
    assert\
        len(world.browser.get_log('browser')) == 0,\
        "JavaScript errors were logged:\n %s" %\
        (world.browser.get_log('browser'))

@after.each_example
def take_down(scenario, outline, steps):
    try:
        # we can do this the easy way...
        world.browser.quit()
    except OSError:
        # ..or we can do this the hard way
        world.browser.service.process.send_signal(signal.SIGTERM)

@before.each_step
def each_step(step):
    print(str(step))

@around.each_step
@contextmanager
def mock_mapit(step):
    feature = slugify(step.feature.text)
    scenario = slugify(step.scenario.text)
    step_slug = slugify(step.text)
    path = 'test_data/vcr_cassettes/integration_tests/{}/{}/{}.yaml'
    with selenium_vcr.use_cassette(path.format(feature, scenario, step_slug)):
        yield
