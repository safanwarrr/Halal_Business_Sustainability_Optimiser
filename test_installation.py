#!/usr/bin/env python3
"""
Test Installation Script for Halal Business Sustainability Optimizer

This script verifies that all dependencies are installed correctly
and demonstrates basic functionality.

Run this after installing requirements:
    python test_installation.py
"""

import sys

def test_imports():
    """Test that all required packages can be imported."""
    print("🔍 Testing package imports...")
    
    try:
        import pandas as pd
        print("   ✅ pandas imported successfully")
    except ImportError as e:
        print(f"   ❌ pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("   ✅ numpy imported successfully")
    except ImportError as e:
        print(f"   ❌ numpy import failed: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("   ✅ matplotlib imported successfully")
    except ImportError as e:
        print(f"   ❌ matplotlib import failed: {e}")
        return False
    
    try:
        import requests
        print("   ✅ requests imported successfully")
    except ImportError as e:
        print(f"   ❌ requests import failed: {e}")
        return False
    
    try:
        import ipywidgets
        print("   ✅ ipywidgets imported successfully")
    except ImportError as e:
        print(f"   ❌ ipywidgets import failed: {e}")
        return False
    
    return True


def test_custom_modules():
    """Test that our custom modules can be imported."""
    print("\n🔍 Testing custom modules...")
    
    try:
        from environmental_data_processor import EnvironmentalDataProcessor
        print("   ✅ environmental_data_processor imported successfully")
    except ImportError as e:
        print(f"   ❌ environmental_data_processor import failed: {e}")
        return False
    
    try:
        from sustainability_simulator import SustainabilitySimulator
        print("   ✅ sustainability_simulator imported successfully")
    except ImportError as e:
        print(f"   ❌ sustainability_simulator import failed: {e}")
        return False
    
    return True


def test_api_connection():
    """Test connection to Carbon Intensity API."""
    print("\n🔍 Testing API connection...")
    
    try:
        import requests
        response = requests.get("https://api.carbonintensity.org.uk/intensity", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            intensity = data['data'][0]['intensity']['actual'] or data['data'][0]['intensity']['forecast']
            print(f"   ✅ API connection successful!")
            print(f"   📊 Current UK grid carbon intensity: {intensity} g CO2/kWh")
            return True
        else:
            print(f"   ⚠️ API returned status code: {response.status_code}")
            print("   Note: Fallback values will be used if API is unavailable")
            return True
            
    except Exception as e:
        print(f"   ⚠️ API connection failed: {e}")
        print("   Note: This is okay! Fallback values will be used.")
        return True


def run_demo_calculation():
    """Run a demo calculation to show functionality."""
    print("\n🔍 Running demo calculation...")
    
    try:
        from environmental_data_processor import EnvironmentalDataProcessor
        
        processor = EnvironmentalDataProcessor()
        
        # Example restaurant
        business_params = {
            'electricity_kwh_month': 2000,
            'heating_kwh_month': 1500,
            'water_m3_month': 50,
            'waste_kg_month': 300,
            'transport_km_month': 1000,
            'transport_mode': 'van',
            'country': 'GB',
            'employees': 5
        }
        
        print("\n   📊 Example Business: Halal Restaurant")
        print("   " + "-" * 50)
        
        footprint = processor.calculate_business_carbon_footprint(business_params)
        
        print(f"   🌍 Monthly Emissions: {footprint['total_emissions_kg_month']:.1f} kg CO2")
        print(f"   📅 Annual Emissions: {footprint['total_emissions_tonnes_year']:.2f} tonnes CO2")
        print(f"   👤 Per Employee: {footprint['per_employee_kg_month']:.1f} kg CO2/month")
        print(f"   🌳 Trees Needed: {footprint['trees_to_offset_annual']:.0f} trees for 1 year")
        
        print("\n   📊 Breakdown:")
        for category, value in footprint['breakdown'].items():
            pct = footprint['percentages'][category]
            print(f"      {category.capitalize():12} {value:7.1f} kg ({pct:5.1f}%)")
        
        print("\n   ✅ Demo calculation completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Demo calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("🌍 Halal Business Sustainability Optimizer - Installation Test")
    print("=" * 70)
    print("\nبِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ")
    print("In the name of Allah, the Most Gracious, the Most Merciful\n")
    
    results = []
    
    # Run tests
    results.append(("Package Imports", test_imports()))
    results.append(("Custom Modules", test_custom_modules()))
    results.append(("API Connection", test_api_connection()))
    results.append(("Demo Calculation", run_demo_calculation()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 Test Summary")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("✅ All tests passed! Installation is successful.")
        print("\nYou can now run the Jupyter notebook:")
        print("   jupyter notebook Halal_Business_Sustainability_Optimizer.ipynb")
        print("\nMay Allah bless your efforts in environmental stewardship!")
        print("Jazakallahu Khairan! 🌍💚")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTry running:")
        print("   pip install -r requirements.txt")
        print("\nIf problems persist, check QUICK_START.md for troubleshooting.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
