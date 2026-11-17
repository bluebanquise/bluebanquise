======
Nvidia
======

GPUs bring a lot of power to a cluster, and a few extra steps to the deployment. Don't worry, there
is nothing difficult: this page gathers them in one place, from drivers to Slurm jobs using GPUs.

We use the ``gpu`` role for drivers and CUDA, and the ``slurm`` role to let jobs request GPUs. Both
are described in detail in their own documentation; here we focus on how they fit together.

``[SCHEMA: nvidia-gpu-stack]``
  *Three stacked layers on a GPU host: Nvidia repository (on the management host or the internet)
  feeding the "driver + CUDA" layer (gpu role), on top of which "slurmd + gres.conf" (slurm role)
  exposes /dev/nvidia0..N to jobs; an arrow from the Slurm controller showing a job submitted with
  --gres=gpu:2 landing on the host.*

1. Describe GPU hosts
=====================

GPUs are a hardware matter, so we describe them in the hardware group of GPU hosts, for example
``group_vars/hw_gpu_worker/settings.yml``:

.. code-block:: yaml

  gpu_vendor: nvidia
  gpu_nvidia_install_cuda: true
  gpu_reboot: true

  hw_specs:
    cpu:
      cores: 64
    memory: 515072
    gpu:
      - NVIDIA H100 80GB HBM3
      - NVIDIA H100 80GB HBM3
      - NVIDIA H100 80GB HBM3
      - NVIDIA H100 80GB HBM3

* ``gpu_vendor`` tells the ``gpu`` role what to install. Setting it in the inventory, rather than
  in a playbook, lets other roles (like ``slurm``, when it generates the configuration of the whole
  cluster on its controller) know which hosts have Nvidia GPUs.
* ``hw_specs.gpu`` lists the GPUs of each host, one line per GPU, with the names reported by
  ``nvidia-smi -L``. Slurm uses this list to declare GPUs.

.. note::

  Hosts without GPU simply do not define ``hw_specs.gpu`` at all.

2. Provide Nvidia repositories
==============================

Nvidia packages come from Nvidia repositories, which must be known to GPU hosts before running the
``gpu`` role. Add them to ``bb_repositories`` of the GPU hosts (in their hardware group, or a
dedicated group), next to the distribution and BlueBanquise repositories. For example on RHEL 10:

.. code-block:: yaml

  bb_repositories:
    - name: cuda
      baseurl: https://developer.download.nvidia.com/compute/cuda/repos/rhel10/x86_64
      gpgcheck: true
      gpgkey: https://developer.download.nvidia.com/compute/cuda/repos/rhel10/x86_64/CDF6BA43.pub
    - name: epel
      baseurl: https://dl.fedoraproject.org/pub/epel/10/Everything/x86_64

Use ``sbsa`` instead of ``x86_64`` for arm64 hosts. The **gpu** role documentation gives the
repository of each supported distribution.

On clusters without internet access, mirror these repositories on the management host, and point
``bb_repositories`` to the local copies. Keep the repository metadata as is: recreating it with
``createrepo`` would destroy the Nvidia DNF module streams.

3. Install drivers and CUDA
===========================

Add the ``gpu`` role to the playbook of GPU hosts:

.. code-block:: yaml

  - role: bluebanquise.infrastructure.gpu
    tags: gpu

And run it:

.. code-block:: bash

  ansible-playbook playbooks/computes_gpu.yml -i inventories/new_cluster -b --tags repositories,gpu

The role installs the kernel headers of the running kernel, the driver (built with DKMS, using
Nvidia open kernel modules by default, for Turing and newer GPUs), CUDA if requested, and enables
``nvidia-persistenced``. A reboot is needed after the first installation: with ``gpu_reboot: true``,
the role takes care of it, and waits for hosts to come back.

Let's check everything is fine:

.. code-block:: bash

  clush -bw @hw_gpu_worker nvidia-smi -L

Each host should list its GPUs, with the same names as in ``hw_specs.gpu``.

.. note::

  Older GPUs (V100, P100...) need Nvidia proprietary kernel modules, available on RHEL 9 only: set
  ``gpu_nvidia_kernel_modules: proprietary``.

.. warning::

  DKMS builds the driver for the running kernel. When the kernel is updated, the driver is rebuilt
  at next boot, which takes a few minutes, and can fail if the new kernel is not yet supported by
  the driver. On production clusters, consider locking the kernel version (see the kernel version
  lock of :doc:`../configuration/os_settings`), and updating kernel and driver together.

4. Let Slurm schedule GPUs
==========================

Slurm handles GPUs as *generic resources* (gres). Let's enable them in the Slurm settings of the
cluster (see the **slurm** role documentation for the other settings):

.. code-block:: yaml

  slurm_selecttype: "select/cons_tres"
  slurm_grestypes: gpu

And declare how many GPUs each GPU host offers, in its hardware group, next to ``hw_specs.gpu``:

.. code-block:: yaml

  hw_specs:
    slurm_extra_nodes_parameters: "Gres=gpu:4"
    gpu:
      - NVIDIA H100 80GB HBM3
      - NVIDIA H100 80GB HBM3
      - NVIDIA H100 80GB HBM3
      - NVIDIA H100 80GB HBM3

The ``slurm`` role then writes ``gres.conf``, mapping each GPU of ``hw_specs.gpu`` to its device file
(``/dev/nvidia0``, ``/dev/nvidia1``...).

Alternatively, Slurm can detect GPUs itself, through Nvidia NVML: set ``slurm_grestypes_nvml: true``
in addition to the settings above. ``slurm_extra_nodes_parameters`` can then also give the GPU type,
as named by NVML, for example ``"Gres=gpu:nvidia_gb200:4"``.

Run the Slurm role on the controller and on GPU hosts, then check Slurm sees the GPUs:

.. code-block:: bash

  scontrol show node g001 | grep -i gres

And finally, the moment of truth, a job using 2 GPUs:

.. code-block:: bash

  srun --gres=gpu:2 nvidia-smi -L

Only the 2 GPUs allocated to the job should be listed.

5. Containers
=============

Users running their software in Singularity containers (``singularity`` role) can access GPUs with
the ``--nv`` option, which makes the host driver available inside the container:

.. code-block:: bash

  srun --gres=gpu:1 singularity exec --nv my_image.sif nvidia-smi

6. Monitoring
=============

Keep an eye on your GPUs: Nvidia provides an exporter for Prometheus, DCGM exporter, which can be
declared as an additional exporter in the **prometheus** role, to follow GPU temperature,
utilization and memory, and to be warned of hardware errors.
