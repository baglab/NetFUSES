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

def fuse(t, simfn, *graphs,verbose=0,**kwargs):
    """
    fuse graphs by finding analogs above a given threshold for each node in the union
    of their vertex sets; nodes without analogs are not fused to anything
    
    the algorithm proceeds by:

    '''On input graphs 𝒢 = {G₀, G₁, ..., Gₙ} and threshold value t,
    1. Initialize fused graph G* = (V*, E*) where E* = ∅ and 
         V* = union of nodes across each Gᵢ∈ 𝒢
    2. for each i ∈ V*;
    3.     E* = E* ∪ { (i,j) | j ∈ V* and S(i,j) > t }  
    4. return G*'''

    args:
        :t (float) - threshold value for the similarity function
        :simfn (function) 
            args:
                :u - the source node
                :V - set of nodes in which there might be located analog(s)
                :t - the threshold
                :**kwargs - any keyword arguments necessary for the function
            returns:
                :nodes in v ∈ V* \ {u} for which S(u, v) > t
        :*graphs (nx.Graph child) - graphs to fuse together
        :verbose: print output every `verbose` steps; not at all for verbose = None
        :**kwargs
    returns:
        : (nx.Graph) - the fused representation of the input graphs
    """
    union = set().union(*map(set, graphs))

    G = nx.Graph()
    G.add_nodes_from(union)
    G.add_edges_from((u,u) for u in union)

    for i, u in enumerate(list(union),1):
        if verbose is not None and i % verbose == 0:
            print('\r{0}\r{1:5d}/{2:5d}, t={3}'.format(80*' ',i,len(union),t))
        valid_nodes = union - set([u])
        analogs = simfn(u, valid_nodes, t, **kwargs)
        G.add_edges_from((u,a) for a in analogs)
        #analogdf = u_simdf[u_simdf.cn_node.isin(valid_nodes)]
        #mx = analogdf.similarity.max()
        #if mx > t:
        #    analogdf = u_simdf[u_simdf.similarity > t]
        #    #analogdf = u_simdf[u_simdf.similarity == mx]
        #    analogs = set(analogdf.cn_node.values.tolist())
        #    if analogs:
        #        G.add_edges_from((u,a) for a in analogs)
        #else:
        #    analogs = []
    if verbose is not None:
        print('performed fuse')
    return G 

def collapse_fused_graph(fuser,*graphs, collapsed=nx.MultiGraph()):
    """
    collapse the graph G so that each connected component in G becomes a fused node in the 
    output graph

    If a connected component contains two nodes that share an edge, create a self loop in the
    output graph

    args:
        :fuser (nx.Graph) - the fused graph, output of `netfuses.fuse`
        :*graphs - some number of source graphs that will comprise the final graph
        :collapsed (nx.Graph child) - the graph to populate
    returns:
        :populated version of `collapsed` 
        :(dict) - mapping from component id to node
        :(dict) - mapping from node to component id
    """
    conn_comps = sorted(nx.connected_component_subgraphs(fuser), key=len)
    # each node in the fused graph is a component in the fuser
    id2fused_set = dict()
    node2fuse_id = dict()
    # add self loops and find node ids
    for i, component in enumerate(conn_comps):
        id2fused_set[i] = set(component.nodes())
        node2fuse_id.update(**{u:i for u in component})
        collapsed.add_node(i)
        self_loops = []
        neighbors = []
        for node in component:
            for Gi in filter(lambda g: node in g, graphs):
                self_loops.extend(n for n in Gi.neighbors(node) if n in component)
                neighbors.extend(Gi.neighbors(node))

        collapsed.add_edges_from((i, node2fuse_id[u]) for u in neighbors) # draw edges between aggregated node sets
        collapsed.add_edges_from((i,i) for _ in range(len(self_loops)))   # add self loops 

    return collapsed, id2fused_set, node2fuse_id

def convert_graph(G, Gprime=nx.DiGraph()):
    """
    convert a multigraph to another graph type
    args:
        :G (nx.Graph child) - graph to collapse edges
        :Gprime (nx.Graph child) - graph to populate; defaults to digraph
    returns:    
        :converted mg --> simple 
    """
    Gprime.add_edges_from(G.edges())
    return Gprime 
