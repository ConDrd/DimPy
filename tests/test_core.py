import pytest
import math
from dimpy import UnitRegistry, constants

# Check for numpy
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

@pytest.fixture
def reg():
    return UnitRegistry(autoload=True)

def test_dynamic_prefixes(reg):
    # kilometer (dynamic)
    d1 = 1 * reg.kilometer
    assert d1.to('meter').value == 1000.0
    
    # micrometer
    d2 = 1 * reg.micrometer
    assert d2.to('meter').value == 1e-6
    
    # milligram
    m1 = 100 * reg.milligram
    assert m1.to('gram').value == 0.1

def test_list_support(reg):
    # Create Quantity from list
    lens = [1, 2, 3] * reg.meter
    assert lens.value == [1, 2, 3]
    
    # Convert list
    lens_cm = lens.to('centimeter')
    assert lens_cm.value == [100.0, 200.0, 300.0]
    
    # List Arithmetic
    # [1, 2, 3] m + 1 m = [2, 3, 4] m
    lens_plus_1 = lens + 1 * reg.meter
    assert lens_plus_1.value == [2, 3, 4]

@pytest.mark.skipif(not HAS_NUMPY, reason="Numpy not installed")
def test_numpy_support(reg):
    arr = np.array([10, 20, 30])
    q_arr = arr * reg.meter
    
    # Element-wise addition
    q_arr2 = q_arr + 5 * reg.meter
    expected = np.array([15, 25, 35])
    np.testing.assert_array_equal(q_arr2.value, expected)
    
    # Array + Array
    q_sum = q_arr + q_arr2
    expected_sum = np.array([25, 45, 65])
    np.testing.assert_array_equal(q_sum.value, expected_sum)
    
    # Conversion
    q_cm = q_arr.to('centimeter')
    expected_cm = np.array([1000.0, 2000.0, 3000.0])
    np.testing.assert_array_equal(q_cm.value, expected_cm)

def test_string_parsing(reg):
    p1 = reg.parse("10 km/hr")
    # 10 km/hr = 10 * 1000 / 3600 m/s = 2.777... m/s
    converted = p1.to('m/s')
    assert math.isclose(converted.value, 2.7777777777777777, rel_tol=1e-5)
    
    p2 = reg.parse("50 kg * m / s^2")
    # Just checking it parses without error and has correct dimensions logic if we were to check
    assert p2 is not None

def test_physical_constants(reg):
    # c is speed of light, approx 3e8 m/s
    val_kms = constants.c.to('km/s').value
    # c exact is 299792458 m/s = 299792.458 km/s
    assert math.isclose(val_kms, 299792.458, rel_tol=1e-5)
