import shlex
from mini_rdbms import Database, Column

class RDBMSRepl:
    def __init__(self):
        self.db = Database()
        self.prompt = "mini_db> "

    def start(self):
        print("--- Mini RDBMS Interactive REPL ---")
        print("Commands: CREATE, INSERT, SELECT, UPDATE, DELETE, JOIN, TABLES, DESC, EXIT")
        print("Type 'HELP' for syntax examples.\n")
        
        while True:
            try:
                line = input(self.prompt)
                if not line.strip():
                    continue
                
                parts = shlex.split(line)
                command = parts[0].upper()
                
                if command == "EXIT":
                    break
                elif command == "HELP":
                    self.show_help()
                elif command == "CREATE":
                    self.handle_create(parts[1:])
                elif command == "INSERT":
                    self.handle_insert(parts[1:])
                elif command == "SELECT":
                    self.handle_select(parts[1:])
                elif command == "UPDATE":
                    self.handle_update(parts[1:])
                elif command == "DELETE":
                    self.handle_delete(parts[1:])
                elif command == "JOIN":
                    self.handle_join(parts[1:])
                elif command == "TABLES":
                    self.handle_tables()
                elif command == "DESC":
                    self.handle_desc(parts[1:])
                else:
                    print(f"Unknown command: {command}")
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")

    def show_help(self):
        print("\nSyntax Examples:")
        print("  CREATE products id:integer:p name:string price:float")
        print("  INSERT products id=1 name=Laptop price=899.99")
        print("  SELECT products id=1")
        print("  UPDATE products price=799.99 WHERE id=1")
        print("  DELETE products id=1")
        print("  JOIN products orders id=product_id")
        print("  TABLES")
        print("  DESC products")
        print("  EXIT\n")

    def _parse_val(self, val, dtype):
        if dtype == "integer": return int(val)
        if dtype == "float": return float(val)
        return val

    def handle_create(self, args):
        name = args[0]
        cols = []
        for col_def in args[1:]:
            parts = col_def.split(":")
            col_name = parts[0]
            dtype = parts[1]
            primary = "p" in parts[2:].lower() if len(parts) > 2 else False
            unique = "u" in parts[2:].lower() if len(parts) > 2 else False
            cols.append(Column(col_name, dtype, primary, unique))
        self.db.create_table(name, cols)
        print(f"Table '{name}' created.")

    def handle_insert(self, args):
        table_name = args[0]
        table = self.db.tables.get(table_name)
        if not table: raise ValueError(f"Table {table_name} not found")
        
        row = {}
        for pair in args[1:]:
            k, v = pair.split("=")
            # Find column type
            col = next((c for c in table.columns if c.name == k), None)
            if not col: raise ValueError(f"Column {k} not found")
            row[k] = self._parse_val(v, col.dtype)
        
        table.insert(row)
        print("Row inserted.")

    def handle_select(self, args):
        table_name = args[0]
        table = self.db.tables.get(table_name)
        if not table: raise ValueError(f"Table {table_name} not found")
        
        where = {}
        for pair in args[1:]:
            k, v = pair.split("=")
            col = next((c for c in table.columns if c.name == k), None)
            val = self._parse_val(v, col.dtype) if col else v
            where[k] = val
            
        results = table.select(where if where else None)
        self.print_table(results)

    def handle_update(self, args):
        table_name = args[0]
        table = self.db.tables.get(table_name)
        if not table: raise ValueError(f"Table {table_name} not found")
        
        # Syntax: UPDATE table col=val WHERE col=val
        try:
            where_idx = [i for i, x in enumerate(args) if x.upper() == "WHERE"][0]
            update_args = args[1:where_idx]
            where_args = args[where_idx+1:]
        except IndexError:
            update_args = args[1:]
            where_args = []

        updates = {}
        for pair in update_args:
            k, v = pair.split("=")
            col = next((c for c in table.columns if c.name == k), None)
            updates[k] = self._parse_val(v, col.dtype) if col else v

        where = {}
        for pair in where_args:
            k, v = pair.split("=")
            col = next((c for c in table.columns if c.name == k), None)
            where[k] = self._parse_val(v, col.dtype) if col else v

        table.update(updates, where)
        print("Update complete.")

    def handle_delete(self, args):
        table_name = args[0]
        table = self.db.tables.get(table_name)
        if not table: raise ValueError(f"Table {table_name} not found")
        
        where = {}
        for pair in args[1:]:
            k, v = pair.split("=")
            col = next((c for c in table.columns if c.name == k), None)
            where[k] = self._parse_val(v, col.dtype) if col else v
        
        table.delete(where)
        print("Delete complete.")

    def handle_join(self, args):
        # Syntax: JOIN table1 table2 on1=on2
        t1_name, t2_name, on_pair = args[0], args[1], args[2]
        t1 = self.db.tables.get(t1_name)
        t2 = self.db.tables.get(t2_name)
        on_self, on_other = on_pair.split("=")
        
        results = t1.join(t2, on_self, on_other)
        self.print_table(results)

    def handle_tables(self):
        print("Tables:", ", ".join(self.db.tables.keys()) if self.db.tables else "None")

    def handle_desc(self, args):
        name = args[0]
        table = self.db.tables.get(name)
        if not table: raise ValueError(f"Table {name} not found")
        print(f"Table: {name}")
        for c in table.columns:
            flags = []
            if c.primary: flags.append("PRIMARY")
            if c.unique: flags.append("UNIQUE")
            print(f"  {c.name}: {c.dtype} {' '.join(flags)}")

    def print_table(self, rows):
        if not rows:
            print("No records found.")
            return
        
        keys = list(rows[0].keys())
        # Header
        header = " | ".join(f"{k:15}" for k in keys)
        print("-" * len(header))
        print(header)
        print("-" * len(header))
        # Body
        for row in rows:
            print(" | ".join(f"{str(row.get(k, '')):15}" for k in keys))
        print("-" * len(header))

if __name__ == "__main__":
    RDBMSRepl().start()
