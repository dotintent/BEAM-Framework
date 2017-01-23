# beam.git

Git support.

## Actions

### deploy

Install git and clones given repository.

Parameters that you can pass in *params* object:

parameter|type|default value|description
---------|----|-------------|-----------
repo_url|string|content of BEAM_VARS.COMPONENT.REPO_URL|Url to repository to be clonned.
repo_name|string|content of BEAM_VARS.COMPONENT.NAME|Name of repository (used internally). 
version|string|content of BEAM_VARS.JOB.DEPLOY_VERSION| Branch, tag or commit used during clonning.
destination|string|content of BEAM_VARS.COMPONENT.NAME|Path where repo will be clonned.

**Example of usage:**

```yamlex
roles:
    - { role: beam.git, action: deploy }
```

