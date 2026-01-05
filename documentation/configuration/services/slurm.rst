
### 5. Topology file

In order to create a topology, you can use the variable `slurm_topology`. It takes into account the Swicth and Block options like in https://slurm.schedmd.com/topology.html

A sample of inventory for Blocks will be:
```yaml
slurm_topology: topology/block
slurm_topology_blocksizes: 18
slurm_topology_file:
  rack1:
    section: BlockName
    subsection: Nodes
    nodeset: c[01-18]
  rack2:
    section: BlockName
    subsection: Nodes
    nodeset: c[19-36]
```

A sample for an inventory for Switches will be:
```yaml
slurm_topology: topology/tree
slurm_topology_file:
  isw101:
    section: SwitchName
    subsection: Nodes
    nodeset: c[01-20]
  isw102:
     section: SwitchName
     subsection: Nodes
     nodeset: c[21-40]
  isw201:
     section: SwitchName
     subsection: Switches
     nodeset: isw[101-102]
```