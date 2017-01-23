# beam.python

Python support.

## Actions

### deploy

Install python package with given version.

Parameters that you can pass in *params* object:

parameter|type|default value|description
---------|----|-------------|-----------
python_version|string|3.5|Version of Python package to be installed.
**Example of usage:**

```yamlex
roles:
  - { role: beam.python, action: deploy}
```
