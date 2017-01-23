# beam.include-yml-files

Helper role that includes (via ansible include directive) any yml files (from given *task_path* path) that names matches with passed *tasks* argument into current playbook. 


Parameters that you can pass in role:

parameter|type|default value|description
---------|----|-------------|-----------
tasks|list of string|*empty list*|List of tasks 
task_path|string|".." *(current dir)*|Path to directory with yml files to be included.

**Example of usage:**

```yamlex
roles:
  - { role: beam.include-yml-files, params: {
        tasks: "{{ BEAM_VARS.JOB.SERVICES }}",
        tasks_path: services,
      }
    }
```
