import sqlite3

# Dictionary containing the data to be inserted
data_to_insert = {
    'bad.gif': 'doc890775441_686084149',
    'game.gif': 'doc890775441_686084150',
    'good.gif': 'doc890775441_686084152',
    'winner.gif': 'doc890775441_686084153',
    'winner2.gif': 'doc890775441_686084155',
    'winner3.gif': 'doc890775441_686084157',
    'winner4.gif': 'doc890775441_686084158',
    'winner5.gif': 'doc890775441_686084161',
    'winner6.gif': 'doc890775441_686084163'
}

# Function to insert data into the database
def insert_data(data):
    with sqlite3.connect("DB.db") as db:
        cursor = db.cursor()
        inj = "INSERT INTO attachment (name, adress) VALUES(?, ?)"
        for file, address in data.items():
            try:
                cursor.execute(inj, (file, address))
            except sqlite3.Error as e:
                print(f"Error inserting {file}: {e}")
        db.commit()  # Commit the changes after all inserts

# Call the function to insert the data
insert_data(data_to_insert)