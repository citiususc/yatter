import logging, coloredlogs

##############################################################################
#############################   RML CONSTANTS  ###############################
##############################################################################

RML_URI = 'http://semweb.mmlab.be/ns/rml#'
R2RML_URI = 'http://www.w3.org/ns/r2rml#'
RDF_URI = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
D2RQ_URI = 'http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#'
QL_URI = 'http://semweb.mmlab.be/ns/ql#'
EXAMPLE_URI = 'http://example.com/ns#'
RDFS_URI = 'http://www.w3.org/2000/01/rdf-schema#'
XSD_URI = 'http://www.w3.org/2001/XMLSchema#'
FOAF_URI ='http://xmlns.com/foaf/0.1/'
RDF_TYPE = 'rdf:type'
SCHEMA_URI = 'http://schema.org/'
STAR_URI = 'https://w3id.org/kg-construct/rml-star'
COMPRESSION_URI = 'http://semweb.mmlab.be/ns/rml-compression#'
FORMATS_URI = 'http://www.w3.org/ns/formats/'
VOID_URI = 'http://rdfs.org/ns/void#'
FNML_URI = 'http://semweb.mmlab.be/ns/fnml#'
GREL_URI = 'http://users.ugent.be/~bjdmeest/function/grel.ttl#'
SD_URI = 'https://w3id.org/okn/o/sd#'

RML_PREFIX = '@prefix'
RML_BASE = '@base'
RML_LOGICAL_SOURCE_CLASS = 'rml:LogicalSource'
RML_LOGICAL_SOURCE = 'rml:logicalSource'
RML_SOURCE = 'rml:source'
RML_REFERENCE_FORMULATION = 'rml:referenceFormulation'
RML_REFERENCE_FORMULATION_CLASS = 'rml:ReferenceFormulation'
RML_ITERATOR = 'rml:iterator'
RML_REFERENCE = 'rml:reference'
RML_LANGUAGE_MAP = 'rml:languageMap'
RML_LANGUAGE_MAP_CLASS = 'rml:LanguageMap'
RML_DATATYPE_MAP = 'rml:datatypeMap'
RML_DATATYPE_MAP_CLASS = 'rml:DatatypeMap'
RML_QUERY = 'rml:query'

RML_LOGICAL_TARGET = 'rml:logicalTarget'
RML_LOGICAL_TARGET_CLASS = 'rml:LogicalTarget'
RML_TARGET = 'rml:target'
RML_SERIALIZATION = 'rml:serialization'
RML_COMPRESSION = 'rml:compression'

RML_EXECUTION = 'fnml:execution'
RML_EXECUTION_CLASS = 'fnml:Execution'
RML_RETURN = 'fnml:return'
RML_FUNCTION = 'fnml:function'
RML_INPUT = 'fnml:input'
RML_INPUT_CLASS = 'fnml:Input'
RML_PARAMETER = 'fnml:parameter'
RML_VALUE_MAP = 'fnml:valueMap'
RML_VALUE_MAP_CLASS = 'fnml:ValueMap'

RML_CC_GATHER = 'rml:gather'
RML_CC_GATHER_AS = 'rml:gatherAs'
RML_CC_EMPTY = 'rml:allowEmptyListAndContainer'
RML_CC_STRATEGY = 'rml:strategy'

STAR_CLASS = 'rml:StarMap'
STAR_NON_ASSERTED_CLASS = 'rml:NonAssertedTriplesMap'
STAR_QUOTED = 'rml:quotedTriplesMap'
STAR_SUBJECT = 'rml:subjectMap'
STAR_OBJECT = 'rml:objectMap'

R2RML_TEMPLATE = 'rr:template'
R2RML_TRIPLES_MAP = 'rr:TriplesMap'
R2RML_CONSTANT = 'rr:constant'
R2RML_SUBJECT = 'rr:subjectMap'
R2RML_SUBJECT_CLASS = 'rr:SubjectMap'
R2RML_CLASS = 'rr:class'
R2RML_SQL_VERSION = 'rr:sqlVersion'
R2RML_SQL_QUERY = 'rr:sqlQuery'
R2RML_PREDICATE_OBJECT_MAP = 'rr:predicateObjectMap'
R2RML_PREDICATE_OBJECT_MAP_CLASS = 'rr:PredicateObjectMap'
R2RML_SHORTCUT_PREDICATE = 'rr:predicate'
R2RML_PREDICATE = 'rr:predicateMap'
R2RML_PREDICATE_CLASS = 'rr:PredicateMap'
R2RML_SHORTCUT_OBJECT = 'rr:object'
R2RML_OBJECT = 'rr:objectMap'
R2RML_OBJECT_CLASS = 'rr:ObjectMap'
R2RML_GRAPH = 'rr:graph'
R2RML_GRAPH_MAP = 'rr:graphMap'
R2RML_GRAPH_CLASS = 'rr:GraphMap'
R2RML_DATATYPE = 'rr:datatype'
R2RML_TERMTYPE = 'rr:termType'
R2RML_LANGUAGE = 'rr:language'
R2RML_IRI = 'rr:IRI'
R2RML_BLANK_NODE = 'rr:BlankNode'
R2RML_LITERAL = 'rr:Literal'
R2RML_REFOBJECT_CLASS = 'rr:RefObjectMap'
R2RML_PARENT_TRIPLESMAP = 'rr:parentTriplesMap'
R2RML_JOIN_CONITION = 'rr:joinCondition'
R2RML_CHILD = 'rr:child'
R2RML_PARENT = 'rr:parent'
R2RML_LOGICAL_TABLE_CLASS = 'rr:LogicalTable'
R2RML_LOGICAL_TABLE = 'rr:logicalTable'
R2RML_TABLE_NAME = 'rr:tableName'
R2RML_COLUMN = 'rr:column'


##############################################################################
#############################   D2RQ CONSTANTS  ###########################
##############################################################################
D2RQ_DATABASE_CLASS = 'd2rq:Database'
D2RQ_DSN = 'd2rq:jdbcDSN'
D2RQ_DRIVER = 'd2rq:jdbcDriver'
D2RQ_USER = 'd2rq:username'
D2RQ_PASS = 'd2rq:password'

##############################################################################
#############################   SD CONSTANTS  ###########################
##############################################################################
SD_DATASET_SPEC = 'sd:DatasetSpecification'
SD_NAME = 'sd:name'
SD_HAS_DATA_TRANSFORMATION = 'sd:hasDataTransformation'
SD_HAS_SOFTWARE_REQUIREMENTS = 'sd:hasSoftwareRequirements'
SD_HAS_SOURCE_CODE= 'sd:hasSourceCode'
SD_PROGRAMMING_LANGUAGE =  'sd:programmingLanguage'
KG4DI_DEFINED_BY = 'kg4di:definedBy'
##############################################################################
#############################   YARRRML CONSTANTS  ###########################
##############################################################################

YARRRML_PREFIXES = 'prefixes'
YARRRML_SOURCES = 'sources'
YARRRML_TABLE = 'table'
YARRRML_ACCESS = 'access'
YARRRML_QUERY = 'query'
YARRRML_REFERENCE_FORMULATION = 'referenceFormulation'
YARRRML_QUERY_FORMULATION = 'queryFormulation'
YARRRML_ITERATOR = 'iterator'
YARRRML_CREDENTIALS = 'credentials'
YARRRML_TYPE = 'type'
YARRRML_USERNAME = 'username'
YARRRML_PASSWORD = 'password'

YARRRML_STRUCTURE_DEFINER = 'structureDefiner'
YARRRML_SOFTWARE_SPECIFICATION = 'softwareSpecification'
YARRRML_PROGRAMMING_LANGUAGE = 'programmingLanguage'
YARRRML_SOFTWARE_REQUIREMENTS = 'softwareRequirements'

YARRRML_MAPPINGS = 'mappings' # used for mappings in conditions and mappings main key
YARRRML_MAPPING = 'mapping'

YARRRML_SUBJECTS = 'subjects'
YARRRML_AUTHORS = 'authors'
YARRRML_GRAPHS = 'graphs'

YARRRML_PREDICATEOBJECT = 'predicateobjects'

YARRRML_PREDICATES = 'predicates'
YARRRML_OBJECTS = 'objects'
YARRRML_VALUE = 'value'
YARRRML_DATATYPE = 'datatype'
YARRRML_LANGUAGE = 'language'

YARRRML_CONDITION = 'condition'
YARRRML_EQUAL = 'equal'
YARRRML_JOIN = 'join'
YARRRML_PARAMETERS = 'parameters' #used for conditions and functions


YARRRML_IRI = '~iri'
YARRRML_LANG = '~lang'
YARRRML_BLANK = 'blank'

YARRRML_QUOTED = 'quoted'
YARRRML_NON_ASSERTED = 'quotedNonAsserted'

YARRRML_TARGETS = 'targets'
YARRRML_SERIALIZATION = 'serialization'
YARRRML_COMPRESSION = 'compression'

YARRRML_FUNCTION = 'function'

YARRRML_PARAMETER = 'parameter'

YARRRML_GATHER = 'gather'
YARRRML_GATHER_AS = 'gatherAs'
YARRRML_GATHER_AS_OPTIONS = ["alt","bag","seq","list"]
YARRRML_EMPTY = 'empty'
YARRRML_STRATEGY = 'strategy'

YARRRML_MAPPING_KEYS = [YARRRML_MAPPINGS, YARRRML_MAPPING]
YARRRML_SUBJECT_KEYS = [YARRRML_SUBJECTS]
YARRRML_POM_KEYS = [YARRRML_PREDICATEOBJECT]
YARRRML_GRAPH_KEYS = [YARRRML_GRAPHS]
YARRRML_PREDICATE_KEYS = [YARRRML_PREDICATES]
YARRRML_OBJECT_KEYS = [YARRRML_OBJECTS]
YARRRML_FUNCTION_KEYS = [YARRRML_FUNCTION]
YARRRML_PARAMETERS_KEYS = [YARRRML_PARAMETERS]
YARRRML_PARAMETER_KEYS = [YARRRML_PARAMETER]
YARRRML_VALUE_KEYS = [YARRRML_VALUE]


YARRRML_OUTPUT_FORMAT = {
    'jsonld':'JSON-LD',
    'n3':'N3',
    'ntriples':'N-Triples',
    'nquads':'N-Quads',
    'ldpatch':'LD_Patch',
    'microdata':'microdata',
    'owlxml':'OWL_XML',
    'owlfunctional':'OWL_Functional',
    'oxmlmanchester':'OWL_Manchester',
    'powder':'POWDER',
    'powder-s':'POWDER-S',
    'prov-n':'PROV-N',
    'prov-xml':'PROV-XML',
    'rdfa':'RDFa',
    'rdfjson':'RDF_JSON',
    'rdfxml':'RDF_XML',
    'rifxml':'RIF_XML',
    'sparqlxml':'SPARQL_Results_XML',
    'sparqljson':'SPARQL_Results_JSON',
    'sparqlcsv':'SPARQL_Results_CSV',
    'sparqltsv':'SPARQL_Results_TSV',
    'turtle':'Turtle',
    'trig':'TriG',
}

YARRRML_REFERENCE_FORMULATIONS = {
    'csv': 'CSV',
    'json': 'JSONPath',
    'xpath': 'XPath',
    'jsonpath': 'JSONPath',
    "shp": "SHP",
    "xlsx": "CSV"
}

YARRRML_DATABASES_DRIVER = {
    'mysql': 'com.mysql.jdbc.Driver',
    'postgresql': 'org.postgresql.Driver',
    'sqlserver': 'com.microsoft.sqlserver.jdbc.SQLServerDriver'
}

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', fmt='%(asctime)s,%(msecs)03d | %(levelname)s: %(message)s', logger=logger)
