Sudoers
-------

Description
^^^^^^^^^^^

This role allows to set sudoers users or groups. It edits */etc/sudoers* file by
adding content at the end.

Instructions
^^^^^^^^^^^^

Set needed sudoers using a list:

.. code-block:: yaml

  sudoers:
    # Set 'manu' user as sudoer with passwordless rights
    - name: manu
      privilege: ALL=(ALL) NOPASSWD:ALL
    # Set 'techs' group users as sudier with passwordless rights
    - name: "%techs"
      privilege: ALL=(ALL) NOPASSWD:ALL

Changelog
^^^^^^^^^

* 1.0.1: Updated role to install sudo package. Neil Munday <neil@mundayweb.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>
