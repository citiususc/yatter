from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap as ordereddict, CommentedSeq

def normalize_yaml(data):
    key_mapping = {
        'mappings': ['mapping', 'm'],
        'subjects': ['subject', 's'],
        'predicates': ['predicate', 'p'],
        'inversepredicates': ['inversepredicate', 'i'],
        'objects': ['object', 'o'],
        'predicateobjects': ['po'],
        'function': ['fn', 'f'],
        'parameters': ['pms'],
        'parameter': ['pm'],
        'value': ['v'],
        'authors': ['author', 'a']
    }

    def get_normalized_key(key):
        for normalized_key, variants in key_mapping.items():
            if key == normalized_key or key in variants:
                return normalized_key
        return key

    def expand_authors(authors):
        expanded_authors = CommentedSeq()
        for author in authors:
            if isinstance(author, str):
                expanded_author = ordereddict()
                parts = author.split()
                name_parts = []
                email = None
                website = None
                for part in parts:
                    if part.startswith("http://") or part.startswith("https://"):
                        if part.startswith("(") and part.endswith(")"):
                            website = part.strip("()")
                        else:
                            expanded_authors.append(part)  # WebID, se añade directamente
                            break
                    # Identificar email
                    elif part.startswith("<") and part.endswith(">"):
                        email = part.strip("<>")
                    else:
                        name_parts.append(part)

                # Si hay partes del nombre, email o sitio web, las agregamos al autor expandido
                if name_parts:
                    expanded_author['name'] = " ".join(name_parts)
                if email:
                    expanded_author['email'] = email
                if website:
                    expanded_author['website'] = website

                if expanded_author:
                    expanded_authors.append(expanded_author)
            else:
                expanded_authors.append(author)
        return expanded_authors

    def expand_sources(sources):
        expanded_sources = CommentedSeq()
        for source in sources:
            if isinstance(source, list):
                expanded_source = ordereddict()
                access, reference = source[0].split('~')
                expanded_source['access'] = access
                expanded_source['referenceFormulation'] = reference
                if len(source) > 1:
                    expanded_source['iterator'] = source[1]
                expanded_sources.append(expanded_source)
            else:
                expanded_sources.append(source)
        return expanded_sources

    def expand_predicateobjects(predicateobjects):
        expanded_predicateobjects = CommentedSeq()
        for po in predicateobjects:
            if isinstance(po, list):
                expanded_po = ordereddict()
                expanded_po['predicates'] = po[0]
                if len(po) == 2:
                    expanded_po['objects'] = po[1]
                elif len(po) == 3:
                    expanded_po['objects'] = ordereddict()
                    expanded_po['objects']['value'] = po[1]
                    expanded_po['objects']['datatype'] = po[2]
                expanded_predicateobjects.append(expanded_po)
            elif isinstance(po, dict):
                expanded_po = ordereddict()
                for key, value in po.items():
                    if key == 'p':
                        expanded_po['predicates'] = value
                    elif key == 'o':
                        expanded_po['objects'] = normalize_yaml(value)
                    else:
                        expanded_po[key] = normalize_yaml(value)
                expanded_predicateobjects.append(expanded_po)
            else:
                expanded_predicateobjects.append(po)
        return expanded_predicateobjects

    def expand_parameters(parameters):
        expanded_parameters = CommentedSeq()
        for param in parameters:
            if isinstance(param, list) and len(param) == 2:
                expanded_param = ordereddict()
                expanded_param['parameter'] = param[0]
                expanded_param['value'] = param[1]
                expanded_parameters.append(expanded_param)
            else:
                expanded_parameters.append(param)
        return expanded_parameters

    if isinstance(data, dict):
        new_data = ordereddict()
        for key, value in data.items():
            new_key = get_normalized_key(key)
            if new_key == 'authors' and isinstance(value, list):
                new_data[new_key] = expand_authors(value)

            elif new_key == 'sources' and isinstance(value, list):
                new_data[new_key] = expand_sources(value)
            elif new_key == 'predicateobjects' and isinstance(value, list):
                new_data[new_key] = expand_predicateobjects(value)
            elif new_key == 'parameters' and isinstance(value, list):
                new_data[new_key] = expand_parameters(value)
            else:
                new_data[new_key] = normalize_yaml(value)
        return new_data
    elif isinstance(data, list):
        new_list = CommentedSeq()
        for item in data:
            new_list.append(normalize_yaml(item))
        return new_list
    else:
        return data


if __name__ == "__main__":
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    # Cargar el YAML
    with open("mapping.yml", "r") as file:
        data = yaml.load(file)

    # Normalizar el YAML
    normalized_data = normalize_yaml(data)

    # Guardar el YAML normalizado
    with open("mapping_normalized.yml", "w") as file:
        yaml.dump(normalized_data, file)

    print("YAML normalizado guardado en mapping_normalized.yml")
