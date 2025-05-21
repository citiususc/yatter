# YATTER
<p align="center">
  <img title="logo" alt="YATTER" src="https://raw.githubusercontent.com/citiususc/yatter/main/logo/logo.png"  width="300" height="300"/>
</p>


![GitHub](https://img.shields.io/github/license/citiususc/yatter?style=flat)
[![Test](https://github.com/citiususc/yatter/actions/workflows/testgha.yml/badge.svg)](https://github.com/citiususc/yatter/actions/workflows/testgha.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7024501.svg)](https://doi.org/10.5281/zenodo.7024501)
[![PyPI](https://img.shields.io/pypi/v/yatter?style=flat)](https://pypi.org/project/yatter)
![GitHub Release Date](https://img.shields.io/github/release-date/citiususc/yatter)
[![codecov](https://codecov.io/gh/citiususc/yatter/branch/main/graph/badge.svg?token=QUWCG214SG)](https://codecov.io/gh/citiususc/yatter)

The tool translates mapping rules from YARRRML in a turtle-based serialization of RML or R2RML.

## Installation:
```
pip install yatter
```

## Execution from CLI
To execute from command line run the following:

- From YARRRML to \[R2\]RML
```bash
python3 -m yatter -i path_to_input_yarrrml.yml -o path_to_rdf_mapping.ttl [-f R2RML]
```

- From \[R2\]RML to YARRRML 
```bash
python3 -m yatter -i path_to_input_rdf_mapping.ttl -o path_to_output_yarrrml.yml [-f R2RML]
```

`-f R2RML` is an optional parameter for translating input YARRRML to R2RML (and inverse)

## Execution as a library

If you want to include the module in your implementation:
- for translating **YARRRML mapping** to **RML mappings** (and inverse):
```python
import yatter
from ruamel.yaml import YAML
# YARRRML to RML
yaml = YAML(typ='safe', pure=True)
rml_content = yatter.translate(yaml.load(open("path-to-yarrrml")))
# RML to YARRRML
yarrrml_content = yatter.inverse_translate("rdf_mapping_content")
```
- for translating **YARRRML mappings** to **R2RML mappings** (and inverse):
```python
import yatter
from ruamel.yaml import YAML

R2RML_URI = 'http://www.w3.org/ns/r2rml#'
# YARRRML to R2RML
yaml = YAML(typ='safe', pure=True)
rml_content = yatter.translate(yaml.load(open("path-to-yarrrml")), mapping_format=R2RML_URI)
# R2RML to YARRRML
yarrrml_content = yatter.inverse_translate("rdf_mapping_content", mapping_format=R2RML_URI)
```
- for merging TriplesMap based on id:
```python
import yatter
list_yarrrml_mappings = ["content_mapping_yarrrml1", "content_mapping_yarrrml1"]
yarrrml_content = yatter.merge_mappings(list_yarrrml_mappings)
```

## Specifications conformant:

These are the following specifications used by the translation process:
- YARRRML: https://w3id.org/kg-construct/yarrrml
- R2RML: https://www.w3.org/TR/r2rml/ 
- RML: https://rml.io/spec 
- RML-star: https://w3id.org/rml/star/spec
- RML-IO: https://w3id.org/rml/io/spec
- RML-FNML: https://w3id.org/rml/fnml/spec
- RML-CC: https://w3id.org/rml/cc/spec

To be implemented soon:
- RML-core: https://w3id.org/rml/core/spec 


## Cite this work:
If you used Yatter in your work, please cite the [ICWE2023](https://icwe2023.webengineering.org/program/) [paper](http://davidchavesfraga.com/outcomes/papers/2023/iglesias2023yatter.pdf):

```bib
@inproceedings{iglesias2023human,
  title={Human-Friendly RDF Graph Construction: Which One Do You Chose?},
  author={Iglesias-Molina, Ana and Chaves-Fraga, David and Dasoulas, Ioannis and Dimou, Anastasia},
  booktitle={International Conference on Web Engineering},
  pages={262--277},
  year={2023},
  doi={10.1007/978-3-031-34444-2_19},
  organization={Springer}
}
```

## Authors
CiTIUS - Universidade de Santiago de Compostela (2023-now):
- [David Chaves-Fraga](mailto:david.chaves@usc.es)
- Rubén Buján Vide (Final bachelor thesis - Mapping normalization, RML-cc and library management)

Ontology Engineering Group - Universidad Politécnica de Madrid (2021-2023):
- David Chaves-Fraga
- Marino González García (Final bachelor thesis - Systematic Testing)
- Luis López Piñero (Final bachelor thesis - v0.1)



