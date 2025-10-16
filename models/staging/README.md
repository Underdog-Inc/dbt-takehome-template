# Staging Conventions
- One model per raw source (seed), with basic type casting and light cleaning.
- Preserve original column names where sensible; document transformations.
- Avoid joins in staging—defer to marts.