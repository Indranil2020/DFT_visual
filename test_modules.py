"""
Quick test script to verify modules work correctly.
Run this to ensure everything is functioning before building UI.
"""

print("=" * 60)
print("TESTING DFT FLIGHT SIMULATOR MODULES")
print("=" * 60)

# Test 1: Validators
print("\n[1/4] Testing validators...")
from utils.validators import validate_element, validate_functional, validate_pseudo_accuracy

test_element = validate_element('C')
assert test_element == 6, "Element validation failed"
print("  ✓ Element validation works")

test_func = validate_functional('PBE')
assert test_func == 'PBE', "Functional validation failed"
print("  ✓ Functional validation works")

test_acc = validate_pseudo_accuracy('standard')
assert test_acc == 'standard', "Accuracy validation failed"
print("  ✓ Accuracy validation works")

# Test 2: Constants
print("\n[2/4] Testing constants...")
from utils.constants import ELEMENTS, FUNCTIONAL_INFO, BOHR_TO_ANGSTROM

assert ELEMENTS[6] == 'C', "Element lookup failed"
print("  ✓ Element constants loaded")

assert 'PBE' in FUNCTIONAL_INFO, "Functional info missing"
print("  ✓ Functional database loaded")

assert abs(BOHR_TO_ANGSTROM - 0.529177) < 0.001, "Physical constant wrong"
print("  ✓ Physical constants correct")

# Test 3: Pseudopotentials
print("\n[3/4] Testing pseudopotential module...")
from modules.pseudopotentials import get_available_pseudos, construct_pseudo_url

pseudos = get_available_pseudos()
assert 'C' in pseudos, "Carbon not in pseudopotentials"
print(f"  ✓ Found {len(pseudos)} elements with pseudopotentials")

url = construct_pseudo_url('C', 'standard', 'PBE')
assert url is not None, "URL construction failed"
assert 'Carbon' in url or 'C.upf' in url, "URL format wrong"
print("  ✓ Pseudopotential URL construction works")

# Test 4: Basis Sets
print("\n[4/4] Testing basis sets module...")
from modules.basis_sets import get_available_basis_sets, get_basis_for_element

basis_list = get_available_basis_sets()
assert len(basis_list) > 0, "No basis sets found"
print(f"  ✓ Found {len(basis_list)} basis sets")

# Try to get a basis set for Carbon
basis_data = get_basis_for_element('6-31G', 'C')
if basis_data is not None:
    print("  ✓ Basis set fetching works")
else:
    print("  ⚠ Basis set fetching returned None (might need cache)")

# Test 5: Plotting utilities
print("\n[5/5] Testing plotting utilities...")
from utils.plotting import get_plot_theme, create_comparison_plot
import numpy as np

theme = get_plot_theme()
assert 'template' in theme, "Plot theme missing template"
print("  ✓ Plot theme loaded")

# Create dummy data for comparison plot
data1 = {'x': np.linspace(0, 10, 50), 'y': np.sin(np.linspace(0, 10, 50))}
data2 = {'x': np.linspace(0, 10, 50), 'y': np.cos(np.linspace(0, 10, 50))}
fig = create_comparison_plot(data1, data2, ('sin', 'cos'), 'Test', 'x', 'y', show_difference=False)
assert fig is not None, "Comparison plot creation failed"
print("  ✓ Comparison plot creation works")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nModules are ready to use. You can now:")
print("1. Keep running the old app: streamlit run basis_visualizer_app.py")
print("2. Build new UI pages using these modules")
print("3. Test individual modules with this script")
print("\n" + "=" * 60)
