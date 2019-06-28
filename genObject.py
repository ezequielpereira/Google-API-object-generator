#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json


def _printParents(parents):
    result = parents[0]

    for parent in parents[1:]:
        result += "->%s" % parent

    return result


def _genProperty(discoveryDoc, prop, parents):
    if '$ref' in prop:
        return _genObject(discoveryDoc, prop['$ref'], parents)
    elif 'type' in prop:
        if prop['type'] == "any":
            return {'@type': "type.googleapis.com/google.protobuf.Empty"}
        elif prop['type'] == "array":
            return [_genProperty(discoveryDoc, prop['items'], parents)]
        elif prop['type'] == "boolean":
            return True
        elif prop['type'] == "integer":
            if prop['format'] == "int32":
                return -0x80000000
            elif prop['format'] == "uint32":
                return 0xFFFFFFFF
        elif prop['type'] == "number":
            if prop['format'] == "double":
                return -0.1
            elif prop['format'] == "float":
                return 0.1
        elif prop['type'] == "object":
            return _genObject(discoveryDoc, prop, parents)
        elif prop['type'] == "string":
            if 'format' not in prop:
                return "RANDOM_STRING"
            elif prop['format'] == "byte":
                return "UkFORE9NX1RFWFQ="
            elif prop['format'] == "date":
                return "2030-12-31"
            elif prop['format'] == "date-time":
                return "2031-11-30T23:00:30.123Z"
            elif prop['format'] == "int64":
                return "-9223372036854775808"
            elif prop['format'] == "byte":
                return "9223372036854775808"


def _genObject(discoveryDoc, objName, parents):
    result = {}

    if objName in parents:
        sys.stderr.write(
          "\033[31;1mWARNING:\n"
          f'\033[0m  {objName} object found within itself, empty object '
          "returned as child to avoid recursion\n"
          f'\033[33;1m  Parents: {_printParents(parents)}\033[0m\n'
        )
        return result

    if type(objName) == dict:
        obj = objName
        newParents = parents
    else:
        obj = discoveryDoc['schemas'][objName]
        newParents = parents + [objName]

    if 'properties' in obj:
        propDict = obj['properties']
        for propName in propDict:
            result[propName] = _genProperty(
                discoveryDoc, propDict[propName], newParents)

    if 'additionalProperties' in obj:
        result['RANDOM_PROPERTY_NAME'] = _genProperty(
            discoveryDoc, obj['additionalProperties'], newParents)

    return result


def genObject(discoveryDoc, objName):
    return _genObject(discoveryDoc, objName, [])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ./genObject.py <discovery document> <object name>")
        exit(1)

    discoveryDocPath = sys.argv[1]
    objName = sys.argv[2]

    with open(discoveryDocPath) as discoveryDocFile:
        discoveryDoc = json.load(discoveryDocFile)

    result = genObject(discoveryDoc, objName)
    print(json.dumps(result, indent=2, sort_keys=True))
