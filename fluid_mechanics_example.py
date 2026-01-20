from dimpy import UnitRegistry

def solve_pump_problem():
    reg = UnitRegistry(autoload=True)
    
    print("--- Solving Fluid Mechanics Pump Problem ---")
    
    # Inputs
    V = 1 * reg.L
    t = 40 * reg.s
    # P1 is vacuum (suction) 150 mmHg. In absolute? Or gauge?
    # Problem says "presion de succion de 150mm de mercurio al vacio". 
    # Usually means P_gauge = -150 mmHg.
    # P_discharge = 30 kPa (gauge implied).
    P_suction_mag = 150 * reg.mmHg
    P_discharge = 30 * reg.kPa
    
    efficiency = 0.6
    
    # 1. Flow Rate Q
    Q = V / t
    print(f"Flow Rate Q = {Q}")
    
    # 2. Convert units to SI for calculation consistency
    # 1 L = 0.001 m^3
    # 1 mmHg = 133.322 Pa
    # 1 kPa = 1000 Pa
    
    # Manually bridging dimensions for this simple library that treat 'L', 'Pa' as base:
    # We will compute the Power in base units of 'kPa L / s' first?
    # Or convert to standard SI bases manually?
    
    # Let's perform conversion by value manipulation to show "under the hood" or just define conversions.
    # Since we can't easily bridge 'L' to 'm^3' automatically in .to() without compound definition support,
    # We will use factors.
    
    # Conversion Factors (Bridging the gaps)
    # Define Liters to cubic meters
    factor_L_to_m3 = 0.001
    # Define mmHg to kPa
    factor_mmHg_to_kPa = 133.322 / 1000
    
    P_suction_kPa = P_suction_mag.value * factor_mmHg_to_kPa * reg.kPa
    # Suction is vacuum, so P1 = -P_suction
    P1 = -1.0 * P_suction_kPa
    P2 = P_discharge
    
    print(f"P1 (Suction) = {P1}")
    print(f"P2 (Discharge) = {P2}")
    
    # 3. Head / Pressure Difference
    # Delta P = P2 - P1
    # Check units match (kPa)
    Delta_P = P2 - P1 
    print(f"Delta P = {Delta_P}")
    
    # 4. Power (Hydraulic) = Q * Delta P
    # Units: (L/s) * kPa = L kPa / s
    Power_hydraulic = Q * Delta_P
    print(f"Hydraulic Power (raw units) = {Power_hydraulic}")
    
    # 5. Convert to Watts
    # 1 kPa * 1 L / s 
    # = (1000 Pa) * (0.001 m^3) / s 
    # = 1 Pa * m^3 / s 
    # = 1 (N/m^2) * m^3 / s 
    # = 1 N*m / s 
    # = 1 J / s 
    # = 1 Watt
    # So numerically, the value in (kPa L / s) IS the value in Watts!
    
    Power_watts_val = Power_hydraulic.value
    Power_watts = Power_watts_val * reg.W
    print(f"Hydraulic Power (Watts) = {Power_watts}")
    
    # 6. Brake Power (Motor Power)
    # P_motor = P_hydraulic / efficiency
    Power_motor = Power_watts / efficiency
    print(f"Motor Power Required = {Power_motor}")
    
    # Verification against hand calc: ~2.08 W
    # Hand calc:
    # P1 = -150 mmHg = -20 kPa
    # P2 = 30 kPa
    # dP = 50 kPa
    # Q = 1/40 L/s = 0.025 L/s
    # W_pump = 0.025 * 50 = 1.25 W
    # W_motor = 1.25 / 0.6 = 2.0833 W
    
    expected = 2.0833333333
    print(f"Expected: ~{expected:.2f} W")

if __name__ == "__main__":
    solve_pump_problem()
