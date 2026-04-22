# Made by Yodahe Wondimu
# A script to analyze the data stored in the SQLite database and visualize trends.

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to DB
db_path = "C:/Users/yodiw/Workspace/Filefly/src/filefly/filefly.db"
conn = sqlite3.connect(db_path)

# Load all data
df = pd.read_sql_query("SELECT * FROM events", conn)

conn.close()

df["timestamp"] = pd.to_datetime(df["timestamp"])

print(df.head())

# Displays a scatter plot that visualizes file processing time based on file size.
# This plot in specific highlighted some very important trends in not only the file types studied
# but the algorithm processing them, and more information on findings can be found in the logs.
sorted_df = df[df["event_type"] == "sorted"]
size_df = sorted_df["size"] / 1024

plt.figure()
plt.scatter(size_df, sorted_df["processing_time"])

plt.title("Processing Time vs File Size")
plt.xlabel("File Size (kilobytes)")
plt.ylabel("Processing Time (seconds)")

plt.tight_layout()
plt.show()

# Below are some other scripts that can also be used for behavior analysis.
# -------------------------------------------------------------------
# *Amount of files processed by Filefly per extension*
# ext_counts = df["extension"].value_counts()

# plt.figure()
# ext_counts.plot(kind="bar")

# plt.title("File Types Processed by Filefly")
# plt.xlabel("Extension")
# plt.ylabel("Count")

# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()
# -------------------------------------------------------------------
# *File stabilization time distribution*
# plt.figure()
# plt.hist(df["stabilization_time"].dropna(), bins=20)

# plt.title("File Stabilization Time Distribution")
# plt.xlabel("Seconds")
# plt.ylabel("Frequency")

# plt.tight_layout()
# plt.show()
# -------------------------------------------------------------------
# *File events over time*
# events_over_time = df.groupby(df["timestamp"].dt.floor("min")).size()

# plt.figure()
# events_over_time.plot()

# plt.title("File Events Over Time")
# plt.xlabel("Time")
# plt.ylabel("Number of Events")

# plt.tight_layout()
# plt.show()