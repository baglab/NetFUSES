#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
implements a clean version of the NetFUSES algorithm, allowing for an extensible similarity function.

The NetFUSES algorithm consists of two stages - fusing and collapsing;
1. Fusing draws analogs between nodes across the set of graphs to fuse 
2. Collapsing takes nodewise analog components and merges them into a single node
    by taking each member of the component and drawing edges between it and its neighbors.
    - if the neighbor is alrady contained in the component, a self loop is drawn.

This version is implemented to support different similarity functions, manifested
by a parameter to `fuse` called `simfn`. As described in the docstring, `simfn`
takes as input a source node u, a set of valid analog vertices V, a threshold value t,
and any other keyword arguments necessary. `simfn` returns all nodes that have 
a similarity to u greater than t.
"""
import networkx as nx
__all__ = ["convert_graph","NetworkFuser"]


def convert_graph(G, Gprime=nx.DiGraph()):
    """
    convert a multigraph to another graph type
    args:
        :G (nx.Graph child) - graph to collapse edges
        :Gprime (nx.Graph child) - graph to populate; defaults to digraph
    returns:    
        :the newly converted graph
    """
    Gprime.add_edges_from(G.edges())
    return Gprime 

class NetworkFuser:
    """
    Fuses graphs by finding analogs above a given threshold
    using the specified similarity function parameter.
    """
    def __init__(self, simfn, threshold=0.95):
        """
        constructs the network fuser using the specified
        similarity function and threshold value

        args:
            :simfn (function)
                determines the similarity between two nodes
                args:
                    :u - node from a network
                    :v - node from a network 
                    :**kwargs - any keyword arguments necessary
                returns:
                    :(float) similarity between the two nodes
        """

        self.similarity_func = simfn
        self.t = threshold

    def _above_threshold(self,u,v):
        return self.similarit_func(u, v) > self.t

    def fuse(self, *graphs, verbose=0, **kwargs):
        """
        fuses the graphs by proceeding through the NetFUSES algorithm
        
        '''On input graphs 𝒢 = {G₀, G₁, ..., Gₙ} and threshold value t,
        1. Initialize fused graph G* = (V*, E*) where E* = ∅ and 
             V* = union of nodes across each Gᵢ∈ 𝒢
        2. for each i ∈ V*;
        3.     E* = E* ∪ { (i,j) | j ∈ V* and S(i,j) > t }  
        4. return G*'''

        args:
            :*graphs some number of (nx.Graph) - members of 𝒢 
            :verbose: print output every `verbose` steps; not at all for
                      verbose = None
            :**kwargs - passed to the similarity function
        """
        union = set().union(*map(set, graphs))
        G = nx.Graph()
        G.add_nodes_from(union)
        G.add_edges_from((u,u) for u in union)

        for i, u in enumerate(list(union), 1):
            if verbose is not None and i % verbose == 0:
                print('\r{0}\r{1:5d/{2:5d}, t={3}'.format(80*' ',i,len(union), self.t))

            valid_nodes = union - set([u])
            analogs = [self._above_threshold(u, v) for v in valid_nodes]
            G.add_edges_from((u,a) for a in analogs)

        return G

    def collapse(self, fuser, *graphs, collapsed=nx.MultiGraph()):

        """
        collapse the graph G so that each connected component in G becomes a 
        fused node in the output graph

        If a connected component contains two nodes that share an edge, 
        create a self loop in the output graph

        args:
            :fuser (nx.Graph) - the fused graph, output of `self._fuse`
            :*graphs - some number of source graphs that will comprise the final graph
            :collapsed (nx.Graph child) - the graph to populate
        returns:
            :populated version of `collapsed` containing a mapping
                from component id -> node under the attribute 'fused_set' 
            :(dict) - mapping from node to component id
        raises:
            :AssertionError if graphs is not all nx.Graph children
        """
        assert all(isinstance(g, nx.Graph) for g in graphs)
        
        conn_comps = sorted(nx.connected_component_subgraphs(fuser), key=len)

        # each node in the fused graph is a component in the fuser
        id2fused_set = dict()
        node2fuse_id = dict()
        # add self loops and find node ids
        for i, component in enumerate(conn_comps):
            id2fused_set[i] = set(component)
            node2fuse_id.update(**{u:i for u in component})
            collapsed.add_node(i)
            self_loops = []
            neighbors = []
            for node in component:
                for Gi in filter(lambda g: node in g, graphs):
                    self_loops.extend(n for n in Gi.neighbors(node) if n in component) 
                    neighbors.extend(Gi.neighbors(node))

            # draw edges between aggregated node sets
            collapsed.add_edges_from((i, node2fuse_id[u]) for u in neighbors) 
            # add self loops 
            collapsed.add_edges_from((i,i) for _ in range(len(self_loops))) 
        
        nx.set_node_attributes(collapsed, 'fused_set', id2fused_set)
        return collapsed, node2fuse_id
