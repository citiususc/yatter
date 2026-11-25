import os
import re
import rdflib
from .constants import *
from .errors import InvalidMappingError
from ruamel.yaml import YAML




def add_source(data, mapping, external_sources=None, mapping_format=RML_OLD_URI):
    if external_sources is None:
        external_sources = {}
    if mapping_format == RML_URI:
        return add_core_sources(data, mapping, external_sources)

    source_template = "\t" + RML_LOGICAL_SOURCE + " [\n\t\ta " + RML_LOGICAL_SOURCE_CLASS + \
                      ";\n\t\t" + RML_SOURCE + " "
    final_list = []
    sources = data.get(YARRRML_MAPPINGS).get(mapping).get(YARRRML_SOURCES)
    external_references_list = []
    for source in sources:
        db_identifier = mapping
        for external_Source in external_sources:
            external_source = {k: v for k, v in external_sources[external_Source].items() if k != YARRRML_MAPPINGS}
            if source == external_source:
                db_identifier = external_Source
        if YARRRML_ACCESS in source:
            if YARRRML_QUERY in source:
                final_list.append(source_template + database_source(mapping, source, db_identifier))
            elif YARRRML_STRUCTURE_DEFINER in source:
                source, external_references = add_in_memory_source(mapping,source)
                final_list.append(source_template + source)
                if external_references is not None:
                    external_references_list.append(external_references)
            else:
                final_list.append(source_template + add_source_full(mapping, source))
        elif type(source) is list: # ToDo: review for in_memory sources
            if "$(" in source[0]:
                source, external_references = add_in_memory_source(mapping, source)
                final_list.append(source_template + source)
                if external_references is not None:
                    external_references_list.append(external_references)
            else:
                final_list.append(source_template + add_source_simplified(mapping, source)) # this probably needs to be removed
        else:
            raise InvalidMappingError(
                f"ERROR: source {source} in mapping {mapping} not valid"
            )
    return final_list, external_references_list


def add_core_sources(data, mapping, external_sources):
    results = []
    external_references = []
    for source in data[YARRRML_MAPPINGS][mapping][YARRRML_SOURCES]:
        if not isinstance(source, dict) or YARRRML_ACCESS not in source:
            raise InvalidMappingError(
                f"RML-Core source in mapping {mapping} requires an access description"
            )
        if YARRRML_STRUCTURE_DEFINER in source:
            description, reference = add_in_memory_source(mapping, source)
            results.append(
                f"\t{RML_LOGICAL_SOURCE} [\n\t\ta {RML_LOGICAL_SOURCE_CLASS};\n"
                f"\t\t{RML_SOURCE} "
                + description
            )
            if reference is not None:
                external_references.append(reference)
            continue

        access = str(source[YARRRML_ACCESS])
        if YARRRML_QUERY in source or YARRRML_TABLE in source:
            identifier = mapping
            for name, external_source in external_sources.items():
                if source == {k: v for k, v in external_source.items() if k != YARRRML_MAPPINGS}:
                    identifier = name
                    break
            source_value = f"<DataSource_{identifier}>"
            key = YARRRML_QUERY if YARRRML_QUERY in source else YARRRML_TABLE
            formulation = RML_SQL_QUERY_FORMULATION if key == YARRRML_QUERY else RML_SQL_TABLE_FORMULATION
            iterator = str(source[key])
        else:
            source_value = (
                f"[ a {RML_SOURCE_CLASS}, {RML_FILE_PATH_CLASS};\n"
                f"\t\t\t{RML_PATH} {rdflib.Literal(access).n3()};\n\t\t]"
            )
            formulation_key = source.get(YARRRML_REFERENCE_FORMULATION)
            if formulation_key is None:
                formulation_key = os.path.splitext(access)[1].lstrip(".").lower()
            formulation = YARRRML_REFERENCE_FORMULATIONS.get(str(formulation_key).lower())
            if formulation is None:
                raise InvalidMappingError(
                    f"Unsupported reference formulation {formulation_key} in mapping {mapping}"
                )
            iterator = source.get(YARRRML_ITERATOR)

        result = (
            f"\t{RML_LOGICAL_SOURCE} [\n\t\ta {RML_LOGICAL_SOURCE_CLASS};\n"
            f"\t\t{RML_SOURCE} {source_value};\n"
            f"\t\t{RML_REFERENCE_FORMULATION} {RML_TERM_PREFIX}{formulation}"
        )
        if iterator is not None:
            result += f";\n\t\t{RML_ITERATOR} {rdflib.Literal(str(iterator)).n3()}"
        results.append(result + "\n\t];\n")
    return results, external_references


def add_table(data, mapping):
    table_template = "\t" + R2RML_LOGICAL_TABLE + " [\n\t\ta " + R2RML_LOGICAL_TABLE_CLASS + \
                     ";\n\t\t"

    final_list = []
    sources = data.get(YARRRML_MAPPINGS).get(mapping).get(YARRRML_SOURCES)
    for source in sources:
        sql_version = False
        db_identifier = mapping
        if YARRRML_ACCESS in source and YARRRML_QUERY in source:
            r2rml_access = database_source(mapping, source, db_identifier)
            sql_version = True
        elif YARRRML_QUERY in source:
            r2rml_access = R2RML_SQL_QUERY + " \"" + source.get(YARRRML_QUERY).replace("\n", " ").replace("\"",
                                                                                                          "\\\"") + "\""
        elif YARRRML_TABLE in source:
            r2rml_access = R2RML_TABLE_NAME + " \"" + source.get(YARRRML_TABLE) + "\""
        else:
            raise InvalidMappingError(
                f"ERROR: table or query is not provided in {source} of mapping {mapping}"
            )
        if not sql_version:
            if YARRRML_QUERY_FORMULATION in source:
                r2rml_access += ";\n\t\t" + R2RML_SQL_VERSION + " " + R2RML_TERM_PREFIX + source.get(YARRRML_QUERY_FORMULATION).upper()
            else:
                r2rml_access += ";\n\t\t" + R2RML_SQL_VERSION + " " + R2RML_SQL_VERSION_DEFAULT
            r2rml_access += "\n\t];\n"
        final_list.append(table_template + r2rml_access)
    return final_list



def add_source_simplified(mapping, source):
    source_rdf = ""
    file_path = re.sub("~.*", "", source[0])
    reference_formulation = source[0].split('~')[1]
    source_extension = os.path.splitext(file_path)[1].replace(".","")
    ref_formulation_rml = YARRRML_REFERENCE_FORMULATIONS[reference_formulation]

    if switch_in_reference_formulation(reference_formulation, source_extension) != source_extension:
        raise InvalidMappingError(
            "ERROR: mismatch extension and referenceFormulation in source "
            + str(source) + " in mapping " + mapping
        )
    else:
        if len(source) == 1:  # do not have iterator
            if source_extension == "csv" or source_extension == R2RML_SQL_VERSION_NAME or source_extension == "xlsx":
                source_rdf += '"' + file_path + '"' + ";\n" + "\t\t" + RML_REFERENCE_FORMULATION + " " + QL_TERM_PREFIX \
                              + ref_formulation_rml + "\n" + "\t];\n"
            else:
                raise InvalidMappingError(
                    f"ERROR: source {source} in mapping {mapping} has no iterator"
                )
        else:  # source[1] is the iterator for json and xml
            source_rdf += "\"" + file_path + "\";\n\t\t" + RML_REFERENCE_FORMULATION + " " + QL_TERM_PREFIX \
                          + ref_formulation_rml + ";\n\t\t" + RML_ITERATOR + " \"" \
                          + source[1] + "\";\n\t];\n"
    return source_rdf

def add_in_memory_source(mapping, source):
    external_reference_formulation = None
    if type(source) is list:
        source = extend_in_memory(source)
    source_rdf = "[\n\t\t\ta " + SD_DATASET_SPEC + ";\n\t\t\t"

    access = str(source.get(YARRRML_ACCESS)).replace("$(","").replace(")","")
    source_rdf += SD_NAME + " \"" + access + "\";\n"

    if YARRRML_SOFTWARE_SPECIFICATION in source:
        source_rdf += "\t\t\t" + SD_HAS_DATA_TRANSFORMATION + "[\n\t\t\t\t"

        if YARRRML_SOFTWARE_REQUIREMENTS in source.get(YARRRML_SOFTWARE_SPECIFICATION):
            software_requirements = str(source.get(YARRRML_SOFTWARE_SPECIFICATION)[YARRRML_SOFTWARE_REQUIREMENTS])
            source_rdf += SD_HAS_SOFTWARE_REQUIREMENTS + " \""+ software_requirements +"\";\n\t\t\t\t"

        if YARRRML_PROGRAMMING_LANGUAGE in source.get(YARRRML_SOFTWARE_SPECIFICATION):
            programming_language = str(source.get(YARRRML_SOFTWARE_SPECIFICATION)[YARRRML_PROGRAMMING_LANGUAGE])
            source_rdf += SD_HAS_SOURCE_CODE +"[\n\t\t\t\t\t" + SD_PROGRAMMING_LANGUAGE + " \"" + programming_language + "\";"
            source_rdf +="\n\t\t\t\t];\n"

        source_rdf += "\t\t\t];\n"
    source_rdf += "\t\t];\n"

    if YARRRML_ITERATOR in source:
        source_rdf += "\t\t" + RML_ITERATOR + " \"" + source.get(YARRRML_ITERATOR) + "\";\n"

    if YARRRML_REFERENCE_FORMULATION in source:
        reference_formulation = str(source.get(YARRRML_REFERENCE_FORMULATION))
        source_rdf += "\t\t" + RML_REFERENCE_FORMULATION + " " + QL_TERM_PREFIX + reference_formulation + ";\n"
        external_reference_formulation = QL_TERM_PREFIX + reference_formulation + " a " + RML_REFERENCE_FORMULATION_CLASS +";\n"
        external_reference_formulation +="\t" + KG4DI_DEFINED_BY +" \""+source.get(YARRRML_STRUCTURE_DEFINER) +"\"."
    source_rdf += "\t];\n"



    return source_rdf, external_reference_formulation

def extend_in_memory(source):
    features = source[0].split("~")
    access = features[0]
    defined_by = features[1].split("-")[0]
    reference_formulation = features[1].split("-")[1]
    extended_source = {
        YARRRML_ACCESS: access,
        YARRRML_STRUCTURE_DEFINER: defined_by,
        YARRRML_REFERENCE_FORMULATION: reference_formulation,
    }
    if len(source) == 2:
        extended_source[YARRRML_ITERATOR] = source[1]
    return extended_source


def add_source_full(mapping, source):
    source_rdf = ""

    access = str(source.get(YARRRML_ACCESS))
    extension = os.path.splitext(access)[1][1:]
    if YARRRML_REFERENCE_FORMULATION in source:
        reference_formulation = str(source.get(YARRRML_REFERENCE_FORMULATION))
        format_from_reference = switch_in_reference_formulation(reference_formulation.lower())
        ref_formulation_rml = YARRRML_REFERENCE_FORMULATIONS[reference_formulation]

        if extension != format_from_reference or format_from_reference == "ERROR":
            raise InvalidMappingError(
                "ERROR: not referenceFormulation found or mismatch between the format and "
                f"referenceFormulation in source {access} in mapping {mapping}"
            )
        if YARRRML_ITERATOR in source:
            source_iterator = str(source.get(YARRRML_ITERATOR))

            source_rdf += "\"" + access + "\";\n\t\t" + RML_REFERENCE_FORMULATION + " " + QL_TERM_PREFIX \
                          + ref_formulation_rml + ";\n\t\t" + RML_ITERATOR + " \"" \
                          + source_iterator + "\";\n\t];\n"
        else:
            if extension == "csv" or extension == R2RML_SQL_VERSION_NAME:
                source_rdf += "\"" + access + "\";\n\t\t" + RML_REFERENCE_FORMULATION + " " + QL_TERM_PREFIX \
                              + ref_formulation_rml + "\n\n\t];\n"
            else:
                raise InvalidMappingError(
                    f"ERROR: source {access} in mapping {mapping} has no referenceFormulation"
                )

    else:
        if extension == "csv":
            source_rdf += "\"" + access + "\";\n\n\t];\n"
        else:
            raise InvalidMappingError(
                f"ERROR: source {access} in mapping {mapping} has no referenceFormulation"
            )

    return source_rdf


def database_source(mapping, source, db_identifier):
    source_rdf = ""
    if YARRRML_ACCESS in source:
        if YARRRML_CREDENTIALS in source:
            if YARRRML_TYPE in source:
                source_rdf += "<DataSource_" + str(db_identifier) + ">;\n\t\t"
                if YARRRML_QUERY in source:
                    source_rdf += RML_QUERY + " \"" + source.get(YARRRML_QUERY).replace("\n", " ").replace("\"",
                                                                                                           "\\\"") + "\""
                elif YARRRML_TABLE in source:
                    source_rdf += R2RML_TABLE_NAME + " \"" + source.get(YARRRML_TABLE) + "\""
                if YARRRML_REFERENCE_FORMULATION in source:
                    source_rdf += ";\n\t\t" + RML_REFERENCE_FORMULATION + " " + QL_TERM_PREFIX \
                                  + switch_in_reference_formulation(source.get(YARRRML_REFERENCE_FORMULATION)).upper()
                if YARRRML_QUERY_FORMULATION in source:
                    source_rdf += ";\n\t\t" + R2RML_SQL_VERSION + " " + R2RML_TERM_PREFIX + source.get(YARRRML_QUERY_FORMULATION).upper()
                else:
                    source_rdf += ";\n\t\t" + R2RML_SQL_VERSION + " " + R2RML_SQL_VERSION_DEFAULT
                source_rdf += "\n\t];\n"
        else:
            raise InvalidMappingError(
                f"ERROR: no credentials to get access to source in mapping {mapping}"
            )
    else:
        raise InvalidMappingError(
            f"ERROR: no access to the source in mapping {mapping}"
        )

    return source_rdf


def switch_in_reference_formulation(value, source_extension=None):
    value = value.lower()
    if "json" in value:
        if "path" in value:
            switcher = "json"
        else:
            switcher = "jsonpath"
    elif "x" in value:
        if "path" in value:
            switcher = "xml"
        else:
            switcher = "xpath"
    elif source_extension:
        if source_extension == "xlsx":
            switcher = "xlsx"
        else:
            switcher = value
    else:
        switcher = value
    return switcher


def generate_database_connections(data, external_sources, mapping_format=RML_OLD_URI):
    database = []
    for mapping in data.get(YARRRML_MAPPINGS):
        sources = data.get(YARRRML_MAPPINGS).get(mapping).get(YARRRML_SOURCES)
        for source in sources:
            db_identifier = mapping
            for external_Source in external_sources:
                external_source = {k: v for k, v in external_sources[external_Source].items() if k != YARRRML_MAPPINGS}
                if source == external_source:
                    db_identifier = external_Source
                    break
            if (YARRRML_QUERY in source or
                (mapping_format == RML_URI and YARRRML_TABLE in source)) and YARRRML_ACCESS in source:
                db_type = source.get(YARRRML_TYPE)
                if db_type in YARRRML_DATABASES_DRIVER:
                    driver = YARRRML_DATABASES_DRIVER[db_type]
                else:
                    driver = None
                access = source.get(YARRRML_ACCESS)
                credentials = source.get(YARRRML_CREDENTIALS, {})
                if not isinstance(credentials, dict):
                    raise InvalidMappingError("Database credentials must be a mapping")
                username = credentials.get(YARRRML_USERNAME)
                password = credentials.get(YARRRML_PASSWORD)

                if mapping_format == RML_URI:
                    properties = [D2RQ_DSN + " " + rdflib.Literal(access).n3()]
                    if driver is not None:
                        properties.append(D2RQ_DRIVER + " " + rdflib.Literal(driver).n3())
                    if username is not None:
                        properties.append(D2RQ_USER + " " + rdflib.Literal(username).n3())
                    if password is not None:
                        properties.append(D2RQ_PASS + " " + rdflib.Literal(password).n3())
                    connection_string = ("<DataSource_" + str(db_identifier) + "> a "
                                         + D2RQ_DATABASE_CLASS + ";\n\t"
                                         + ";\n\t".join(properties) + ".\n\n")
                    if connection_string not in database:
                        database.append(connection_string)
                    continue

                if driver is None:
                    connection_string = "<DataSource_" + str(db_identifier) + "> a " + D2RQ_DATABASE_CLASS + ";\n\t" \
                                        + D2RQ_DSN + " \"" + access + "\";\n\t" \
                                        + D2RQ_USER + " \"" + username + "\";\n\t" \
                                        + D2RQ_PASS + " \"" + password + "\".\n\n"
                else:
                    connection_string = "<DataSource_" + str(db_identifier) + "> a " + D2RQ_DATABASE_CLASS + ";\n\t" \
                                        + D2RQ_DSN + " \"" + access + "\";\n\t" \
                                        + D2RQ_DRIVER + " \"" + driver + "\";\n\t" \
                                        + D2RQ_USER + " \"" + username + "\";\n\t" \
                                        + D2RQ_PASS + " \"" + password + "\".\n\n"

                if connection_string not in database:
                    database.append(connection_string)

    return database


def add_inverse_source(tm, rdf_mapping, mapping_format):
    query = f'SELECT ?source  WHERE {{ <{tm}> {R2RML_LOGICAL_TABLE}|{RML_LOGICAL_SOURCE} ?source . }} '
    sources = [
        result[rdflib.Variable('source')]
        for result in rdf_mapping.query(query).bindings
    ]
    if not sources:
        logger.error("Logical Source or Logical Table is not defined in the mapping")
        raise InvalidMappingError("Logical Source or Logical Table is not defined in the mapping")
    source = sources[0]

    if mapping_format == R2RML_URI:
        yarrrml_source = get_logical_table(source, rdf_mapping)
    elif mapping_format == RML_URI:
        yarrrml_source = get_core_logical_source(source, rdf_mapping)
    else:
        yarrrml_source = get_logical_source(source, rdf_mapping)

    return yarrrml_source


def get_core_logical_source(logical_source_id, rdf_mapping):
    vocabulary = rdflib.Namespace(RML_URI)
    source = rdf_mapping.value(logical_source_id, vocabulary.source)
    formulation = rdf_mapping.value(logical_source_id, vocabulary.referenceFormulation)
    iterator = rdf_mapping.value(logical_source_id, vocabulary.iterator)
    if source is None or isinstance(source, rdflib.Literal):
        raise InvalidMappingError("RML-Core logical source requires a source resource")
    path = rdf_mapping.value(source, vocabulary.path)
    if path is not None:
        if formulation and not str(formulation).startswith(RML_URI):
            raise InvalidMappingError("Unsupported RML-Core reference formulation")
        if any(rdf_mapping.value(source, predicate) is not None for predicate in (
            vocabulary.root, vocabulary.encoding, vocabulary.null, vocabulary.compression
        )):
            raise InvalidMappingError("Source path options cannot be represented in YARRRML")
        formulation_name = str(formulation).removeprefix(RML_URI).lower() if formulation else "csv"
        result = [str(path) + "~" + formulation_name]
        if iterator is not None:
            result.append(str(iterator))
        return result
    d2rq = rdflib.Namespace(D2RQ_URI)
    dsn = rdf_mapping.value(source, d2rq.jdbcDSN)
    if dsn is None:
        sd = rdflib.Namespace(SD_URI)
        kg4di = rdflib.Namespace(KG4DI_URI)
        name = rdf_mapping.value(source, sd.name)
        if name is not None and (source, rdflib.RDF.type, sd.DatasetSpecification) in rdf_mapping:
            definer = rdf_mapping.value(formulation, kg4di.definedBy)
            if formulation is None or definer is None:
                raise InvalidMappingError("In-memory source requires a formulation and structure definer")
            result = {
                YARRRML_ACCESS: "$(" + str(name) + ")",
                YARRRML_REFERENCE_FORMULATION: str(formulation).rsplit("#", 1)[-1],
                YARRRML_STRUCTURE_DEFINER: str(definer),
            }
            if iterator is not None:
                result[YARRRML_ITERATOR] = str(iterator)
            transformation = rdf_mapping.value(source, sd.hasDataTransformation)
            if transformation is not None:
                specification = {}
                requirements = rdf_mapping.value(transformation, sd.hasSoftwareRequirements)
                code = rdf_mapping.value(transformation, sd.hasSourceCode)
                language = rdf_mapping.value(code, sd.programmingLanguage) if code is not None else None
                if requirements is not None:
                    specification[YARRRML_SOFTWARE_REQUIREMENTS] = str(requirements)
                if language is not None:
                    specification[YARRRML_PROGRAMMING_LANGUAGE] = str(language)
                result[YARRRML_SOFTWARE_SPECIFICATION] = specification
            return result
        raise InvalidMappingError("Unsupported RML-Core source access description")
    if formulation not in (vocabulary[RML_SQL_QUERY_FORMULATION], vocabulary[RML_SQL_TABLE_FORMULATION]) or iterator is None:
        raise InvalidMappingError("Database source requires a SQL formulation and iterator")
    result = {
        YARRRML_ACCESS: str(dsn),
        YARRRML_QUERY if formulation == vocabulary[RML_SQL_QUERY_FORMULATION] else YARRRML_TABLE: str(iterator),
    }
    username = rdf_mapping.value(source, d2rq.username)
    password = rdf_mapping.value(source, d2rq.password)
    if username is not None or password is not None:
        result[YARRRML_CREDENTIALS] = {}
        if username is not None:
            result[YARRRML_CREDENTIALS][YARRRML_USERNAME] = str(username)
        if password is not None:
            result[YARRRML_CREDENTIALS][YARRRML_PASSWORD] = str(password)
    driver = rdf_mapping.value(source, d2rq.jdbcDriver)
    if driver is not None:
        for name, driver_name in YARRRML_DATABASES_DRIVER.items():
            if str(driver) == driver_name:
                result[YARRRML_TYPE] = name
                break
        else:
            raise InvalidMappingError("Unsupported database driver cannot be represented in YARRRML")
    return result


def get_logical_table(logical_table_id, rdf_mapping):
    table_name = rdf_mapping.value(subject=logical_table_id, predicate=rdflib.Namespace(R2RML_URI).tableName)
    sql_query = rdf_mapping.value(subject=logical_table_id, predicate=rdflib.Namespace(R2RML_URI).sqlQuery)
    sql_version = rdf_mapping.value(subject=logical_table_id, predicate=rdflib.Namespace(R2RML_URI).sqlVersion)

    if table_name is None and sql_query is None:
        logger.error("Mapping does not define neither tableName nor sqlQuery")
        raise InvalidMappingError(
            "Mapping does not define neither tableName nor sqlQuery"
        )
    yarrrml_source = {}
    if table_name:
        yarrrml_source[YARRRML_TABLE] = table_name.value
    elif sql_query:
        yarrrml_source[YARRRML_QUERY] = sql_query.value

    if sql_version:
        yarrrml_source[YARRRML_QUERY_FORMULATION] = sql_version.toPython().replace(R2RML_URI, '').lower()

    return yarrrml_source


def get_logical_source(logical_source_id, rdf_mapping):
    yaml = YAML()
    source = rdf_mapping.value(subject=logical_source_id, predicate=rdflib.Namespace(RML_OLD_URI).source)
    iterator = rdf_mapping.value(subject=logical_source_id, predicate=rdflib.Namespace(RML_OLD_URI).iterator)
    reference_formulation = rdf_mapping.value(subject=logical_source_id,
                                              predicate=rdflib.Namespace(RML_OLD_URI).referenceFormulation)
    sql_query = rdf_mapping.value(subject=logical_source_id, predicate=rdflib.Namespace(R2RML_URI).sqlQuery)
    sql_version = rdf_mapping.value(subject=logical_source_id, predicate=rdflib.Namespace(R2RML_URI).sqlVersion)

    if source is None:
        logger.error("Mapping does not define source access")
        raise InvalidMappingError("Mapping does not define source access")

    if source and reference_formulation and iterator:
        yarrrml_source = [source.value + '~' + reference_formulation.toPython().replace(QL_URI, '').lower(), iterator.value]
    elif source and sql_query:
        # this means a database source
        source_dict = {YARRRML_QUERY: sql_query.value, YARRRML_SOURCE: source.value}
        if reference_formulation:
            source_dict[YARRRML_REFERENCE_FORMULATION] = reference_formulation.toPython().replace(QL_URI, '').lower()
        if sql_version:
            source_dict[YARRRML_QUERY_FORMULATION] = sql_version.toPython().replace(R2RML_URI, '').lower()
        yarrrml_source = source_dict
    elif source and reference_formulation:
        yarrrml_source = [source.value + '~' + reference_formulation.toPython().replace(QL_URI, '').lower()]
    else:
        if source.value.endswith(".csv"):
            yarrrml_source = [source.value + '~csv']
        else:
            yarrrml_source = [source.value]

    if type(yarrrml_source) is list:
        yarrrml_source = yaml.seq(yarrrml_source)
        yarrrml_source.fa.set_flow_style()

    return yarrrml_source
