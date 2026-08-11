import sqlite3
import os
 
DB_PATH = "data/chroma_db/chroma.sqlite3"
 
size_before = os.path.getsize(DB_PATH)
print(f"Size before: {size_before / (1024 * 1024):.1f} MB")
 
conn = sqlite3.connect(DB_PATH)
conn.execute("VACUUM")
conn.close()
 
size_after = os.path.getsize(DB_PATH)
print(f"Size after:  {size_after / (1024 * 1024):.1f} MB")
print(f"Reclaimed:   {(size_before - size_after) / (1024 * 1024):.1f} MB")
    