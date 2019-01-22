# NetFUSES
## Overview

<p>
NetFUSES is a <b>graph fusion</b> algorithm for coalescing networks of distinct sets of nodes into 
a single network. Graph fusion is a unique problem associate with combining nodes across and inside of networks
based on a similarity function defined across all nodes with respect to a single threshold parameter <i>t</i>.
</p> 

<h2>Algorithm</h2> 

<p>
The NetFUSES algorithm consists of two stages - fusing and collapsing;
<ul>
<li> Fusing draws analogs between nodes across the set of graphs to fuse </li>
<li> Collapsing takes nodewise analog components and merges them into a single node
    by taking each member of the component and drawing edges between it and its neighbors.
    If the neighbor is already contained in the component, a self loop is drawn.
</li>
</ul>
</p>
<p>
This version is implemented to support different similarity functions, manifested
by a parameter to <code>fuse</code> called <code>simfn</code>. As described in the docstring, <code>simfn</code>
takes as input a source node <i>u</i>, a set of valid analog vertices <i>V</i>, a threshold value <i>t</i>,
and any other keyword arguments necessary. Function `simfn` returns all nodes that have a similarity to u greater than <i>t</i>.
</p>

<h2>Requirements</h2>
<p>
This module requires the installation of networkx (we used version 1.11)
</p>
