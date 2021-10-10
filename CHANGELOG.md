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
