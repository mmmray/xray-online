import os
import json
import sys

from typing import Iterator, Sequence, TypedDict

class RawType(TypedDict):
    title: str
    description: str
    raw_properties: list[dict]

class JsonschemaType(TypedDict):
    title: str
    description: str
    # enable markdown in monaco
    # https://github.com/microsoft/monaco-editor/issues/1816
    markdownDescription: str
    properties: dict[str, dict]
    additionalProperties: bool

KNOWN_BAD_RESOLVES = ("FakeDnsObject", "metricsObject", "TransportObject", "noiseObject", "DnsServerObject")
USED_OBJECTS = set()

def parse(stdin: Iterator[str]) -> Iterator[JsonschemaType]:
    current_obj: RawType | None = None

    for line in stdin:
        if line.startswith("##"):
            if current_obj:
                description = current_obj['description']

                yield {
                    "title": current_obj['title'],
                    "description": description,
                    "markdownDescription": description,
                    "properties": {
                        x['name']: x
                        for x in current_obj['raw_properties']
                    },
                    # turn off additionalProperties so that monaco will warn on
                    # unknown properties. xray does allow for unknown
                    # properties but most likely, setting them is a mistake. we
                    # only do this if we have any props ourselves, otherwise
                    # there is no point.
                    "additionalProperties": not current_obj["raw_properties"]
                }

            current_obj = {
                "title": line.split(" ", 1)[-1].strip(),
                "description": "",
                "raw_properties": []
            }
        elif line.startswith("> ") and ":" in line and current_obj:
            name, ty = line[2:].split(":", 1)
            if name == "Tony":
                continue

            name = name.strip(" `")

            current_obj['raw_properties'].append({
                "name": name,
                "description": "",
                "markdownDescription": "",
                **parse_type(ty),
            })
        elif current_obj:
            if current_obj['raw_properties']:
                current_obj['raw_properties'][-1]['description'] += line
                current_obj['raw_properties'][-1]['markdownDescription'] += line
            else:
                current_obj['description'] += line

def parse_type(input: str) -> dict:
    input = input \
            .replace('<Badge text="WIP" type="warning"/>', '') \
            .replace('<Badge text="BETA" type="warning"/>', '') \
            .strip()

    if not input:
        return {}

    if input.startswith("\\[") and input.endswith("\\]"):
        return {
            "type": "array",
            "items": parse_type(input[2:-2])
        }

    if input.startswith("[") and input.endswith("]"):
        return {
            "type": "array",
            "items": parse_type(input[1:-1])
        }

    if (input.startswith("[") and input.endswith(")")) or input.endswith("Object"):
        name = input.split("]")[0].strip("[]")
        if name in KNOWN_BAD_RESOLVES:
            # If there is a dangling reference, monaco editor will turn off
            # all inline validation markers, as the root object has a warning.
            # So we catch all dangling references here and replace them with
            # object.
            return {"type": "object"}
        else:
            USED_OBJECTS.add(name)
            return {
                "$ref": f"#/definitions/{name}"
            }

    if input in ("true", "false", "true | false", "bool"):
        return {"type": "boolean"}

    if " | " in input:
        return {"anyOf": [parse_type(x) for x in input.split(" | ")]}

    if input in ("address", "address_port", "CIDR"):
        return {"type": "string"}

    if input in ("string", "number"):
        return {"type": input}

    if input == "int":
        return {"type": "integer"}

    if input.startswith("map"):
        return {"type": "object"}

    if input.startswith('"') and input.endswith('"'):
        return {"const": input[1:-1]}

    if input.startswith("a list of"):
        return {}

    if input == "string array":
        return {"type": "array", "items": {"type": "string"}}

    if input.startswith("string, any of"):
        return {"type": "string"}

    raise Exception(input)

def main():
    definitions = {}
    for definition in parse(sys.stdin):
        key = definition['title']
        if key in definitions:
            # Handle multiple instances of
            # InboundConfigurationObject/OutboundConfigurationObject
            if "anyOf" not in definitions[key]:
                definitions[key] = {"anyOf": [definitions[key]]}
            definitions[key]['anyOf'].append(definition)
        else:
            definitions[key] = definition

    for name in USED_OBJECTS:
        assert name in definitions, f"Cannot resolve {name}, add to KNOWN_BAD_RESOLVES?"

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$ref": "#/definitions/Basic Configuration Modules",
        "definitions": definitions
    }

    print(json.dumps(schema, indent=2))

if __name__ == "__main__":
    main()
