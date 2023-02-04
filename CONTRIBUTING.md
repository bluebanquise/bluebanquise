# Contributing

:construction_worker: Many thanks for considering contributing to **BlueBanquise**. :construction_worker:

Please do not hesitate to contact us using [issues](https://github.com/bluebanquise/bluebanquise/issues) or [discussions](https://github.com/bluebanquise/bluebanquise/discussions), we will be glad to help you! :raising_hand:

Please keep in mind we are developing BlueBanquise as a **best effort** on our free time.

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
Feel free to refuse, we will **never** take offense.

Do not provide security related data (ssh key, passwords, etc) in your reports.

## Asking for new features / enhancements

If you need new features, please open an issue using the feature request template.
Try to comply with it to fasten our answer.

## Pull Requests

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

### Versioning

By default, each role has a version number, set in vars/main.yml and at the bottom of the readme.rst or README.md.
If your PR brings changes to the tasks, files, templates or vars folders, please increment the version.

## License

The stack is under MIT. This choice is based on a wish to allow everyone to use it.
Please consider using the same license if you wish to Pull Request some code into the main project.
