# beam.nginx

Nginx server support.

## Actions

### deploy

Deploys nginx server: nginx server (and all required  related packages) is installed and configured.

Parameters that you can pass in *params* object:

parameter|type|default value|description
---------|----|-------------|-----------
nginx_site_conf_file_template|*none*|Path to template of site conf file.
nginx_host|*none*|Domain (or IP address if no domain) of Nginx server.
nginx_port|*none*|Port on which Nginx serwer will listen.
nginx_client_max_body_size|64K|Maximum acceptable request body size,
nginx_project_name|content of BEAM_VARS.COMPONENT.NAME|arbitrary project name for distinguising other Nginx project instances (if any),

**Example of usage:**

```yamlex
roles:
  - { role: beam.nginx, action: deploy, params: {
        nginx_domain: localhost,
        nginx_host: 127.0.0.1,
        nginx_port: 8081,
        nginx_client_max_body_size: 100K,
        nginx_project_name: "{{ BEAM_VARS.COMPONENT.NAME }}",
        nginx_site_conf_file_template: templates/nginx_django_app.conf
      }
    }
```
