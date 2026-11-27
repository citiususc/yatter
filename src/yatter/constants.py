import logging, coloredlogs

##############################################################################
#############################   RML CONSTANTS  ###############################
##############################################################################

RML_OLD_NAMESPACE = 'http://semweb.mmlab.be/ns/rml#'
RML_NAMESPACE = 'http://w3id.org/rml/'
R2RML_NAMESPACE = 'http://www.w3.org/ns/r2rml#'
MAPPING_FORMATS = {
    'RML': RML_NAMESPACE,
    'RML-OLD': RML_OLD_NAMESPACE,
    'R2RML': R2RML_NAMESPACE,
}
RDF_NAMESPACE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
D2RQ_NAMESPACE = 'http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#'
QL_NAMESPACE = 'http://semweb.mmlab.be/ns/ql#'
EXAMPLE_NAMESPACE = 'http://example.com/ns#'
RDFS_NAMESPACE = 'http://www.w3.org/2000/01/rdf-schema#'
XSD_NAMESPACE = 'http://www.w3.org/2001/XMLSchema#'
FOAF_NAMESPACE ='http://xmlns.com/foaf/0.1/'
RDF_TYPE = f"{RDF_NAMESPACE}type"
SCHEMA_NAMESPACE = 'http://schema.org/'
STAR_URI = 'https://w3id.org/kg-construct/rml-star'
COMPRESSION_NAMESPACE = 'http://semweb.mmlab.be/ns/rml-compression#'
FORMATS_NAMESPACE = 'http://www.w3.org/ns/formats/'
VOID_NAMESPACE = 'http://rdfs.org/ns/void#'
FNML_NAMESPACE = 'http://semweb.mmlab.be/ns/fnml#'
GREL_NAMESPACE = 'http://users.ugent.be/~bjdmeest/function/grel.ttl#'
SD_NAMESPACE = 'https://w3id.org/okn/o/sd#'
KG4DI_NAMESPACE = 'https://w3id.org/kg4di/'
DCAT_NAMESPACE = 'http://www.w3.org/ns/dcat#'
SPARQL_SERVICE_NAMESPACE = 'http://www.w3.org/ns/sparql-service-description#'

# Backward-compatible names for the public namespace constants.
RML_OLD_URI = RML_OLD_NAMESPACE
RML_URI = RML_NAMESPACE
R2RML_URI = R2RML_NAMESPACE
RDF_URI = RDF_NAMESPACE
D2RQ_URI = D2RQ_NAMESPACE
QL_URI = QL_NAMESPACE
EXAMPLE_URI = EXAMPLE_NAMESPACE
RDFS_URI = RDFS_NAMESPACE
XSD_URI = XSD_NAMESPACE
FOAF_URI = FOAF_NAMESPACE
SCHEMA_URI = SCHEMA_NAMESPACE
COMPRESSION_URI = COMPRESSION_NAMESPACE
FORMATS_URI = FORMATS_NAMESPACE
VOID_URI = VOID_NAMESPACE
FNML_URI = FNML_NAMESPACE
GREL_URI = GREL_NAMESPACE
SD_URI = SD_NAMESPACE
KG4DI_URI = KG4DI_NAMESPACE
DCAT_URI = DCAT_NAMESPACE
SPARQL_SERVICE_URI = SPARQL_SERVICE_NAMESPACE

RML_PREFIX = '@prefix'
RML_BASE = '@base'
RML_TERM_PREFIX = 'rml:'
R2RML_TERM_PREFIX = 'rr:'
RDF_TERM_PREFIX = 'rdf:'
RDFS_TERM_PREFIX = 'rdfs:'
XSD_TERM_PREFIX = 'xsd:'
QL_TERM_PREFIX = 'ql:'
D2RQ_TERM_PREFIX = 'd2rq:'
FOAF_TERM_PREFIX = 'foaf:'
SCHEMA_TERM_PREFIX = 'schema:'
COMPRESSION_TERM_PREFIX = 'comp:'
FORMATS_TERM_PREFIX = 'formats:'
VOID_TERM_PREFIX = 'void:'
FNML_TERM_PREFIX = 'fnml:'
GREL_TERM_PREFIX = 'grel:'
SD_TERM_PREFIX = 'sd:'
KG4DI_TERM_PREFIX = 'kg4di:'
DCAT_TERM_PREFIX = 'dcat:'
SPARQL_SERVICE_TERM_PREFIX = 'sd:'
RML_LOGICAL_SOURCE_CLASS = f"{RML_NAMESPACE}LogicalSource"
RML_LOGICAL_SOURCE = f"{RML_NAMESPACE}logicalSource"
RML_SOURCE = f"{RML_NAMESPACE}source"
RML_REFERENCE_FORMULATION = f"{RML_NAMESPACE}referenceFormulation"
RML_REFERENCE_FORMULATION_CLASS = f"{RML_NAMESPACE}ReferenceFormulation"
RML_ITERATOR = f"{RML_NAMESPACE}iterator"
RML_REFERENCE = f"{RML_NAMESPACE}reference"
RML_LANGUAGE_MAP = f"{RML_NAMESPACE}languageMap"
RML_LANGUAGE_MAP_CLASS = f"{RML_NAMESPACE}LanguageMap"
RML_DATATYPE_MAP = f"{RML_NAMESPACE}datatypeMap"
RML_DATATYPE_MAP_CLASS = f"{RML_NAMESPACE}DatatypeMap"
RML_QUERY = f"{RML_NAMESPACE}query"
RML_SOURCE_CLASS = f"{RML_NAMESPACE}Source"
RML_FILE_PATH_CLASS = f"{RML_NAMESPACE}FilePath"
RML_PATH = f"{RML_NAMESPACE}path"
RML_SQL_QUERY_FORMULATION = 'SQL2008Query'
RML_SQL_TABLE_FORMULATION = 'SQL2008Table'
R2RML_SQL_VERSION_NAME = 'SQL2008'
R2RML_SQL_VERSION_DEFAULT = R2RML_NAMESPACE + R2RML_SQL_VERSION_NAME

RML_LOGICAL_TARGET = f"{RML_NAMESPACE}logicalTarget"
RML_LOGICAL_TARGET_CLASS = f"{RML_NAMESPACE}LogicalTarget"
RML_TARGET = f"{RML_NAMESPACE}target"
RML_SERIALIZATION = f"{RML_NAMESPACE}serialization"
RML_COMPRESSION = f"{RML_NAMESPACE}compression"

RML_EXECUTION = f"{FNML_NAMESPACE}execution"
RML_EXECUTION_CLASS = f"{FNML_NAMESPACE}Execution"
RML_RETURN = f"{FNML_NAMESPACE}return"
RML_FUNCTION = f"{FNML_NAMESPACE}function"
RML_INPUT = f"{FNML_NAMESPACE}input"
RML_INPUT_CLASS = f"{FNML_NAMESPACE}Input"
RML_PARAMETER = f"{FNML_NAMESPACE}parameter"
RML_VALUE_MAP = f"{FNML_NAMESPACE}valueMap"
RML_VALUE_MAP_CLASS = f"{FNML_NAMESPACE}ValueMap"

RML_CC_GATHER = f"{RML_NAMESPACE}gather"
RML_CC_GATHER_AS = f"{RML_NAMESPACE}gatherAs"
RML_CC_EMPTY = f"{RML_NAMESPACE}allowEmptyListAndContainer"
RML_CC_STRATEGY = f"{RML_NAMESPACE}strategy"

STAR_CLASS = f"{RML_OLD_NAMESPACE}StarMap"
STAR_NON_ASSERTED_CLASS = f"{RML_OLD_NAMESPACE}NonAssertedTriplesMap"
STAR_QUOTED = f"{RML_OLD_NAMESPACE}quotedTriplesMap"
STAR_SUBJECT = f"{RML_OLD_NAMESPACE}subjectMap"
STAR_OBJECT = f"{RML_OLD_NAMESPACE}objectMap"

R2RML_TEMPLATE = f"{R2RML_NAMESPACE}template"
R2RML_TRIPLES_MAP = f"{R2RML_NAMESPACE}TriplesMap"
R2RML_CONSTANT = f"{R2RML_NAMESPACE}constant"
R2RML_SUBJECT = f"{R2RML_NAMESPACE}subjectMap"
R2RML_SUBJECT_CLASS = f"{R2RML_NAMESPACE}SubjectMap"
R2RML_CLASS = f"{R2RML_NAMESPACE}class"
R2RML_SQL_VERSION = f"{R2RML_NAMESPACE}sqlVersion"
R2RML_SQL_QUERY = f"{R2RML_NAMESPACE}sqlQuery"
R2RML_PREDICATE_OBJECT_MAP = f"{R2RML_NAMESPACE}predicateObjectMap"
R2RML_PREDICATE_OBJECT_MAP_CLASS = f"{R2RML_NAMESPACE}PredicateObjectMap"
R2RML_SHORTCUT_PREDICATE = f"{R2RML_NAMESPACE}predicate"
R2RML_PREDICATE = f"{R2RML_NAMESPACE}predicateMap"
R2RML_PREDICATE_CLASS = f"{R2RML_NAMESPACE}PredicateMap"
R2RML_SHORTCUT_OBJECT = f"{R2RML_NAMESPACE}object"
R2RML_OBJECT = f"{R2RML_NAMESPACE}objectMap"
R2RML_OBJECT_CLASS = f"{R2RML_NAMESPACE}ObjectMap"
R2RML_GRAPH = f"{R2RML_NAMESPACE}graph"
R2RML_GRAPH_MAP = f"{R2RML_NAMESPACE}graphMap"
R2RML_GRAPH_CLASS = f"{R2RML_NAMESPACE}GraphMap"
R2RML_DATATYPE = f"{R2RML_NAMESPACE}datatype"
R2RML_TERMTYPE = f"{R2RML_NAMESPACE}termType"
R2RML_LANGUAGE = f"{R2RML_NAMESPACE}language"
R2RML_IRI = f"{R2RML_NAMESPACE}IRI"
R2RML_BLANK_NODE = f"{R2RML_NAMESPACE}BlankNode"
R2RML_LITERAL = f"{R2RML_NAMESPACE}Literal"
R2RML_REFOBJECT_CLASS = f"{R2RML_NAMESPACE}RefObjectMap"
R2RML_PARENT_TRIPLESMAP = f"{R2RML_NAMESPACE}parentTriplesMap"
R2RML_JOIN_CONITION = f"{R2RML_NAMESPACE}joinCondition"
R2RML_CHILD = f"{R2RML_NAMESPACE}child"
R2RML_PARENT = f"{R2RML_NAMESPACE}parent"
R2RML_LOGICAL_TABLE_CLASS = f"{R2RML_NAMESPACE}LogicalTable"
R2RML_LOGICAL_TABLE = f"{R2RML_NAMESPACE}logicalTable"
R2RML_TABLE_NAME = f"{R2RML_NAMESPACE}tableName"
R2RML_COLUMN = f"{R2RML_NAMESPACE}column"

SPARQL_ENDPOINT = f"{SPARQL_SERVICE_NAMESPACE}endpoint"
SPARQL_SUPPORTED_LANGUAGE = f"{SPARQL_SERVICE_NAMESPACE}supportedLanguage"
SPARQL_11_UPDATE = f"{SPARQL_SERVICE_NAMESPACE}SPARQL11Update"
DCAT_DATASET = f"{DCAT_NAMESPACE}Dataset"
DCAT_DATA_DUMP = f"{DCAT_NAMESPACE}dataDump"
VOID_DATASET = f"{VOID_NAMESPACE}Dataset"
VOID_DATA_DUMP = f"{VOID_NAMESPACE}dataDump"
FORMATS_NQUADS = f"{FORMATS_NAMESPACE}N-Quads"

# Terms shared by R2RML and Core retain their local names.
R2RML_CORE_SHARED_TERMS = (
    R2RML_TRIPLES_MAP, R2RML_TEMPLATE, R2RML_CONSTANT, R2RML_SUBJECT,
    R2RML_SUBJECT_CLASS, R2RML_CLASS, R2RML_PREDICATE,
    R2RML_SHORTCUT_PREDICATE, R2RML_PREDICATE_CLASS, R2RML_OBJECT,
    R2RML_SHORTCUT_OBJECT, R2RML_OBJECT_CLASS, R2RML_GRAPH_MAP,
    R2RML_GRAPH, R2RML_GRAPH_CLASS, R2RML_PREDICATE_OBJECT_MAP,
    R2RML_REFOBJECT_CLASS, R2RML_PARENT_TRIPLESMAP, R2RML_JOIN_CONITION,
    R2RML_CHILD, R2RML_PARENT, R2RML_DATATYPE, R2RML_LANGUAGE,
    R2RML_TERMTYPE, R2RML_IRI, R2RML_BLANK_NODE, R2RML_LITERAL,
)

RML_CORE_TERM_OVERRIDES = {
    R2RML_COLUMN: RML_REFERENCE,
    RML_EXECUTION: f"{RML_NAMESPACE}functionExecution",
    RML_EXECUTION_CLASS: f"{RML_NAMESPACE}FunctionExecution",
    RML_FUNCTION: f"{RML_NAMESPACE}function",
    RML_INPUT: f"{RML_NAMESPACE}input",
    RML_INPUT_CLASS: f"{RML_NAMESPACE}Input",
    RML_PARAMETER: f"{RML_NAMESPACE}parameter",
    RML_VALUE_MAP: f"{RML_NAMESPACE}inputValueMap",
    RML_VALUE_MAP_CLASS: f"{RML_NAMESPACE}TermMap",
}


##############################################################################
#############################   D2RQ CONSTANTS  ###########################
##############################################################################
D2RQ_DATABASE_CLASS = f"{D2RQ_NAMESPACE}Database"
D2RQ_DSN = f"{D2RQ_NAMESPACE}jdbcDSN"
D2RQ_DRIVER = f"{D2RQ_NAMESPACE}jdbcDriver"
D2RQ_USER = f"{D2RQ_NAMESPACE}username"
D2RQ_PASS = f"{D2RQ_NAMESPACE}password"

##############################################################################
#############################   SD CONSTANTS  ###########################
##############################################################################
SD_DATASET_SPEC = f"{SD_NAMESPACE}DatasetSpecification"
SD_NAME = f"{SD_NAMESPACE}name"
SD_HAS_DATA_TRANSFORMATION = f"{SD_NAMESPACE}hasDataTransformation"
SD_HAS_SOFTWARE_REQUIREMENTS = f"{SD_NAMESPACE}hasSoftwareRequirements"
SD_HAS_SOURCE_CODE= f"{SD_NAMESPACE}hasSourceCode"
SD_PROGRAMMING_LANGUAGE =  f"{SD_NAMESPACE}programmingLanguage"
KG4DI_DEFINED_BY = f"{KG4DI_NAMESPACE}definedBy"
##############################################################################
#############################   YARRRML CONSTANTS  ###########################
##############################################################################

YARRRML_PREFIXES = 'prefixes'
YARRRML_SOURCES = 'sources'
YARRRML_SOURCE = 'source'
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
YARRRML_SUBJECT_SHORT = 's'
YARRRML_AUTHORS = 'authors'
YARRRML_GRAPHS = 'graphs'

YARRRML_PREDICATEOBJECT = 'predicateobjects'
YARRRML_PREDICATEOBJECT_SHORT = 'po'

YARRRML_PREDICATES = 'predicates'
YARRRML_PREDICATE_SHORT = 'p'
YARRRML_OBJECTS = 'objects'
YARRRML_OBJECT_SHORT = 'o'
YARRRML_GRAPH = 'graph'
YARRRML_VALUE = 'value'
YARRRML_DATATYPE = 'datatype'
YARRRML_LANGUAGE = 'language'

YARRRML_CONDITION = 'condition'
YARRRML_EQUAL = 'equal'
YARRRML_JOIN = 'join'
YARRRML_PARAMETERS = 'parameters' #used for conditions and functions


YARRRML_IRI = '~iri'
YARRRML_LANG = '~lang'
YARRRML_IRI_TYPE = 'iri'
YARRRML_BLANK = 'blank'
YARRRML_LITERAL_TYPE = 'literal'

YARRRML_QUOTED = 'quoted'
YARRRML_NON_ASSERTED = 'quotedNonAsserted'

YARRRML_TARGETS = 'targets'
YARRRML_SERIALIZATION = 'serialization'
YARRRML_COMPRESSION = 'compression'
YARRRML_TARGET_SPARQL = 'sparql'
YARRRML_TARGET_DCAT = 'dcat'
YARRRML_TARGET_VOID = 'void'

YARRRML_FUNCTION = 'function'

YARRRML_PARAMETER = 'parameter'
YARRRML_JOIN_CHILD_PARAMETER = 'str1'
YARRRML_JOIN_PARENT_PARAMETER = 'str2'

YARRRML_GATHER = 'gather'
YARRRML_GATHER_AS = 'gatherAs'
YARRRML_GATHER_AS_OPTIONS = ["alt","bag","seq","list"]
YARRRML_EMPTY = 'empty'
YARRRML_STRATEGY = 'strategy'
YARRRML_STRATEGY_OPTIONS = ['append', 'cartesianProduct']

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

basic_types = [int, float]

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', fmt='%(asctime)s,%(msecs)03d | %(levelname)s: %(message)s', logger=logger)
