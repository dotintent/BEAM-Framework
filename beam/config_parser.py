# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import ConfigParser
from os import path as p

import re

from beam.constans import BEAM_PROJECT_CONF_NAME, BEAM_ROOT_DIR
from beam.cli import UI
from beam.errors import BEAMConfParserException


_sentinel = object()


class PBase(object):
    """Base class for Project and Component with base conf files parser"""
    type = None

    def __init__(self, conf_file_path):
        self.conf_file = conf_file_path
        self.parser = ConfigParser.RawConfigParser()
        self.parser.optionxform = str  # make option names case sensitive
        if not self.parser.read(conf_file_path or ''):
            raise BEAMConfParserException(
                'Configuration file %s has improper format or file not found.' % conf_file_path)
        self.root_path = p.dirname(p.dirname(self.conf_file))
        self.name = self.get_option(str, 'NAME', self.type)
        self.check_for_disallowed_characters('NAME', self.name)
        self.description = self.get_option(str, 'DESCRIPTION', self.type)
        self.repo_ssh_url = self.get_option(str, 'REPO_SSH_URL', self.type)
        self.check_for_disallowed_characters('REPO_SSH_URL', self.repo_ssh_url)
        self.repo_name = p.basename(self.repo_ssh_url.split(':')[-1])[:-4]  # TODO port support
        self.repo_host = p.basename(self.repo_ssh_url.split(':')[0])[4:]  # TODO port support

    def __str__(self):
        return '%s %s (%s)' % (self.__class__.__name__, self.name, self.description)

    def check_for_disallowed_characters(self, what, text):
        if re.sub('[,\s\t\v\n\f]', '', text) != text:
            raise BEAMConfParserException(
                '%s in %s is %r' % (what if what else 'Component section name', self.conf_file, text) +
                ' and contains disallowed whitespaces or commas\n')

    def get_option(self, opttype, option, section, default=_sentinel):
        """Trying to get option value with given type from given section"""
        if self.parser.has_option(section, option):
            if isinstance(opttype, bool):
                opttype = bool
                get_method = self.parser.getboolean
            else:
                get_method = self.parser.get
            return get_method(section, option)

        # no option found in given section but check for default value
        if default is not _sentinel:
            msg = '\nNOTICE: option %s not set in %s, using given default value for that option: %s' % (
                option, self.conf_file, default)
            UI.output(msg)
            return default
        else:
            args = option, self.conf_file
            raise BEAMConfParserException('Option %s not set in %s and no its default value given.' % args)


class Project(PBase):
    type = 'project'

    def __init__(self, root_path):
        conf_file_path = p.join(root_path, BEAM_ROOT_DIR, BEAM_PROJECT_CONF_NAME)
        if not p.isfile(conf_file_path):
            args = (BEAM_ROOT_DIR, BEAM_PROJECT_CONF_NAME)
            raise BEAMConfParserException(
                'Cannot find %s directory with %s in expected project directory:\n' % args +
                '\n--> %s\n' % root_path +
                '\nHINT: The beam-cli tool must be run always from root of project directory (or set it by -p option).')
        super(Project, self).__init__(conf_file_path)
        # gather active components
        active_components_names = {}
        for section in self.parser.sections():
            if section == self.type:
                continue
            self.check_for_disallowed_characters(None, section)
            if self.get_option(bool, 'ACTIVE', section):
                active_components_names[section] = self.get_option(str, 'REPO_SSH_URL', section)
                self.check_for_disallowed_characters('REPO_SSH_URL', active_components_names[section])
        self.components = active_components_names


class Component(PBase):
    type = 'component'

    def __init__(self, conf_file_path):
        super(Component, self).__init__(conf_file_path)
