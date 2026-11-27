from .constants import YARRRML_GRAPH, YARRRML_GRAPHS

def add_inverse_graph(graph_values):
    graphs = []
    for graph in graph_values:
        if not graph.startswith("http"):
            graph = '$(' + graph + ')'
        else:
            if '{' in graph:
                graph = graph.replace('{', "$(").replace('}', ')')
        graphs.append(graph.toPython())

    if len(graphs) == 1:
        yarrrml_graphs = {YARRRML_GRAPH: graphs[0]}
    else:
        yarrrml_graphs = {YARRRML_GRAPHS: graphs}

    return yarrrml_graphs
