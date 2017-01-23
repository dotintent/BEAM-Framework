# beam.postgresql

PostgreSQL server support.

## Actions

### deploy

Install and configure postgresql packages, creates database & database user (if not present).

Parameters that you can pass in *params* object:

parameter|type|default value|description
---------|----|-------------|-----------
postgresql_version|string|9.5|Version of postgresql to be installed.
pg_hba_conf_file_template|string|*none*|Path to pg_hba.conf template
db_name|string|*none*|name of database that will be created
db_user_login|string|*none*|database user login name
db_user_password|sring|*none*|database user login password

**Example of usage:**

```yamlex
roles:
  - { role: beam.postgresql, action: deploy, params: {
        postgresql_version: 9.5,
        pg_hba_conf_file_template: "templates/pg_hba.conf.j2",
        db_name: pfcdb,
        db_user_login: djangoapp,
        db_user_password: 123abc,
      }
    }
```
