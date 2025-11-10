# Doreamon

![Doreamon](doreamon.jpg)

Doreamon is my daemon that runs "somewhere" :wink:, to build all packages, documentation, tutorials, website, etc, and pushs all of that to target web hosting.

It is for my personal usage to automate BlueBanquise builds, but feel free to copy part of it if needed.

## Usage

A file credentials.sh is required inside user $HOME. It contains the following variables:

```shell
website_user=XXXXXXXX
website_pass=XXXXXXXXXXXX
website_host=XXXXXXXXXXXXXXXXX
```

These are target web hosting credentials to push final files.

It is also mandatory that the hosts aarch64_worker and x86_64_worker are known by current system, and that current user can ssh to bluebanquise@aarch64_worker and to bluebanquise@x86_64_worker.
