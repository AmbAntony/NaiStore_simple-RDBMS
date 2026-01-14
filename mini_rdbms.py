class Column:
    def __init__(self, name, dtype, primary=False, unique=False):
        self.name = name
        self.dtype = dtype  # 'integer', 'string', 'float'
        self.primary = primary
        self.unique = unique


class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.rows = []
        self.primary_key = next((c.name for c in columns if c.primary), None)
        self.unique_columns = [c.name for c in columns if c.unique or c.primary]
        self.indexes = {}

    def _validate_row(self, row, exclude_row=None):
    
        for col in self.columns:
            if col.name in row:
                val = row[col.name]
                if col.dtype == 'integer' and not isinstance(val, int):
                    raise ValueError(f"Column {col.name} must be integer")
                if col.dtype == 'float' and not isinstance(val, (int, float)):
                    raise ValueError(f"Column {col.name} must be float")
                if col.dtype == 'string' and not isinstance(val, str):
                    raise ValueError(f"Column {col.name} must be string")


        for r in self.rows:
            if r is exclude_row:
                continue
            for col_name in self.unique_columns:
                if col_name in row and r.get(col_name) == row[col_name]:
                    raise ValueError(f"Duplicate value for unique column: {col_name}")

    def create_index(self, column_name):
        if column_name not in [c.name for c in self.columns]:
            raise ValueError(f"Column {column_name} does not exist")
        index = {}
        for i, row in enumerate(self.rows):
            val = row.get(column_name)
            if val not in index:
                index[val] = []
            index[val].append(i)
        self.indexes[column_name] = index

    def insert(self, row):
        self._validate_row(row)
        self.rows.append(row)
 
        for col_name, index in self.indexes.items():
            val = row.get(col_name)
            if val not in index:
                index[val] = []
            index[val].append(len(self.rows) - 1)

    def select(self, where=None):
        if not where:
            return self.rows
        
     
        indexed_col = next((k for k in where.keys() if k in self.indexes), None)
        if indexed_col:
            val = where[indexed_col]
            row_indices = self.indexes[indexed_col].get(val, [])
            results = [self.rows[i] for i in row_indices]
    
            remaining_where = {k: v for k, v in where.items() if k != indexed_col}
            if not remaining_where:
                return results
            return [r for r in results if all(r.get(k) == v for k, v in remaining_where.items())]

        return [
            r for r in self.rows
            if all(r.get(k) == v for k, v in where.items())
        ]

    def update(self, updates, where):
        targets = self.select(where)
        for row in targets:
            new_row = {**row, **updates}
            self._validate_row(new_row, exclude_row=row)
        
      
        for row in targets:
            row.update(updates)
        
        for col_name in updates:
            if col_name in self.indexes:
                self.create_index(col_name)

    def delete(self, where):
        targets = self.select(where)
        self.rows = [r for r in self.rows if r not in targets]
        for col_name in self.indexes:
            self.create_index(col_name)

    def join(self, other_table, on_self, on_other):
        results = []
        for r1 in self.rows:
            for r2 in other_table.rows:
                if r1.get(on_self) == r2.get(on_other):
                    combined = {f"{self.name}_{k}": v for k, v in r1.items()}
                    combined.update({f"{other_table.name}_{k}": v for k, v in r2.items()})
                    results.append(combined)
        return results


class Database:
    def __init__(self):
        self.tables = {}

    def create_table(self, name, columns):
        self.tables[name] = Table(name, columns)
