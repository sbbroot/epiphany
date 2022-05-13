from pathlib import Path
from typing import Any, Callable, Dict, List, Set

import yaml

from src.error import CriticalError


def load_yaml_file_all(filename: Path) -> List[Any]:
    try:
        with open(filename, encoding="utf-8") as req_handler:
            return list(yaml.safe_load_all(req_handler))
    except yaml.YAMLError as yaml_err:
        raise CriticalError(f'Failed loading: `{yaml_err}`') from yaml_err
    except Exception as err:
        raise CriticalError(f'Failed loading: `{filename}`') from err


def load_yaml_file(filename: Path) -> Any:
    return load_yaml_file_all(filename)[0]


class ManifestReader:
    """
    Load the manifest file and call defined parser methods to process required documents.
    Main running method is :func:`~manifest_reader.ManifestReader.parse_manifest` which returns formatted manifest output.
    """

    def __init__(self, dest_manifest: Path):
        self.__dest_manifest = dest_manifest
        self.__detected_components: Set = set()
        self.__detected_features: Set = set()

    def __parse_cluster_info(self, cluster_doc: Dict):
        """
        Parse `epiphany-cluster` document and extract only used components.

        :param cluster_doc: handler to a `epiphany-cluster` document
        """
        components = cluster_doc['specification']['components']
        for component in components:
            if components[component]['count'] > 0:
                self.__detected_components.add(component)

    def __parse_feature_mappings_info(self, feature_mappings_doc: Dict):
        """
        Parse `configuration/feature-mappings` document and extract only used features (based on `epiphany-cluster` doc).

        :param feature_mappings_doc: handler to a `configuration/feature-mappings` document
        """
        mappings = feature_mappings_doc['specification']['mappings']
        for mapping in mappings.keys() & self.__detected_components:
            for feature in mappings[mapping]:
                self.__detected_features.add(feature)

    def parse_manifest(self) -> Dict[str, Any]:
        """
        Load the manifest file, call parsers on required docs and return formatted output.
        """
        parse_doc: Dict[str, Callable] = {
            'epiphany-cluster':               self.__parse_cluster_info,
            'configuration/feature-mappings': self.__parse_feature_mappings_info
        }

        parsed_docs: Set[str] = set()
        for manifest_doc in load_yaml_file_all(self.__dest_manifest):
            try:
                kind: str = manifest_doc['kind']
                parse_doc[kind](manifest_doc)
                parsed_docs.add(kind)
            except KeyError:
                pass

        if len(parsed_docs) != len(parse_doc.keys()):
            raise CriticalError(f'ManifestReader - could not find documents: {parsed_docs ^ parse_doc.keys()}')

        return {'detected-components': sorted(list(self.__detected_components)),
                'detected-features': sorted(list(self.__detected_features))}