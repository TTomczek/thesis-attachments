# ba-manual-mcp-server

## Generating APIs (Windows)
Die generierten APIs werden in den Ordner `src` gespeichert. Dadurch passen die Imports nicht. Diese müssen manuell korrigiert werden, indem ein `src.` vorangestellt wird.
Aus `from discord_client import example` wird dann `from src.discord_client import example`.
Das Invoice Model der API benötigt Before Validatoren um die Liste an Werten zu Dates konvertieren zu können.
```python
@field_validator('serviceFrom', mode='before')
@classmethod
def parse_service_from(cls, value):
    if isinstance(value, list) and len(value) == 3:
        return date(value[0], value[1], value[2])
    if isinstance(value, (date, datetime)):
        return value.date() if isinstance(value, datetime) else value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    return value

@field_validator('serviceTo', mode='before')
@classmethod
def parse_service_to(cls, value):
    if value is None:
        return None
    if isinstance(value, list) and len(value) == 3:
        return date(value[0], value[1], value[2])
    if isinstance(value, (date, datetime)):
        return value.date() if isinstance(value, datetime) else value
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    return value
```

### GitHub
```bash
    docker run --rm -v "${PWD}:/local" -e JAVA_OPTS="-DmaxYamlCodePoints=10000000" openapitools/openapi-generator-cli generate -g python --additional-properties=library=httpx,packageName=github_client,generateSourceCodeOnly=true --global-property=apiTests=false,modelTests=false,apiDocs=false,modelDocs=false -i https://raw.githubusercontent.com/TTomczek/apis/refs/heads/main/github/api.github.com.yaml -o /local/src
```

### Discord
```bash
    docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate -g python --additional-properties=library=httpx,packageName=discord_client,generateSourceCodeOnly=true --global-property=apiTests=false,modelTests=false,apiDocs=false,modelDocs=false -i https://raw.githubusercontent.com/TTomczek/apis/refs/heads/main/discord/openapi-modified.json -o /local/src
```

### EVE
```bash
    docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate -g python --additional-properties=library=httpx,packageName=eve_client,generateSourceCodeOnly=true --global-property=apiTests=false,modelTests=false,apiDocs=false,modelDocs=false -i https://raw.githubusercontent.com/TTomczek/apis/refs/heads/main/eve/openapi-3.0.yaml -o /local/src
```

### Invoice Manager
```bash
    docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate -g python --additional-properties=library=httpx,packageName=invman_client,generateSourceCodeOnly=true --global-property=apiTests=false,modelTests=false,apiDocs=false,modelDocs=false -i https://raw.githubusercontent.com/TTomczek/apis/refs/heads/main/invoice-manager/openapi.yaml -o /local/src
```

### Remove support files
```bash
    Remove-Item src/* -Include *_README.md
    Remove-Item src/.openapi-generator-ignore
    Remove-Item src/.openapi-generator -Recurse -Force
```

