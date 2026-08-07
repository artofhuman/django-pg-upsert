0.6.1
-----
Add the readme to the package metadata, so the PyPI page shows the documentation

Add the license, project links, keywords, and classifiers to the package metadata

0.6.0
-----
Support where condition for update on conflict

Support django 4.2, 5.2, 6.0, 6.1

0.5.0
-----
Unlock python upper bound

0.4.0
-----
Allow to use with django 4.0

0.3.1
-----
Relax django version to allow using package with django 2.x

0.3.0
-----
Allows for bulk upserting, e.g.

```sql
INSERT INTO table_name (col1, col2)
VALUES
    ('name1', 12),
    ('name2', 13)
ON CONFLICT conflict (col1) DO UPDATE
SET col2 = EXCLUDED.col2;
```
