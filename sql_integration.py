import pandas as pd
from sqlalchemy import create_engine

# Step 1: Load the CSV file
df = pd.read_csv('twitter.csv')  # Make sure the file is in the same folder or give the full path

# Optional: Check the first few rows
print("📄 Preview of data:")
print(df.head())

# Step 2: MySQL connection details
username = 'root'                # Replace with your MySQL username
password = ''       # Replace with your MySQL password
host = 'localhost'
port = '3306'                    # Default MySQL port
database = 'twitter_feedback_db' # The database you created earlier

# Step 3: Create a connection to the MySQL database
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')

# Step 4: Import the data into MySQL (table name: twitter_feedback)
df.to_sql('twitter_feedback', con=engine, if_exists='replace', index=False)

print("✅ CSV file successfully imported into MySQL!")
