from sqlalchemy import create_engine
import streamlit as st
import psycopg2
import pandas as pd

from sqlalchemy import create_engine, text

# Connect postgre sql
engine = None
try:
    engine= create_engine("postgresql://postgres:password@localhost:5032/login_crud")
    # st.success("Connected Successfully")
except Exception as e:
    st.error("Connection failed :", repr(e))

def create_user_table(engine):
    create_table_query = "CREATE TABLE IF NOT EXISTS Users (ID SERIAL PRIMARY KEY, User_Name VARCHAR(100), Password VARCHAR(50), Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP, Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"

    try:
        with engine.begin() as conn:
            conn.execute(text(create_table_query))
            # st.success("User created successfully")
    except Exception as e:
        st.error("Error while creating User :",repr(e))

create_user_table(engine)

# signup
def is_username_taken(engine, username):
    check_query = text("SELECT 1 FROM Users WHERE User_Name = :username")
    with engine.begin() as conn:
        result = conn.execute(check_query, {"username": username}).fetchone()
        return result is not None
    
def signup(engine, username, password):
    if is_username_taken(engine, username):
        st.warning("\nUsername already taken. Please choose a different one.")
        return
    
    insert_query = text("INSERT INTO Users (User_Name, Password) VALUES (:username, :password)")
    
    try:
        with engine.begin() as conn:
            conn.execute(insert_query, {"username": username, "password": password})
            st.success("\nUser registered successfully.")
    
    except Exception as e:
        st.error("Error inserting user:", repr(e))

# update password

def update_password(engine, username, old_password, new_password):
    update_query = text("""
        UPDATE Users
        SET Password = :new_password, Updated_At = CURRENT_TIMESTAMP
        WHERE User_Name = :username AND Password = :old_password
    """)
    
    try:
        with engine.begin() as conn:
            result = conn.execute(update_query, {
                "username": username,
                "old_password": old_password,
                "new_password": new_password
            })
            st.success("\nPassword updated successfully.")
    
    except Exception as e:
        st.error("Error updating password:", repr(e))

# delete user

def delete_user(engine, username, password):
    delete_query = text("DELETE FROM Users WHERE User_Name = :username AND Password = :password")
    
    try:
        with engine.begin() as conn:
            result = conn.execute(delete_query, {"username": username, "password": password})
            if result.rowcount:
                st.success("\nUser deleted successfully.")
            else:
                st.error("Invalid username or password.")
    
    except Exception as e:
        st.error("Error deleting user:", repr(e))

# sign in

def signIn(engine, username, password):
    check_query = text("SELECT * FROM Users WHERE User_Name = :username AND Password = :password")
    
    try:
        with engine.begin() as conn:
            result = conn.execute(check_query, {"username": username, "password": password}).fetchone()
            if result:
                st.success("\nLogin successful.")
                return True
            else:
                st.error("\nInvalid credentials.")
                return False
    
    except Exception as e:
        st.error("Error verifying user:", repr(e))
        return False

# verify password

def is_valid_password(password):
    if len(password) < 5:
        st.warning("Password must be at least 6 characters.")
        return False

    if not any(c.isalpha() for c in password):
        st.warning("Password must contain at least 1 letter.")
        return False

    if not any(c.isupper() for c in password):
        st.warning("Password must contain at least 1 uppercase letter.")
        return False

    if not any(c.isdigit() for c in password):
        st.warning("Password must contain at least 1 number.")
        return False
    
    if not any(c.isalnum() for c in password):
        st.warning("Password must contain atleast 1 symbol.")
        return False

    return True

# read db

def read(engine):
    all_users = text("SELECT * FROM Users ORDER BY ID ASC")

    try:
        with engine.begin() as conn:
            result = conn.execute(all_users)
            rows = result.fetchall()
            if rows:
                df = pd.DataFrame(rows, columns=result.keys())
                st.table(df)
            else:
                st.info("No users.")
    except Exception as e:
        st.error("Error fetching data: ", repr(e))


st.title("🔐 User Management System")

menu = st.selectbox("Menu", ["Sign Up", "Sign In", "Update Password", "Delete User", "View Records", "Exit"])

if menu == "Sign Up":
    st.subheader("Sign Up")
    username = st.text_input("Username", key="su_username")
    password = st.text_input("Password", type="password", key="su_password")
    if st.button("Register"):
        if is_valid_password(password):
            signup(engine, username, password)

elif menu == "Sign In":
    st.subheader("Sign In")
    username = st.text_input("Username", key="si_username")
    password = st.text_input("Password", type="password", key="si_password")
    if st.button("Login"):
        signIn(engine, username, password)

elif menu == "Update Password":
    st.subheader("Update Password")
    username = st.text_input("Username", key="up_username")
    old_password = st.text_input("Old Password", type="password")
    new_password = st.text_input("New Password", type="password")
    if st.button("Update"):
        if is_valid_password(new_password):
            update_password(engine, username, old_password, new_password)

elif menu == "Delete User":
    st.subheader("Delete User")
    username = st.text_input("Username", key="del_username")
    password = st.text_input("Password", type="password")
    if st.button("Delete"):
        delete_user(engine, username, password)

elif menu == "View Records":
    st.subheader("User List")
    read(engine)

elif menu == 'Exit':
    st.header("\nThank you...")

else:
    print("\nInvalid choice. Try again.")