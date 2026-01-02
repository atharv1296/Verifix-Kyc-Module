"""
Helper script to convert firebase_config.json to minified JSON for Render environment variable
"""

import json

print("=" * 70)
print("FIREBASE CREDENTIALS CONVERTER FOR RENDER")
print("=" * 70)
print()

try:
    # Read firebase_config.json
    with open('firebase_config.json', 'r') as f:
        config = json.load(f)
    
    # Convert to minified JSON (single line, no spaces)
    minified = json.dumps(config, separators=(',', ':'))
    
    print("✅ Successfully converted firebase_config.json to minified JSON")
    print()
    print("=" * 70)
    print("COPY THIS VALUE TO RENDER ENVIRONMENT VARIABLE:")
    print("=" * 70)
    print()
    print("Variable Name: FIREBASE_CREDENTIALS")
    print()
    print("Variable Value:")
    print("-" * 70)
    print(minified)
    print("-" * 70)
    print()
    print("=" * 70)
    print("INSTRUCTIONS:")
    print("=" * 70)
    print("1. Copy the entire line above (between the dashes)")
    print("2. Go to Render → Your Service → Environment")
    print("3. Add new environment variable:")
    print("   - Key: FIREBASE_CREDENTIALS")
    print("   - Value: (paste the copied line)")
    print("4. Save and redeploy")
    print("=" * 70)
    
    # Save to a text file for easy copying
    with open('firebase_env_value.txt', 'w') as f:
        f.write(minified)
    
    print()
    print("💾 Also saved to: firebase_env_value.txt")
    print()
    
except FileNotFoundError:
    print("❌ Error: firebase_config.json not found")
    print("   Make sure the file exists in the current directory")
except json.JSONDecodeError:
    print("❌ Error: Invalid JSON in firebase_config.json")
    print("   Check the file format")
except Exception as e:
    print(f"❌ Error: {str(e)}")
