import sqlite3
import getpass


# Path to your SQLite databasea
user = getpass.getuser()
db_path = "/home/%s/printer_data/database/moonraker-sql.db" % user

def delete_unauthorized_users(db_path):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # SQL query to delete rows where username is not '_API_KEY_USER_'
        sql_query = """
            DELETE FROM authorized_users WHERE username != '_API_KEY_USER_';
        """
        
        # Execute the query
        cursor.execute(sql_query)
        
        # Commit the changes
        conn.commit()
        
        print(f"Deleted {cursor.rowcount} unauthorized users.")
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
   
    finally:
        # Close the connection
        if conn:
            conn.close()


if __name__ == "__main__":
    print(db_path)
    delete_unauthorized_users(db_path)
