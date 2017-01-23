# beam.django

Django support.

## Actions

### deploy

Install and configure django package on separate virtualenv environment.

Parameters that you can pass in *params* object:

parameter|type|default value|description
---------|----|-------------|-----------
virtualenv_python_version|string|*none*|version of python used for runtime
django_wsgi_module|string|*none*|wsgi module dotpath
django_project_name|string|content of BEAM_VARS.PROJECT.NAME|Name of django project (used internally).
django_project_root|string|content of BEAM_VARS.PROJECT.NAME|Name of project root folder.
django_local_settings_template|string|*none*|Path to local settings template
db_name|string|*none*|Database name.
db_host|string|localhost|Database host (IP or domain)
db_port|int|5432| Database port
db_user_login|string|*none*|Database user login name
db_user_password|string|*none*|Database user password

**Example of usage:**

```yamlex
roles:
  - { role: beam.django, action: deploy, params: {
        virtualenv_python_version: 3.5,
        django_wsgi_module: djangoapp.wsgi,
        django_project_name: "{{ BEAM_VARS.COMPONENT.NAME }}",
        django_project_root: "{{ BEAM_VARS.COMPONENT.NAME }}",
        django_local_settings_template: templates/local_settings.py.j2,
        db_name: pfcdb,
        db_user_login: djangoapp,
        db_user_password: djang0apppassw0rd,
      }
    }
```
