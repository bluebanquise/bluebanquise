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

We may ask you more questions then, or even to provide part of your inventories. Feel free to refuse, we will **never** take offence.

Do not provide security related data (ssh key, passwords, etc) in your reports.

## Asking for new features / enhancements :bulb:

We would be happy to provide more possibilities to the stack.

However, please keep in mind we are doing this as a best effort, on our free time :family:. We will do our best to at least acknowledge we got your query.

Also, if we consider this may damage the stack (modifications in the engine or the core roles), or break the KISS (Keep it simple) effort we are doing on the stack, we may only provide the feature as an addon.

## Pull Requests :arrow_heading_down:

All contributions must pass through a Pull Request, to ensure easy reviewing of modifications.

There are currently no automatic tests done after a Pull Request.

We will then do our best to answer you and test your contribution as soon as possible, before merging it. We may iterate with you to converge before merging to master branch.

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

## Architecture :octopus:

If you provide a new role, please try to make it autonomous, so that it can be mixed with any kind of other roles. This is one of the targets of this stack: full modularity.

Also, consider that some variables are specific in BlueBanquise, and do not fully follow the standard rules of Ansible:
* Equipment_profile
* Authentication

These dictionaries **MUST** be set in group_vars/equipment_profile folders or in group_vars/all . Any other usage (for example at host_vars level or extra_vars level) will result in a dangerous situation.

## Writing, naming :page_with_curl:

We are using *.yml* (and not *.yaml*) for all YAML files.

We try to not use tabulations, but instead double space for indentation.

Variables that contains Jinja2 code should be prepend with “j2_”.

If you are working on Microsoft Windows, please check you do not submit ^M at the end of your lines.

## Ownership

By default, each contributing physical person will be added to a “Contributors” list in the main stack README file. This is important for us.

If you do not wish so, please inform us.

## License

The stack is under MIT. This choice is based on a wish to allow everyone to use it. Please consider using the same license if you wish to Pull Request some code into the main project.

If you do not wish so, but you still wish to contribute, please contact us.





