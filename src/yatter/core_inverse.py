import rdflib
from rdflib.collection import Collection

from .constants import (
    DCAT_URI, FORMATS_URI, RDF_TYPE, RML_URI, SPARQL_SERVICE_URI, VOID_URI,
    YARRRML_ACCESS, YARRRML_COMPRESSION, YARRRML_CONDITION, YARRRML_DATATYPE,
    YARRRML_BLANK, YARRRML_EMPTY, YARRRML_EQUAL, YARRRML_FUNCTION, YARRRML_GATHER,
    YARRRML_GATHER_AS, YARRRML_GRAPH, YARRRML_IRI_TYPE, YARRRML_JOIN_CHILD_PARAMETER,
    YARRRML_JOIN_PARENT_PARAMETER, YARRRML_LANGUAGE, YARRRML_LITERAL_TYPE,
    YARRRML_MAPPING, YARRRML_OBJECT_SHORT, YARRRML_OUTPUT_FORMAT, YARRRML_PARAMETER,
    YARRRML_PARAMETERS, YARRRML_PREDICATE_SHORT, YARRRML_SERIALIZATION,
    YARRRML_STRATEGY, YARRRML_TARGET_DCAT, YARRRML_TARGET_SPARQL,
    YARRRML_TARGET_VOID, YARRRML_TARGETS, YARRRML_TYPE, YARRRML_VALUE,
)
from .errors import InvalidMappingError


RML = rdflib.Namespace(RML_URI)


def read_expression(graph, node):
    expressions = [
        (predicate, value)
        for predicate in (RML.constant, RML.reference, RML.template)
        for value in graph.objects(node, predicate)
    ]
    if len(expressions) != 1:
        raise InvalidMappingError("A Core expression must have exactly one supported expression")
    predicate, value = expressions[0]
    if predicate == RML.reference:
        return "$(" + str(value) + ")"
    if predicate == RML.template:
        return str(value).replace("{", "$(").replace("}", ")")
    if isinstance(value, rdflib.URIRef):
        return str(value) if str(value).startswith(("http://", "https://")) else f"<{value}>"
    if "$(" in str(value):
        raise InvalidMappingError("A constant containing YARRRML reference syntax cannot be represented")
    return str(value)


def _single(graph, node, predicate, required=False):
    values = list(graph.objects(node, predicate))
    if len(values) > 1 or (required and not values):
        raise InvalidMappingError(f"Expected {'exactly' if required else 'at most'} one {predicate}")
    return values[0] if values else None


def _iri(graph, value):
    if not isinstance(value, rdflib.URIRef):
        raise InvalidMappingError("Expected an IRI")
    return graph.namespace_manager.normalizeUri(value)


def read_targets(graph, node):
    targets = list(graph.objects(node, RML.logicalTarget))
    if len(targets) > 1:
        raise InvalidMappingError("Multiple logical targets cannot be represented")
    if not targets:
        return []
    target = targets[0]
    destination = _single(graph, target, RML.target, required=True)
    void = rdflib.Namespace(VOID_URI)
    dcat = rdflib.Namespace(DCAT_URI)
    sd = rdflib.Namespace(SPARQL_SERVICE_URI)
    choices = [(void.dataDump, YARRRML_TARGET_VOID), (dcat.dataDump, YARRRML_TARGET_DCAT),
               (sd.endpoint, YARRRML_TARGET_SPARQL)]
    accesses = [(graph.value(destination, predicate), kind) for predicate, kind in choices]
    accesses = [(access, kind) for access, kind in accesses if access is not None]
    if len(accesses) != 1:
        raise InvalidMappingError("Unsupported logical target destination")
    access, kind = accesses[0]
    result = {YARRRML_ACCESS: str(access), YARRRML_TYPE: kind}
    serialization = _single(graph, target, RML.serialization)
    if serialization is not None:
        formats = rdflib.Namespace(FORMATS_URI)
        names = {formats[value]: name for name, value in YARRRML_OUTPUT_FORMAT.items()}
        if serialization not in names:
            raise InvalidMappingError("Unsupported target serialization")
        result[YARRRML_SERIALIZATION] = names[serialization]
    compression = _single(graph, destination, RML.compression)
    if compression is not None:
        if not str(compression).startswith(RML_URI):
            raise InvalidMappingError("Unsupported target compression")
        result[YARRRML_COMPRESSION] = str(compression).removeprefix(RML_URI)
    return [result]


def read_graph_map(graph, node):
    value = read_expression(graph, node)
    targets = read_targets(graph, node)
    return {YARRRML_VALUE: value, YARRRML_TARGETS: targets} if targets else value


def read_function(graph, execution):
    function = _single(graph, execution, RML.function, required=True)
    parameters = []
    for input_node in graph.objects(execution, RML.input):
        parameter = _single(graph, input_node, RML.parameter, required=True)
        input_map = _single(graph, input_node, RML.inputValueMap)
        input_value = _single(graph, input_node, RML.inputValue)
        if (input_map is None) == (input_value is None):
            raise InvalidMappingError("Function input must have one input value")
        if input_map is not None:
            nested = _single(graph, input_map, RML.functionExecution)
            value = read_function(graph, nested) if nested else read_expression(graph, input_map)
        else:
            if isinstance(input_value, rdflib.Literal) and (input_value.datatype or input_value.language):
                raise InvalidMappingError("Typed function input cannot be represented without loss")
            value = str(input_value)
        parameters.append({YARRRML_PARAMETER: _iri(graph, parameter), YARRRML_VALUE: value})
    return {YARRRML_FUNCTION: _iri(graph, function), YARRRML_PARAMETERS: parameters}


def _mapping_name(value):
    if not isinstance(value, rdflib.URIRef):
        raise InvalidMappingError("Blank-node triples maps cannot be represented in YARRRML")
    return str(value).rsplit("/", 1)[-1].rsplit("#", 1)[-1]


def read_join(graph, node):
    parent = _single(graph, node, RML.parentTriplesMap, required=True)
    result = {YARRRML_MAPPING: _mapping_name(parent)}
    conditions = []
    for condition in graph.objects(node, RML.joinCondition):
        parameters = []
        for name, shortcut, mapping in (
            (YARRRML_JOIN_CHILD_PARAMETER, RML.child, RML.childMap),
            (YARRRML_JOIN_PARENT_PARAMETER, RML.parent, RML.parentMap),
        ):
            reference = _single(graph, condition, shortcut)
            expression_map = _single(graph, condition, mapping)
            if (reference is None) == (expression_map is None):
                raise InvalidMappingError("Join must have one child and one parent expression")
            value = "$(" + str(reference) + ")" if reference is not None else read_expression(graph, expression_map)
            parameters.append([name, value])
        conditions.append({YARRRML_FUNCTION: YARRRML_EQUAL, YARRRML_PARAMETERS: parameters})
    if conditions:
        result[YARRRML_CONDITION] = conditions[0] if len(conditions) == 1 else conditions
    return result


def read_gather(graph, node):
    head = _single(graph, node, RML.gather, required=True)
    gather_as = _single(graph, node, RML.gatherAs, required=True)
    types = {
        rdflib.RDF.List: "list",
        rdflib.RDF.Bag: "bag",
        rdflib.RDF.Seq: "seq",
        rdflib.RDF.Alt: "alt",
    }
    if gather_as not in types:
        raise InvalidMappingError("Unsupported collection type")
    items = []
    for item in Collection(graph, head):
        if graph.value(item, RML.gather) is not None:
            items.append(read_gather(graph, item))
        elif graph.value(item, RML.parentTriplesMap) is not None:
            items.append(read_join(graph, item))
        else:
            items.append(read_expression(graph, item))
    result = {YARRRML_GATHER: items[0] if len(items) == 1 and isinstance(items[0], str) else items,
              YARRRML_GATHER_AS: types[gather_as]}
    if any(graph.value(node, predicate) is not None
           for predicate in (RML.constant, RML.reference, RML.template)):
        result[YARRRML_VALUE] = read_expression(graph, node)
    strategy = _single(graph, node, RML.strategy)
    if strategy is not None:
        result[YARRRML_STRATEGY] = str(strategy).removeprefix(RML_URI)
    allow_empty = _single(graph, node, RML.allowEmptyListAndContainer)
    if allow_empty is not None:
        result[YARRRML_EMPTY] = allow_empty.toPython()
    return result


def read_object(graph, node):
    if graph.value(node, RML.parentTriplesMap) is not None:
        return read_join(graph, node)
    execution = _single(graph, node, RML.functionExecution)
    if execution is not None:
        result = read_function(graph, execution)
    elif graph.value(node, RML.gather) is not None:
        result = read_gather(graph, node)
    else:
        result = {YARRRML_VALUE: read_expression(graph, node)}
        constant = _single(graph, node, RML.constant)
        if isinstance(constant, rdflib.Literal):
            if constant.datatype or constant.language:
                raise InvalidMappingError("Typed or language-tagged constant cannot be represented without loss")
            result[YARRRML_TYPE] = YARRRML_LITERAL_TYPE
    term_type = _single(graph, node, RML.termType)
    types = {RML.IRI: YARRRML_IRI_TYPE, RML.BlankNode: YARRRML_BLANK, RML.Literal: YARRRML_LITERAL_TYPE}
    if term_type is not None:
        if term_type not in types:
            raise InvalidMappingError("Unsupported Core term type")
        result[YARRRML_TYPE] = types[term_type]
    datatype = _single(graph, node, RML.datatype)
    datatype_map = _single(graph, node, RML.datatypeMap)
    language = _single(graph, node, RML.language)
    language_map = _single(graph, node, RML.languageMap)
    if sum(value is not None for value in (datatype, datatype_map, language, language_map)) > 1:
        raise InvalidMappingError("Object has incompatible datatype or language maps")
    if datatype is not None:
        result[YARRRML_DATATYPE] = _iri(graph, datatype)
    elif datatype_map is not None:
        result[YARRRML_DATATYPE] = read_expression(graph, datatype_map)
    elif language is not None:
        result[YARRRML_LANGUAGE] = str(language)
    elif language_map is not None:
        result[YARRRML_LANGUAGE] = read_expression(graph, language_map)
    targets = read_targets(graph, node)
    if targets:
        result[YARRRML_TARGETS] = targets
    return result


def read_predicate_object_maps(graph, triples_map, classes):
    result = [{YARRRML_PREDICATE_SHORT: RDF_TYPE, YARRRML_OBJECT_SHORT: str(cls)} for cls in classes]
    for pom in graph.objects(triples_map, RML.predicateObjectMap):
        predicates = [str(value) for value in graph.objects(pom, RML.predicate)]
        for node in graph.objects(pom, RML.predicateMap):
            execution = _single(graph, node, RML.functionExecution)
            predicate = read_function(graph, execution) if execution else read_expression(graph, node)
            targets = read_targets(graph, node)
            if targets:
                if not isinstance(predicate, dict):
                    predicate = {YARRRML_VALUE: predicate}
                predicate[YARRRML_TARGETS] = targets
            predicates.append(predicate)
        objects = []
        for value in graph.objects(pom, RML.object):
            if isinstance(value, rdflib.Literal):
                if value.datatype or value.language:
                    raise InvalidMappingError("Typed or language-tagged constant cannot be represented without loss")
                objects.append({YARRRML_VALUE: str(value), YARRRML_TYPE: YARRRML_LITERAL_TYPE})
            else:
                objects.append({YARRRML_VALUE: str(value)})
        objects.extend(read_object(graph, node) for node in graph.objects(pom, RML.objectMap))
        graphs = [str(value) for value in graph.objects(pom, RML.graph)]
        graphs.extend(read_graph_map(graph, node) for node in graph.objects(pom, RML.graphMap))
        if not predicates or not objects:
            raise InvalidMappingError("Predicate-object map must have predicates and objects")
        for predicate in predicates:
            for obj in objects:
                for graph_value in graphs or [None]:
                    item = {YARRRML_PREDICATE_SHORT: predicate, YARRRML_OBJECT_SHORT: obj}
                    if graph_value is not None:
                        item[YARRRML_GRAPH] = graph_value
                    result.append(item)
    return result
