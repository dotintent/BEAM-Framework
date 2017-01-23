# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import subprocess
import os

from beam.constans import BEAM_FRAMEWORK_ROOT_DIR


ansible_error_codes = {
    1: 'general error',
    2: 'host failed',
    3: 'host unreachable',
    4: 'playbook parser error',
    5: 'bad or incomplete options passed',
    99: 'execution interrupted by user',
    250: 'unexpected exception occured'
}


def run_playbook(playbook, inventory_path, extra_vars, extra_os_environment_vars, ansible_options=None):
    osenv = os.environ
    osenv.update(extra_os_environment_vars)
    # add BEAM's ansible first on PYTHONPATH to start BEAM's ansible, not system installed
    osenv['PYTHONPATH'] = ':'.join([os.path.join(BEAM_FRAMEWORK_ROOT_DIR, 'ansible', 'lib'), osenv.get('PYTHONPATH', '')])
    ansible_paybook_tool = os.path.join(BEAM_FRAMEWORK_ROOT_DIR, 'ansible', 'bin', 'ansible-playbook')
    ansible_options = ansible_options if ansible_options else []
    ansible_inventory = '-i %s' % inventory_path if inventory_path else ''
    exit_code = subprocess.call([ansible_paybook_tool, playbook] + ansible_inventory.split() + [
                                '--extra-vars=%s' % extra_vars] + ansible_options, env=osenv)
    return exit_code, ansible_error_codes.get(exit_code, 'Unknown error.')
