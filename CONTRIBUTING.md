# Contributing

:construction_worker: Many thanks for considering contributing to **BlueBanquise**. :construction_worker:

Please do not hesitate to contact us using [issues](https://github.com/bluebanquise/bluebanquise/issues) or [discussions](https://github.com/bluebanquise/bluebanquise/discussions), we will be glad to help you! :raising_hand:

Please keep in mind we are doing this as a **best effort**, on our free time :family:.
We will do our best to at least acknowledge we got your query.

You will find here some basic guidelines to contribute.

## Conventions

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
and commits adheres to [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

Whenever possible, we try to comply with these conventions.

## Reporting bugs

If you encounter any bug, please open an issue.
An issue template is generated when creating a bug issue. Try to comply with it to fasten our answer.

We may ask you more questions then, or even to provide part of your inventories.
Feel free to refuse, we will **never** take offence.

Do not provide security related data (ssh key, passwords, etc) in your reports.

## Asking for new features / enhancements

If you need new features, please open an issue using the feature request template.
Try to comply with it to fasten our answer.

## Pull Requests

All contributions must pass through a Pull Request, to ensure easy reviewing of modifications.

We will then do our best to answer you and test your contribution as soon as possible, before merging it.
We may iterate with you to converge before merging to master branch.

### Datamodel

A datamodel is available at https://github.com/bluebanquise/bluebanquise/blob/master/resources/data_model.md

Your PR must comply with it.

### Backports

All PRs must be merged to the **master** branch first. Once merged, you can
create a new PR to backport the change to a previous stable branch.

For backports, we use a workflow similar to the [Ansible Development
Cycle](https://docs.ansible.com/ansible/latest/community/development_process.html#backporting-merged-prs).

We do **not** backport features.

Note: The default branch of Ansible is named `devel`. Ours is named `master`.

Whenever possible, please cherry-pick the commit using the `-x` flag to indicate
which commit this change was cherry-picked from.

```bash
git fetch upstream
git checkout -b backport/1.2/<pr_number_from_master> upstream/stable-1.2
git cherry-pick -x <commit_from_master>
git push origin backport/1.2/<pr_number_from_master>
```

Submit the PR for `backport/1.2/<pr_number_from_master>` against the
`stable-1.2` branch.

### Versioning

By default, each role has a version number, set in vars/main.yml and at the bottom of the readme.rst or README.md.
If your PR brings changes to the tasks, files, templates or vars folders, please increment the version.

### Changelog

In order to get your PR accepted, please update the main CHANGELOG.md. This is mandatory to merge the PR.

## Development guidelines

### The stack philosophy

BlueBanquise is a **fun** and **simple** stack, made to deploy generic cluster of hosts,
from IT room or enterprise network to large HPC/Farm clusters.

BlueBanquise is made to **simplify life of system administrators**,
allowing them to spend more time on interesting parts of the job (coffee break for example).

BlueBanquise is also made to **teach system administration** to students,
as each role is made to be a **step by step** simple process, easy to reproduce manually,
like a self-explaining practical session. This is also why documentation covers learning of Ansible.

### General and architecture

1. Stack was always aimed to **maximum simplicity**, even at the price of non-elegant ways.
A naïve code is, we think, better than an advanced one. Consider step by step understanding.
Remember the smart guy who made the ultimate compressed piped command, that nobody, even this guy, could understand after 2 months.
We should always consider debugging cost, and think as a non-developer user.

2. Stack was designed to be a ***united*** stack, while focusing on ***modularity***.
This means each role should be fully autonomous against the others, even in the core.
However, this also means roles are not expected to be used externally of the stack, without the stack standard inventory.

3. Stack is desired *semi-automatic*.
System administrator must always have a way to force things manually, most of the time using variables precedence mechanism.
This is the reason why in some key roles, inventory data is used instead of system facts.

### Documenting, comments

1. When possible, we try to add balanced comments, considering teaching to someone.
Do not hesitate to add url to your references, or to tutorials, etc.

2. **Always document**, if global in main documentation, if role related in role readme.
Documentation is written in sphinx, but if this is an issue for you, use markdown and we will translate it to sphinx for you.

### Scripting

1. Scripts should be written in *Python 3.6+*, and as simple as possible.
Maximum but balanced comments and verbosity should be considered.

2. A tool like Ansible is a configuration deployment tool. Ansible job is not to do administration tasks.
This is scripts job.

3. Tools, scripts, wrappers, are made to simplify system usage (Shell commands, Ansible, Linux tools, etc.).
However, when possible, manual way should always be documented side by side with the automated way,
to allow easy debug and simply understand scripts, as the stack also has a teaching objective.

### Variables

1. Internal roles variables, means under the hood variables that user should not consider modifying,
must be defined in the role vars.
External roles variables, means variables that user are expected to precedence,
must be defined in the role defaults.

2. All variables related to an equipment_profile should go in group_vars/all/equipment_all/ (global) or in group_vars/equipment_X/ with X the equipment profile name (dedicated). These variables must be prefixed by **ep_**.

3. All variables containing jinja2 code must be prefix with **j2_** and stored in internal/group_vars/all/j2_variables/.
j2_ variables are core of the stack, and should be manipulated with care.
These are intended to be precedence by user only. If needed, theses variables can be fixed.

### Miscellaneous

1. We start numbering at **1**, since a cluster stack is related to existing physical elements.
Networks start at 1, icebergs at 1, etc.

2. We are using *.yml* (and not *.yaml*) for all YAML files.

3. We try to not use tabulations, but instead double space for indentation.

4. If you are working on Microsoft Windows, please check you do not submit CRLF (seen sometime as ^M at the end of your lines).
See [Customizing-Git-Git-Configuration](https://www.git-scm.com/book/en/v2/Customizing-Git-Git-Configuration#_code_core_autocrlf_code].

## License

The stack is under MIT. This choice is based on a wish to allow everyone to use it.
Please consider using the same license if you wish to Pull Request some code into the main project.
