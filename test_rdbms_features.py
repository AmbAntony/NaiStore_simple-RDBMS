from mini_rdbms import Database, Column

def test_rdbms():
    db = Database()
    
 
    db.create_table("users", [
        Column("id", "integer", primary=True),
        Column("username", "string", unique=True),
        Column("email", "string", unique=True),
        Column("age", "integer")
    ])
    
    db.create_table("posts", [
        Column("id", "integer", primary=True),
        Column("user_id", "integer"),
        Column("content", "string")
    ])

    print("✅ Tables created with types and keys.")


    db.tables["users"].insert({"id": 1, "username": "alice", "email": "alice@example.com", "age": 30})
    db.tables["users"].insert({"id": 2, "username": "bob", "email": "bob@example.com", "age": 25})
    
    print("✅ Rows inserted.")


    try:
        db.tables["users"].insert({"id": 1, "username": "claire", "email": "c@ex.com", "age": 20})
        print("❌ Primary Key validation failed (accepted duplicate)")
    except ValueError as e:
        print(f"✅ Primary Key validation works: {e}")

    try:
        db.tables["users"].insert({"id": 3, "username": "alice", "email": "unique@ex.com", "age": 20})
        print("❌ Unique Key validation failed (accepted duplicate username)")
    except ValueError as e:
        print(f"✅ Unique Key validation works: {e}")


    alice = db.tables["users"].select({"username": "alice"})
    print(f"✅ Select works: found {len(alice)} alice(s)")


    db.tables["users"].create_index("username")
    alice_indexed = db.tables["users"].select({"username": "alice"})
    print(f"✅ Indexed Select works: {alice_indexed}")


    db.tables["users"].update({"age": 31}, {"username": "alice"})
    updated_alice = db.tables["users"].select({"username": "alice"})[0]
    if updated_alice["age"] == 31:
        print("✅ Update works.")
    else:
        print("❌ Update failed.")

 
    db.tables["users"].delete({"username": "bob"})
    bobs = db.tables["users"].select({"username": "bob"})
    if len(bobs) == 0:
        print("✅ Delete works.")
    else:
        print("❌ Delete failed.")


    db.tables["posts"].insert({"id": 101, "user_id": 1, "content": "Hello World"})
    db.tables["posts"].insert({"id": 102, "user_id": 1, "content": "My second post"})
    
    joined_results = db.tables["users"].join(db.tables["posts"], "id", "user_id")
    print(f"✅ Join works: found {len(joined_results)} joined records.")
    for row in joined_results:
        print(f"   - {row['users_username']} posted: {row['posts_content']}")

if __name__ == "__main__":
    test_rdbms()
