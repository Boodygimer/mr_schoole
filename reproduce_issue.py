import sys
print("Starting import...")
try:
    import app
    print("Import successful!")
except Exception as e:
    print(f"Import failed: {e}")
except SystemExit:
    print("SystemExit caught")
