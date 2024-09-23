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
    properties: dict[str, dict]

def parse(stdin: Iterator[str]) -> Iterator[JsonschemaType]:
    current_obj: RawType | None = None

    for line in stdin:
        if not line.strip():
            continue
        elif line.startswith("##"):
            if current_obj:
                yield {
                    "title": current_obj['title'],
                    # hide noisy descriptions, code samples don't look good in
                    # vscode/monaco
                    "description": current_obj['description'] if not current_obj['description'].startswith("```") else "",
                    "properties": {
                        x['name']: x
                        for x in current_obj['raw_properties']
                    }
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
                **parse_type(ty),
            })
        elif current_obj:
            if current_obj['raw_properties']:
                current_obj['raw_properties'][-1]['description'] += line
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

    if input.startswith("[") and input.endswith(")"):
        name = input.split("]")[0].strip("[]")
        return {
            "$ref": f"#/definitions/{name}"
        }

    if input in ("true", "false", "true | false", "bool"):
        return {"type": "bool"}

    if " | " in input:
        return {"anyOf": [parse_type(x) for x in input.split(" | ")]}

    if input.endswith("Object"):
        return {
            "$ref": f"#/definitions/{input}"
        }

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

    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$ref": "#/definitions/Basic Configuration Modules",
        "definitions": definitions
    }

    print(json.dumps(schema, indent=2))

if __name__ == "__main__":
    main()
