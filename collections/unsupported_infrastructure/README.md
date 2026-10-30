# Unsupported infrastructure roles

This folder stores roles that were part of the `bluebanquise.infrastructure` collection,
but are no longer maintained.

These roles are kept as they were when they were removed from the collection: they are
not tested anymore, and may not work on currently supported distributions.
They are not part of the `bluebanquise.infrastructure` collection, and are not installed with it.

If you need one of these roles, please open an issue on the
[BlueBanquise GitHub repository](https://github.com/bluebanquise/bluebanquise/issues),
so it can be brought back to the collection and updated.

| Role | Removed in | State when removed |
|------|------------|--------------------|
| `flexlm` | 3.4 | Broken on supported distributions (LSB packages removed from RHEL 9 and Ubuntu 24.04). |
| `google_authenticator` | 3.4 | Fixed and tested on Ubuntu 24.04 just before removal (SSH key or password + verification code), not tested on other distributions. |
