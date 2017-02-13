import os.path as p
BEAM_VERSION = '0.9.1'
BEAM_PROJECT_CONF_NAME = 'project.conf'
BEAM_COMPONENT_CONF_NAME = 'component.conf'

BEAM_FRAMEWORK_ROOT_DIR = p.dirname(p.dirname(p.abspath(__file__)))
BEAM_FRAMEWORK_ROLES_INT_DIR = p.join(BEAM_FRAMEWORK_ROOT_DIR, 'beam', 'roles', 'beam-internals')
BEAM_FRAMEWORK_ROLES_LIB_DIR = p.join(BEAM_FRAMEWORK_ROOT_DIR, 'beam', 'roles', 'beam-roles-library')

BEAM_ROOT_DIR = '.BEAM'
BEAM_ENVIRONMENTS_DIR = p.join(BEAM_ROOT_DIR, 'environments')
BEAM_JOBS_DIR = p.join(BEAM_ROOT_DIR, 'jobs', )
BEAM_JOBS_ROLES_DIR = p.join(BEAM_ROOT_DIR, 'jobs', 'roles')
