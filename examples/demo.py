from dimpy import UnitRegistry
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

def main():
    reg = UnitRegistry(autoload=True)
    
    print("--- Dynamic Prefixes ---")
    
    # 1. kilometer (dynamic)
    # 'kilometer' is not in defaults, but 'kilo' + 'meter' is.
    # Note: 'km' is manual shortcut, 'kilometer' is dynamic.
    d1 = 1 * reg.kilometer
    print(f"1 kilometer = {d1.to('meter')}")
    
    # micrometer
    d2 = 1 * reg.micrometer
    print(f"1 micrometer = {d2.to('meter')}")
    
    # gigawatt
    p1 = 1.21 * reg.gigawatt
    print(f"1.21 gigawatt = {p1.to('watt')}")
    
    # milligram (base is gram)
    m1 = 100 * reg.milligram
    print(f"100 milligram = {m1.to('gram')}")

    print("\n--- Array Support (Lists) ---")
    
    # Create Quantity from list
    lens = [1, 2, 3] * reg.meter
    print(f"Lengths: {lens}")
    
    # Convert list
    lens_cm = lens.to('centimeter')
    print(f"Lengths in cm: {lens_cm}")
    
    # List Arithmetic
    # [1, 2, 3] m + 1 m = [2, 3, 4] m
    lens_plus_1 = lens + 1 * reg.meter
    print(f"Lengths + 1m: {lens_plus_1}")
    
    if HAS_NUMPY:
        print("\n--- Numpy Support ---")
        
        arr = np.array([10, 20, 30])
        q_arr = arr * reg.meter
        print(f"Numpy Quantity: {q_arr}")
        
        # Element-wise addition
        q_arr2 = q_arr + 5 * reg.meter
        print(f"Numpy + scalar: {q_arr2}")
        
        # Numpy ufunc (sqrt) - not fully implemented in ufunc yet? 
        # But let's test basic arithmetic.
        
        # Array + Array
        q_sum = q_arr + q_arr2
        print(f"Array + Array: {q_sum}")
        
        # Conversion
        q_cm = q_arr.to('centimeter')
        print(f"Numpy in cm: {q_cm}")
        
        # Compatibility with numpy functions?
        # mean() -> quantity?
        # If __array_ufunc__ handled well or __array_function__
        # For now, simplistic.
    else:
        print("\nSkipping Numpy tests (Numpy not installed)")
    
    print("\n--- String Parsing ---")
    p1 = reg.parse("10 km/hr")
    print(f"Parsed '10 km/hr': {p1} -> {p1.to('m/s')}")
    
    p2 = reg.parse("50 kg * m / s^2")
    print(f"Parsed '50 kg * m / s^2': {p2}")
    
    print("\n--- Physical Constants ---")
    from dimpy import constants
    print(f"Speed of light (c): {constants.c}")
    print(f"c in km/s: {constants.c.to('km/s')}")
    print(f"Standard Gravity (g_0): {constants.g_0}")

if __name__ == "__main__":
    main()
