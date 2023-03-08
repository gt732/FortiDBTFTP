from py3tftpsql.database import connect_database

if __name__ == "__main__":
    with connect_database() as db:
        result = db.query(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'backups')"
        )
        if not result[0][0]:
            db.execute(
                """
                    CREATE TABLE backups (
                        id PRIMARY KEY,
                        hostname TEXT,
                        config TEXT,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
                """
            )
