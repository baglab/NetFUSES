# NetFUSES
## Overview

NetFUSES is a __graph fusion__ algorithm for coalescing networks of distinct sets of nodes into 
a single network when node identity is unreliable or ambiguous. 
Graph fusion is a unique problem associated with combining nodes both across and inside of networks.
The combination of such nodes is based on a similarity function defined across all nodes 
with respect to a single threshold parameter _t_.

## Algorithm 

The NetFUSES algorithm consists of two stages - fusing and collapsing;
- Fusing draws analogs between nodes across the set of graphs to fuse
- Collapsing takes nodewise analog components and merges them into a single node
    by taking each member of the component and drawing edges between it and its neighbors.
    If the neighbor is already contained in the component, a self loop is drawn.

This version is implemented to support different similarity functions, manifested
by a parameter to `NetworkFuser`, `simfn`. As described in the docstring, `simfn`
takes as input two network nodes _u_ and _v_, any other keyword arguments necessary. 

## Installation Requirements
This module requires the installation of networkx (we used version 1.11)
