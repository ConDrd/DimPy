from dimpy import UnitRegistry
import math

def solve_heat_transfer_problem():
    reg = UnitRegistry(autoload=True)
    
    print("--- Solving Heat Transfer Problem (Ejemplo 2-7) ---")
    
    # Inputs
    L_thickness = 0.3 * reg.cm
    D_pan = 20 * reg.cm
    Power_electric = 800 * reg.W
    efficiency = 0.9
    T_inner = 110 * reg.degC
    
    # 1. Calculate Effective Heat Transfer Rate (Q_dot)
    # 90% of heat generated is transferred to the pan
    Q_dot = Power_electric * efficiency
    print(f"Heat Transfer Rate (Q_dot) = {Q_dot}")
    
    # 2. Calculate Area of the bottom of the pan
    # A = pi * r^2 = pi * (D/2)^2
    radius = D_pan / 2
    # Note: radius is a Quantity (10 cm). radius**2 will be 100 cm^2.
    Area = math.pi * (radius ** 2)
    print(f"Area of Pan Bottom = {Area}")
    print(f"Area in m^2 = {Area.to('m^2')}")
    
    # 3. Calculate Heat Flux (q)
    # q = Q_dot / A
    # Units will be W / cm^2 initially
    Heat_Flux = Q_dot / Area
    print(f"Heat Flux (q) [raw] = {Heat_Flux}")
    
    # Convert to standard W/m^2
    # 1 cm = 0.01 m => 1 cm^2 = 1e-4 m^2
    # W/cm^2 = W / (1e-4 m^2) = 10000 W/m^2
    Heat_Flux_SI = Heat_Flux.to('W/m^2')
    print(f"Heat Flux (q) [SI] = {Heat_Flux_SI}")
    
    # Boundary Conditions Description
    print("\n--- Boundary Conditions ---")
    print(f"1. Top Surface (Inner): Fixed Temperature T = {T_inner}")
    print(f"2. Bottom Surface (Outer): Constant Heat Flux q = {Heat_Flux_SI}")
    
    # Verification approx check
    # Q = 720 W
    # A = pi * 0.1^2 = 0.0314159 m^2
    # q = 720 / 0.0314159 = 22918.3 W/m^2
    expected = 22918.3
    print(f"Expected q ~ {expected:.1f} W/m^2")

if __name__ == "__main__":
    solve_heat_transfer_problem()
