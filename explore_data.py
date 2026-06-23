import pandas as pd

# Looking at the international results dataset (1872-2017+)
results = pd.read_csv("results.csv/results.csv")
print("=" * 50)
print("results.csv columns:")
print("=" * 50)
print(results.columns.tolist())
print("\nFirst 3 rows:")
print(results.head(3))
print("\nTotal rows:", len(results))

print("\n\n")

# Looking at the World Cup specific matches dataset
wc = pd.read_csv("worldcup.csv/WorldCupMatches.csv")
print("=" * 50)
print("WorldCupMatches.csv columns:")
print("=" * 50)
print(wc.columns.tolist())
print("\nFirst 3 rows:")
print(wc.head(3))
print("\nTotal rows:", len(wc))