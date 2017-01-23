# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
from os import getcwd, listdir, path as p

import sys

from beam import argparse
from beam.constans import BEAM_ROOT_DIR, BEAM_COMPONENT_CONF_NAME
from beam.errors import BEAMException, BEAMCommandlineParserException


QUIET_MODE = FORCE_MODE = False


def is_force_mode():
    return FORCE_MODE


class UI(object):
    """BEAM UI"""

    class ansi(object):
        """ANSI codes to colorize console output. Not all codes are widely supported"""
        reset =             '\033[0m'   # noqa
        bold =              '\033[1m'   # noqa might also make fg color brighter instead/with making font bold
        faint =             '\033[2m'   # noqa decreases insensitivity of fg color
        standout =          '\033[3m'   # noqa italic
        underline =         '\033[4m'   # noqa
        blink =             '\033[5m'   # noqa
        inverse =           '\033[7m'   # noqa swap fg and bg colors, may be used to get real white bg and black text
        strikethrough =     '\033[9m'   # noqa
        hidden =            '\033[8m'   # noqa
        crossedout =        '\033[9m'   # noqa
        nostandout =        '\033[23m'  # noqa no standout
        nounderline =       '\033[24m'  # noqa no underlined
        noblink =           '\033[25m'  # noqa no blink
        noreverse =         '\033[27m'  # noqa no reverse

        class fg(object):
            current =       ''          # noqa
            default =       '\033[39m'  # noqa
            black =         '\033[30m'  # noqa
            red =           '\033[31m'  # noqa
            green =         '\033[32m'  # noqa
            orange =        '\033[33m'  # noqa
            blue =          '\033[34m'  # noqa
            magenta =       '\033[35m'  # noqa
            cyan =          '\033[36m'  # noqa
            grey =          '\033[37m'  # noqa
            darkgrey =      '\033[90m'  # noqa
            lightred =      '\033[91m'  # noqa
            lightgreen =    '\033[92m'  # noqa
            yellow =        '\033[93m'  # noqa lightorange is yellow
            lightblue =     '\033[94m'  # noqa
            lightmagenta =  '\033[95m'  # noqa
            lightcyan =     '\033[96m'  # noqa
            lightgrey=      '\033[97m'  # noqa

        class bg(object):
            current =       ''           # noqa
            default =       '\033[39m'   # noqa
            black =         '\033[40m'   # noqa
            red =           '\033[41m'   # noqa
            green =         '\033[42m'   # noqa
            orange =        '\033[43m'   # noqa
            blue =          '\033[44m'   # noqa
            purple =        '\033[45m'   # noqa
            cyan =          '\033[46m'   # noqa
            grey =          '\033[47m'   # noqa
            lightblack =    '\033[100m'  # noqa
            lightred =      '\033[101m'  # noqa
            lightgreen =    '\033[102m'  # noqa
            yellow =        '\033[103m'  # noqa lightorange is yellow
            lightblue =     '\033[104m'  # noqa
            lightmagenta =  '\033[105m'  # noqa
            lightcyan =     '\033[106m'  # noqa
            lightgrey =     '\033[107m'  # noqa

    # status types definitions (publicly exported)
    STATUS_NONE = 0
    STATUS_PENDING = 1
    STATUS_SKIPPED = 2
    STATUS_SUCCESS = 3
    STATUS_FAIL = 4
    STATUS_ERROR = 5

    # statuses definition (used by status rendering methods)
    statuses_def = {
        #               status text     status text color
        STATUS_NONE:    ('',            ansi.fg.current),   # noqa
        STATUS_PENDING: ('PENDING',     ansi.fg.cyan),  # noqa
        STATUS_SKIPPED: ('SKIPPED',     ansi.fg.orange),  # noqa
        STATUS_SUCCESS: ('SUCCESS',     ansi.fg.green),  # noqa
        STATUS_FAIL:    ('FAIL',        ansi.fg.red),  # noqa
        STATUS_ERROR:   ('ERROR',       ansi.fg.lightred)  # noqa
    }

    class Widget(tuple):
        """Represents widget as tuple of any renderable elements. Widgets can be composed from other widgets."""
        def __new__(cls, *elements):
            return super(UI.Widget, cls).__new__(cls, elements)

    class Colorized(Widget):
        def __new__(cls, color, *elements):
            return super(UI.Colorized, cls).__new__(cls, color, elements, UI.ansi.reset)

    class Boldized(Widget):
        def __new__(cls, *elements):
            return super(UI.Boldized, cls).__new__(cls, elements, UI.ansi.reset)

    class Underlinized(Widget):
        def __new__(cls, color, *elements):
            return super(UI.Underlinized, cls).__new__(cls, color, elements, UI.ansi.reset)

    class Status(Widget):
        def __new__(cls, status_type):
            status = UI.statuses_def.get(status_type, UI.statuses_def[UI.STATUS_NONE])
            return super(UI.Status, cls).__new__(cls,
                status[1], '[' if status[0] else '', status[0], ']' if status[0] else '',
                UI.ansi.reset, ' ' if status_type else '')

    class Frame(Widget):
        def __new__(cls, status_type, *elements, **kwargs):
            offset = '\033[3F' if kwargs.pop('replace_previous', False) else ''
            return super(UI.Frame, cls).__new__(cls,
                offset, '\n', UI.ansi.fg.orange, '-' * 80, UI.ansi.reset, '\n',
                UI.Colorized(UI.ansi.fg.orange, '%s | ' % sys.argv[0].split(os.sep)[-1]),
                UI.Status(status_type), UI.Colorized(UI.ansi.fg.blue, *elements), '\n')

    @classmethod
    def render(cls, *obj):
        """Renders objects (may be list of lists of strings/widgets) to chars ready do display"""
        return ''.join([cls.render(*x) if isinstance(x, (tuple, list)) else x for x in obj])

    @classmethod
    def output(self, *msg, **kwargs):
        """Output any message on console, quiet mode aware"""
        force_verbose = kwargs.pop('force_verbose', False)
        if not QUIET_MODE or force_verbose:
            print(self.render(*msg), end='')
            sys.stdout.flush()


class BEAMArgumentParser(argparse.ArgumentParser):
    """Customized ArgumentParser for BEAM needs"""
    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        # validate arguments syntax
        for arg in ['on', '@', 'run']:
            if vars(args).get(arg) != arg:
                argv.append(vars(args).get(arg))
        if argv:
            msg = 'commandline parser found unrecognized argument(s): %s'
            self.error(msg % ' '.join(argv))
        return args

    def error(self, message):
        """Raise exception to intercept instead sys.exit()"""
        message += UI.ansi.reset + '\n\n' + self.format_usage()
        raise BEAMCommandlineParserException(message)


class CommandlineParser(object):
    def __init__(self):
        # Build CommandlineParser instance
        prog_name = sys.argv[0].split(os.sep)[-1]
        usage = UI.render(UI.Boldized('%s' % prog_name), ' [options] ', UI.Boldized('on'), ' component ',
                          UI.Boldized('@'), ' environment ', UI.Boldized('run'), ' job [job_arg1, job_arg2, ...]')
        self.parser = BEAMArgumentParser(add_help=False, usage=usage)
        opts = self.parser.add_argument_group('options')
        opts.add_argument('--help', action='help',
                          help="Show this help message and exit.")
        opts.add_argument('--quiet', action='store_false', dest='be_quiet', default=False,
                          help="Don't print status messages to stdout")
        opts.add_argument('--force-confirmations', action='store_true', dest='force_mode', default=False,
                          help="Force mode: accepts all confirmations etc. Usable for running %s" % prog_name +
                               "in batch processing etc.")
        opts.add_argument('-p', dest='project_path', nargs=1,
                          help="Specify path of project directory. By default assumes directory from %s has been run."
                               % prog_name)
        opts.add_argument('--ansible-options', dest='ansible_options', nargs=1,
                          help="Specify additional options passed to ansible (i.e. --ansible-options=\"--verbose\").")
        args = self.parser.add_argument_group('arguments')
        args.add_argument('on', help=argparse.SUPPRESS)
        args.add_argument('components',
                          help="Components names (as defined in component.conf, one or more, comma-delimited."
                               "May be `all` to use all components in project.")
        args.add_argument('@', help=argparse.SUPPRESS)
        args.add_argument('environment',
                          help="Project environment name (one of defined in project.conf).")
        args.add_argument('run', help=argparse.SUPPRESS)
        args.add_argument('job',
                          help="Job name (one of defined in project and components conf files).")
        args.add_argument('job_args', nargs='*',
                          help="Job args (defined by job).")

    def parse_commandline(self, argv):
        global QUIET_MODE
        global FORCE_MODE
        project = components = beam_options = None
        # check "special" commands
        args = self.parser.parse_args(argv)
        QUIET_MODE, FORCE_MODE = args.be_quiet, args.force_mode

        UI.output(UI.Frame(UI.STATUS_PENDING, 'Parsing and validating project.conf of selected project...'))
        # check if run properly, form project root directory
        from beam.config_parser import Project, Component
        project_root_path = args.project_path if args.project_path else getcwd()
        project = Project(project_root_path)

        components = []
        if args.components == 'all':
            components_names = [x for x in project.components.keys()]
        else:
            components_names = [x for x in args.components.split(',')]

        components_path = p.join(project_root_path, 'project_components')
        component_root_paths_list = [p.join(components_path, x) for x in listdir(components_path) if
                                   p.isdir(p.join(components_path, x))]
        UI.output(UI.Frame(UI.STATUS_SUCCESS, 'Parsing and validating project.conf of selected project...',
                           replace_previous=True))

        UI.output(UI.Frame(UI.STATUS_PENDING, "Parsing and validating component.conf of project components..."))
        # gather all BEAM-aware components from project components directory
        all_components = []
        for component_root_path in component_root_paths_list:
            component_conf_path = p.join(component_root_path, BEAM_ROOT_DIR, BEAM_COMPONENT_CONF_NAME)
            if p.isfile(component_conf_path):
                all_components.append(Component(component_conf_path))
        # check if all required components has been gathered
        all_components_names = [component.name for component in all_components]
        for component_name in components_names:
            if component_name not in all_components_names:
                raise BEAMException('Cannot find component %s in project components directory, ' % (component_name) +
                                    'Check for component name typos or if component.conf contais proper names.')
            components.append([x for x in all_components if x.name == component_name][0])
        # gather options
        beam_options = [{x: getattr(args, x)} for x in ['be_quiet', 'force_mode']]
        UI.output(UI.Frame(UI.STATUS_SUCCESS, "Parsing and validating component.conf of project components...",
                           replace_previous=True))
        return project, components, args.environment, args.job, args.job_args, beam_options, args.ansible_options
