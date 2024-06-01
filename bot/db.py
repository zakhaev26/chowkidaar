import psycopg2
from config import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST
from parse_message import extract_user_info

def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST
        )
        print("Connection to the database was successful")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
    
def save_log(conn, message, discord_user_id, discord_message_id, sent_at, in_text_valid=-1):
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO participation_logs (
                message, discord_user_id, discord_message_id, sent_at, in_text_valid
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (message, discord_user_id, discord_message_id, sent_at, in_text_valid)
        )
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error occurred while saving log: {e}")
        conn.rollback()  # Rollback the transaction if there is any error
    finally:
        cur.close()

def update_log(conn, discord_message_id, message, in_text_valid, updated_at):
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE participation_logs
            SET message = %s, in_text_valid = %s, updated_at = %s
            WHERE discord_message_id = %s
        """, (message, in_text_valid, updated_at, discord_message_id))
        conn.commit()
        print(f"Log updated for message ID: {discord_message_id}")
    except Exception as e:
        print(f"Error updating log: {e}")
        conn.rollback()
    finally:
        cur.close()

def check_intext_validity(conn, message):
    try: 
        college_id = extract_user_info(message)
        if college_id:
            cur= conn.cursor()
            cur.execute("SELECT name FROM student_list_2023 WHERE student_id = %s", (college_id.upper(),))
            full_name = cur.fetchone()
            if full_name:
                first_name = full_name[0].split()[0]  # Assuming name is the first element of the tuple
                if first_name.lower() in message.lower():
                    return 1
                elif full_name[0].lower() in message.lower():
                    return 1
            else:
                print(f"No name found for student_id: {college_id}")
        return 0  
        cur.close() 

    except Exception as e:
        print(f"Error while checking intext validity: {e}")
        return -1


if __name__ == "__main__":
    conn= connect_to_database()
    print(check_intext_validity(conn, "Abhigyan Dutta B123003 aetwgwrgwsgrgwsrgswgs"))
    conn.close()
