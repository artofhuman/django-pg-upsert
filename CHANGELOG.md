0.5.0
-----
Ulock python upper bound

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
