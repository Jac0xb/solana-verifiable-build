import requests

response = requests.get(
    "https://hub.docker.com/v2/namespaces/ellipsislabs/repositories/solana/tags?page_size=1000"
)

digest_map = {}
for result in response.json()["results"]:
    if result["name"] != "latest":
        try:
            major, minor, patch = list(map(int, result["name"].split(".")))
            digest_map[(major, minor, patch)] = result["digest"]
        except Exception as e:
            print(e)
            continue


entries = []
for k, v in sorted(digest_map.items()):
    entries.append(f'        m.insert({k}, "{v}");')

mappings = "\n".join(entries)

code = f"""
/// THIS FILE IS AUTOGENERATED. DO NOT MODIFY
use lazy_static::lazy_static;
use std::collections::BTreeMap;

lazy_static! {{
    pub static ref IMAGE_MAP: BTreeMap<(u32, u32, u32), &'static str> = {{
        let mut m = BTreeMap::new();
{mappings}
        m
    }};
}}
"""

print(code)

with open("src/image_config.rs", "w") as f:
    f.write(code.lstrip("\n"))