#!/usr/bin/env python3
"""
Download and cache all basis set metadata locally for fast offline access
"""

import basis_set_exchange as bse
import json
import os
from datetime import datetime
from pathlib import Path
import sys

CACHE_DIR = Path(__file__).parent / "basis_cache"
METADATA_FILE = CACHE_DIR / "metadata.json"

def download_all_basis_sets():
    """Download metadata for all basis sets"""
    
    print("🚀 Starting basis set cache download...")
    print(f"📁 Cache directory: {CACHE_DIR}")
    
    # Create cache directory
    CACHE_DIR.mkdir(exist_ok=True)
    
    # Get all basis set names
    all_names = bse.get_all_basis_names()
    print(f"📊 Found {len(all_names)} basis sets")
    
    # Get families
    families = bse.get_families()
    print(f"👨‍👩‍👧‍👦 Found {len(families)} families")
    
    cache_data = {
        'download_date': datetime.now().isoformat(),
        'total_basis_sets': len(all_names),
        'families': families,
        'basis_sets': {}
    }
    
    successful = 0
    failed = 0
    
    for idx, name in enumerate(all_names, 1):
        try:
            # Progress indicator
            if idx % 10 == 0:
                print(f"⏳ Progress: {idx}/{len(all_names)} ({idx*100//len(all_names)}%)")
            
            # Get basis data for hydrogen (lightest element) to extract metadata
            basis_data = bse.get_basis(name, elements='1')
            
            # Get available elements (try common ones)
            available_elements = []
            test_elements = [1, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 
                           19, 20, 26, 29, 30, 35, 36, 47, 53, 54, 79, 80, 82, 86]
            
            for z in test_elements:
                try:
                    bse.get_basis(name, elements=str(z))
                    available_elements.append(z)
                except:
                    pass
            
            # Store metadata
            cache_data['basis_sets'][name] = {
                'name': basis_data.get('name', name),
                'display_name': basis_data.get('names', [name])[0] if basis_data.get('names') else name,
                'family': basis_data.get('family', 'Other'),
                'description': basis_data.get('description', 'No description available'),
                'role': basis_data.get('role', 'orbital'),
                'available_elements': available_elements,
                'tags': basis_data.get('tags', [])
            }
            
            successful += 1
            
        except Exception as e:
            print(f"❌ Failed to process {name}: {e}")
            failed += 1
            continue
    
    # Save cache
    print(f"\n💾 Saving cache to {METADATA_FILE}...")
    with open(METADATA_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"\n✅ Cache download complete!")
    print(f"   ✓ Successful: {successful}")
    print(f"   ✗ Failed: {failed}")
    print(f"   📦 Cache size: {METADATA_FILE.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"\n🎉 You can now run the app with fast local access!")

def check_cache_age():
    """Check if cache needs updating (older than 30 days)"""
    if not METADATA_FILE.exists():
        return None
    
    with open(METADATA_FILE, 'r') as f:
        data = json.load(f)
    
    download_date = datetime.fromisoformat(data['download_date'])
    age_days = (datetime.now() - download_date).days
    
    return age_days

if __name__ == "__main__":
    # Check if cache exists
    if METADATA_FILE.exists():
        age = check_cache_age()
        print(f"📦 Existing cache found (age: {age} days)")
        
        if age < 30:
            response = input("Cache is recent. Re-download anyway? (y/N): ")
            if response.lower() != 'y':
                print("✅ Using existing cache")
                sys.exit(0)
    
    download_all_basis_sets()
