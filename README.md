# Cloud Office - Office Module

This repository currently contains a standalone Office module implementation.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Run demo service

```bash
python -m office_module.server --host 127.0.0.1 --port 8080
```

- Demo page: `http://127.0.0.1:8080/`
- Gather API: `http://127.0.0.1:8080/api/scene/gathered`

## Documentation

- System usage guide: `docs/system-usage.md`
