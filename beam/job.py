# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import json
from os import path as p

from beam import ansible
from beam.cli import UI, is_force_mode
from beam.constans import (BEAM_FRAMEWORK_ROOT_DIR, BEAM_FRAMEWORK_ROLES_LIB_DIR, BEAM_ENVIRONMENTS_DIR,
                           BEAM_JOBS_DIR, BEAM_JOBS_ROLES_DIR, BEAM_FRAMEWORK_ROLES_INT_DIR)
from beam.errors import BEAMException, BEAM_GENERAL_ERROR, BEAM_SUCCESSFUL_TERMINATION, BEAMExitException


class Job(object):
    """Job representation with all job required data and tasks"""
    def __init__(self, environment, job, job_args, beam_options, ansible_options, project, *components):
        self.job = job
        self.job_args = job_args
        self.environment = environment
        self.beam_options = beam_options
        self.ansible_options = ansible_options
        self.project = project
        self.components = components

    def make_ansible_extra_os_env_vars(self, project, component):
        # order of searching ansible roles (higher overrides lower)
        roles_dirs = []
        if component:
            roles_dirs.append(p.join(component.root_path, BEAM_JOBS_ROLES_DIR))
        if project:
            roles_dirs.append(p.join(self.project.root_path, BEAM_JOBS_ROLES_DIR))
        roles_dirs.append(BEAM_FRAMEWORK_ROLES_LIB_DIR)
        roles_dirs.append(BEAM_FRAMEWORK_ROLES_INT_DIR)

        return {
            'ANSIBLE_ROLES_PATH': ':'.join(roles_dirs),
            'ANSIBLE_CONFIG': p.join(BEAM_FRAMEWORK_ROOT_DIR, 'ansible.cfg')
        }

    def make_ansible_extra_vars(self, project, component):
        project_d = {
            'NAME': project.name,
            'REPO_URL': project.repo_ssh_url,
            'REPO_NAME': project.repo_name,
            'ENVIRONMENT': self.environment
        } if project else {}

        component_d = {
            'NAME': component.name,
            'REPO_URL': component.repo_ssh_url,
            'REPO_NAME': component.repo_name,
        } if component else {}

        job_d = {
            'NAME': self.job,
            'ARGS': self.job_args
        }
        extra_vars = {}
        extra_vars.update({'PROJECT': project_d}) if project_d else extra_vars
        extra_vars.update({'COMPONENT': component_d}) if component_d else extra_vars
        extra_vars.update({'JOB': job_d})
        extra_vars.update({'BEAM_ROOT_DIR': BEAM_FRAMEWORK_ROOT_DIR})
        return json.dumps({'__RAW_BEAM_VARS': extra_vars})

    def confirm_job_run(self):
        fg = UI.ansi.fg
        project_line = UI.render(UI.Colorized(fg.orange, UI.Boldized('%s' % self.project.name)),
                                 UI.Colorized(fg.grey, '  [%s]' % self.project.root_path))
        component_lines = [UI.render(UI.Colorized(fg.blue, UI.Boldized('%s' % component.name)),
                                   UI.Colorized(fg.grey, '  [%s]\n' % component.root_path)) for component in self.components]
        UI.output(UI.Colorized(fg.lightred, '\n***CAUTION***\n'), '\nYou are going to run the job: ',
                  UI.Colorized(fg.cyan, UI.Boldized('%s' % self.job)), '\n..........with job arguments: ',
                  UI.Colorized(fg.cyan, UI.Boldized('%s' % self.job_args)), '\n..............on environment: ',
                  UI.Colorized(fg.cyan, UI.Boldized('%s' % self.environment)), '\non project: ', '%s' % project_line,
                  "\n\nThis job will be performed on following components from the project:",
                  '\n--> ', '--> '.join(component_lines),
                  '\n\n ', UI.Colorized(fg.lightred, 'PROCEED? [Y/N] '), ' ')
        if is_force_mode():
            UI.output("\nFORCE MODE ACTIVATED (confirmed automatically)")
        else:
            choice = raw_input().lower()
            if choice != 'y':
                raise BEAMException('Job terminated by user!')

    def run_subsequent_job(self, target, job_header, ansible_options=None):
        exit_code = status = None
        job_header = job_header + ' job: %s on %s: %s...'
        if not target or not getattr(target, 'type', None):
            raise BEAMException(
                'Job can be run on project or component only, check if Job instance has been instantiated properly.')
        UI.output(UI.Frame(UI.STATUS_PENDING, job_header % (self.job, target.type, target.name)))
        playbook = p.join(target.root_path, BEAM_JOBS_DIR, '%s' % self.job, 'main.yml')
        if p.isfile(playbook):
            environ = p.join(self.project.root_path, BEAM_ENVIRONMENTS_DIR, self.environment)
            extra_vars = self.make_ansible_extra_vars(self.project, None if target.type == 'project' else target)
            extra_os_env = self.make_ansible_extra_os_env_vars(self.project, None if target.type == 'project' else target)
            ansible_options = (ansible_options or []) + (self.ansible_options or [])
            exit_code, exit_msg = ansible.run_playbook(playbook, environ, extra_vars, extra_os_env, ansible_options)

            if exit_code:
                status = UI.STATUS_FAIL
                UI.output(UI.Frame(status, job_header % (self.job, target.type, target.name),
                                   'ansible terminated with error code: %s (%s), ' % (exit_code, exit_msg),
                                   'check ansible output above for details.', status_code=UI.STATUS_FAIL))
            else:
                status = UI.STATUS_SUCCESS
                UI.output(UI.Frame(status, job_header % (self.job, target.type, target.name), ' DONE!'))
        else:
            status = UI.STATUS_SKIPPED
            UI.output(UI.Frame(status, job_header % (self.job, target.type, target.name),
                               "\nno %s.yml job playbook found for %s." % (self.job, target.name)))
        return exit_code, status

    def validate(self):
        exit_code, status = self.run_subsequent_job(self.project, 'Validating', ansible_options=['--syntax-check'])
        if exit_code:
            raise BEAMExitException("Validating job %s playbooks FAILED" % self.job, exit_code)

        for component in self.components:
            exit_code, exit_msg = self.run_subsequent_job(component, 'Validating', ansible_options=['--syntax-check'])
            if exit_code:
                raise BEAMExitException("Validating job %s playbooks FAILED" % self.job, exit_code)

    def run(self, confirm=True):
        """Runs job on job's project and components"""
        summary = []
        if confirm:
            self.confirm_job_run()
        # run job
        exit_code, status = self.run_subsequent_job(self.project, 'Running')
        summary.append((self.project.name, exit_code, status))
        for component in self.components:
            exit_code, status = self.run_subsequent_job(component, 'Running')
            summary.append((component.name, exit_code, status))
        # prepare summary
        exit_code = BEAM_GENERAL_ERROR if any([item[1] for item in summary]) else BEAM_SUCCESSFUL_TERMINATION
        item_line_t = "Job: %(job)s for %(target)s finished with status: %(status)s\n"
        summary_msg = [item_line_t % {'job': self.job, 'target': item[0], 'status': UI.statuses_def[item[2]][0]}
                       for item in summary]
        status_info = "with errors" if exit_code else "OK"
        exit_msg = 'Job: %s finished %s' % (self.job, status_info), UI.ansi.reset, '\n\nJob Summary:\n\n', summary_msg
        return exit_code, exit_msg
