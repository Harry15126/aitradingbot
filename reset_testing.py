import os

FILES_TO_RESET = [
    "paper_journal.csv",
    "paper_account.csv",
    "open_trades.csv"
]

print("\n===== TEST RESET TOOL =====")

for file_name in FILES_TO_RESET:
    if os.path.isfile(file_name):
        os.remove(file_name)
        print("Deleted:", file_name)
    else:
        print("Not found:", file_name)

print("\nTesting files reset complete.")
print("Run python main.py to recreate fresh files.")