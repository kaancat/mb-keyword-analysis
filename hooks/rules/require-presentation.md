---
name: require-presentation-generation
enabled: true
event: stop
action: block
conditions:
  - field: transcript
    operator: not_contains
    pattern: generate_presentation.py|presentation.html created
---

**Phase 7 Not Complete!**

The presentation was not generated. Before completing the keyword analysis workflow, you must run:

```bash
python scripts/generate_presentation.py clients/<client_name>
```

This creates the interactive HTML presentation for the client.
