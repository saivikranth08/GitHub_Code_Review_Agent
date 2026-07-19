def get_user(db, user_id):
    # Security Agent should catch this SQL Injection
    query = "SELECT * FROM users WHERE id = " + user_id
    db.execute(query)

    # Performance Agent should catch this O(N^2) loop
    items = [1, 2, 3, 4, 5]
    for i in items:
        for j in items:
            print(i + j) :::
