import MySQLdb

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'pass',
    'db': 'AdventureWorks2019',
}
  
# Create a connection to the database
conn = MySQLdb.connect(**db_config)       


