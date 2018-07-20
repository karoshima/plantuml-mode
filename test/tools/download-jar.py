#!/usr/bin/env python3
#
# -----
# Downloads the latest version of the PlantUML jar.
# -----
#
# In order to determine which version number is used by the latest PlantUML release,
# the Maven Central repository metadata is inspected. Since PlantUML has used different
# version numbering schemes along with the time, this script only looks into versions
# that follow the following convention:
#     <major>.<year>.<minor>
#
# -----

import urllib.request
import os

from re import match
from xml.dom.minidom import parseString
from functools import reduce

def download_metadata():
    url = "https://repo.maven.apache.org/maven2/net/sourceforge/plantuml/plantuml/maven-metadata.xml"
    response = urllib.request.urlopen(url)
    data_bin = response.read()
    xml = data_bin.decode('utf-8')
    return xml

def parse_metadata(xml_str):
    return parseString(xml_str)

def parse_version(version):
    regex = r'(?P<major>\d+)\.(?P<year>\d+)\.(?P<minor>\d+)'
    matched = match(regex, version).groupdict()
    return {k: int(v) for k, v in matched.items()}

def extract_versions(metadata_xml):
    def node_text(node):
        return node.firstChild.data
    versionNodes = metadata_xml.getElementsByTagName('version')
    versions = [parse_version(version) for version in map(node_text, versionNodes) if match(r'\d+\.\d+\.\d+', version)]
    return versions

def bigger_version(versionA, versionB):
    if versionA['major'] < versionB['major']:
        return versionB
    elif versionA['major'] > versionB['major']:
        return versionA
    # same major, one level down
    elif versionA['year'] < versionB['year']:
        return versionB
    elif versionA['year'] > versionB['year']:
        return versionA
    # same major, same year, one level down
    elif versionA['minor'] < versionB['minor']:
        return versionB
    elif versionA['minor'] > versionB['minor']:
        return versionA
    # same everything
    return versionA

def max_version(versions):
    return reduce(bigger_version, versions)

def download_link(version):
    version_str = str.format("{}.{}.{}", version['major'], version['year'], version['minor'])
    return str.format("https://repo.maven.apache.org/maven2/net/sourceforge/plantuml/plantuml/{}/plantuml-{}.jar", version_str, version_str)

def main():
    target_file = "./bin/plantuml.jar"

    # Build up the correct URL
    metadata_xml = parse_metadata(download_metadata())
    version = max_version(extract_versions(metadata_xml))
    link = download_link(version)

    # Create the target folder and actually download the file
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    urllib.request.urlretrieve(link, target_file)

if __name__ == "__main__":
    main()
