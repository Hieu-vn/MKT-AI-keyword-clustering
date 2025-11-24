#!/usr/bin/env python3
"""
Script to manage API Keys for the Keyword Cluster Service.
Supports creating, listing, and revoking keys.
Keys are stored in 'api_keys.json'.
"""
import json
import secrets
import os
from datetime import datetime

KEYS_FILE = "api_keys.json"

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return {}
    try:
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def generate_key(client_name="default"):
    """Generate a secure random API key"""
    # Generate a 32-byte hex token (64 chars)
    key = f"sk-{secrets.token_hex(16)}"
    
    keys = load_keys()
    
    # Metadata for the key
    key_data = {
        "client_name": client_name,
        "created_at": datetime.now().isoformat(),
        "active": True,
        "key": key
    }
    
    # Store by key value for fast lookup, or by ID if we wanted complexity
    # Here we store a list of key objects for simplicity in management
    if "keys" not in keys:
        keys["keys"] = []
        
    keys["keys"].append(key_data)
    save_keys(keys)
    
    print(f"\n✅ API Key created successfully for '{client_name}'")
    print(f"🔑 Key: {key}")
    print("⚠️  Save this key now! It allows access to the Clustering API.\n")
    return key

def list_keys():
    keys = load_keys()
    if "keys" not in keys or not keys["keys"]:
        print("\nNo API keys found.")
        return

    print(f"\n{'Client Name':<20} {'Created At':<25} {'Active':<10} {'Key Prefix'}")
    print("-" * 70)
    for k in keys["keys"]:
        status = "✅ Yes" if k.get("active", True) else "❌ No"
        prefix = k["key"][:8] + "..." + k["key"][-4:]
        print(f"{k['client_name']:<20} {k['created_at']:<25} {status:<10} {prefix}")
    print("-" * 70 + "\n")

def revoke_key(client_name):
    keys = load_keys()
    if "keys" not in keys:
        print("No keys found.")
        return

    found = False
    for k in keys["keys"]:
        if k["client_name"] == client_name:
            k["active"] = False
            found = True
            print(f"🚫 Key for '{client_name}' has been revoked (deactivated).")
    
    if found:
        save_keys(keys)
    else:
        print(f"Client '{client_name}' not found.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manage API Keys")
    subparsers = parser.add_subparsers(dest="command")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new API key")
    create_parser.add_argument("client", help="Name of the client/partner")
    
    # List command
    subparsers.add_parser("list", help="List all API keys")
    
    # Revoke command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke an API key")
    revoke_parser.add_argument("client", help="Name of the client to revoke")
    
    args = parser.parse_args()
    
    if args.command == "create":
        generate_key(args.client)
    elif args.command == "list":
        list_keys()
    elif args.command == "revoke":
        revoke_key(args.client)
    else:
        parser.print_help()
