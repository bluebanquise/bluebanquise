# Contributing

:construction_worker: Many thanks for considering contributing to **BlueBanquise**. :construction_worker:

Please do not hesitate to contact us using issues, we will be glad to help you! :raising_hand:

The stack is still young, and some aspects are not clearly defined yet. But here are some basic guidelines:

## Conventions

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
and commits adheres to [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

Whenever possible, we try to comply with these conventions.

## Reporting bugs :beetle:

If you encounter any bug (and you will probably do), please provide the following details:
* How did you end up to this bug? What were you expecting as a normal result?
* Full trace of the shell
* Your operating system distribution and version
* Your Ansible version

If the bug is related to PXE or OS deployment:
* Is system is in EFI or legacy/bios?
* What is the native ROM of the system, PXE or iPXE? Did you boot in PXE, or from USB/CDrom?
* What is the hardware used?
* A small photo/screenshot of the screen when it fails maybe?

We may ask you more questions then, or even to provide part of your inventories.
Feel free to refuse, we will **never** take offence.

Do not provide security related data (ssh key, passwords, etc) in your reports.

## Asking for new features / enhancements :bulb:

We would be happy to provide more possibilities to the stack.

However, please keep in mind we are doing this as a **best effort**, on our free time :family:.
We will do our best to at least acknowledge we got your query.

Also, if we consider this may damage the stack (modifications in the engine or the core roles),
or break the KISS (Keep it simple) effort we are doing on the stack, we may only provide the feature as an addon,
or simply refuse the feature.

## Pull Requests :arrow_heading_down:

All contributions must pass through a Pull Request, to ensure easy reviewing of modifications.

We will then do our best to answer you and test your contribution as soon as possible, before merging it.
We may iterate with you to converge before merging to master branch.

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

## Development guidelines :octopus:

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
A naïve code is, I think, better than an advanced one. Consider step by step understanding.
Remember the smart guy who made the ultimate compressed piped command, that nobody, even this guy, can understand after 2 months.
We should always consider debugging cost, and think as a non-developer user.

2. Stack was designed to be a ***united*** stack, while focusing on ***modularity***.
This means each role should be fully autonomous against the others, even in the core.
However, this also means roles are not expected to be used externally of the stack, without the stack standard inventory.

3. Stack is desired *semi-automatic*.
System administrator must always have a way to force things manually, most of the time using variables precedence mechanism.
This is the reason why in some key roles, inventory data is used instead of system facts.

### Documenting, comments

1. When possible, try to add balanced comments, considering you are teaching to someone.
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

4. If a WebUI is available (and it is planed), standard inventory editing,
standard deployment using ansible-playbook, and standard usage will remain the default way.

### Variables

1. Variables should be centralized in the inventory as much as possible,
to ensure a single location for users to configure all, and non-replication of variables.
This is not the Ansible standard, but a need for a unified stack.

2. Internal roles variables, means under the hood variables that user should not consider modifying,
can be defined in the role vars. Example: packages names, services names, paths, etc.

3. General variables, i.e. not related to an equipment_profile, can be defined in group_vars/all/general_settings/,
in dedicated files or if needed in a new one. When possible, variables should be optional.
In any cases, they must be documented in the role readme (and if needed provided commented in the example inventories).

4. All variables related to an equipment_profile should go in group_vars/all/equipment_all/ (global) or in group_vars/equipment_X/ with X the equipment profile name (dedicated). These variables must be prefixed by **ep_**.

5. All variables containing jinja2 code must be prefix with *j2_* and stored in group_vars/all/j2_variables/.
j2_ variables are core of the stack, and should be manipulated with care.
These are intended to be precedence by user only. If needed, theses variables can be fixed.

6. Also, consider that some variables are specific in BlueBanquise,
and do not fully follow the standard rules of Ansible.
As stated in 4, these variables **must** be set in group_vars/equipment_X/ folders or in group_vars/all/equipment_all/.
Any other usage (for example at host_vars level or extra_vars level) will result in a unpredictable situation, as the stack use a random host of these groups to gather equipment_profile data.

### Miscellaneous

1. We start numbering at **1**, since a cluster stack is related to existing physical elements.
Networks start at 1, icebergs at 1, etc.

2. We are using *.yml* (and not *.yaml*) for all YAML files.

3. We try to not use tabulations, but instead double space for indentation.

4. If you are working on Microsoft Windows, please check you do not submit CRLF (seen sometime as ^M at the end of your lines).
See [Customizing-Git-Git-Configuration](https://www.git-scm.com/book/en/v2/Customizing-Git-Git-Configuration#_code_core_autocrlf_code].

## Ownership

By default, each contributing physical person will be added to a “Contributors” list in the main stack README file.
This is important for us. Remember to add yourself with first PR.

If you do not wish so, please inform us.

## License

The stack is under MIT. This choice is based on a wish to allow everyone to use it.
Please consider using the same license if you wish to Pull Request some code into the main project.

If you do not wish so, but you still wish to contribute, please contact us.
