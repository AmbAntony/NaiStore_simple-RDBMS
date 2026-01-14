class Column:
    def __init__(self, name, dtype, primary=False, unique=False):
        self.name = name
        self.dtype = dtype
        self.primary = primary
        self.unique = unique


class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.rows = []
        self.primary_key = next((c.name for c in columns if c.primary), None)

    def insert(self, row):
        if self.primary_key:
            for r in self.rows:
                if r[self.primary_key] == row[self.primary_key]:
                    raise ValueError("Duplicate primary key")
        self.rows.append(row)

    def select(self, where=None):
        if not where:
            return self.rows
        return [
            r for r in self.rows
            if all(r[k] == v for k, v in where.items())
        ]

    def delete(self, where):
        self.rows = [
            r for r in self.rows
            if not all(r[k] == v for k, v in where.items())
        ]


class Database:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, columns):
        self.tables[name] = Table(name, columns)
