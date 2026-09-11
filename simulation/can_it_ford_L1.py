import sys

THRESHOLDS_M2S = {
    "sedan": 0.30,
    "large_passenger": 0.45,
    "large_4wd": 0.60,
}
DEFAULT_CLASS = "large_4wd"

def ford_L1(depth_m: float, velocity_ms: float, vehicle_class: str = DEFAULT_CLASS) -> tuple:
    hazard = depth_m * velocity_ms
    threshold = THRESHOLDS_M2S[vehicle_class]
    verdict = "FORD" if hazard <= threshold else "NO-FORD"
    return verdict, hazard

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python3 can_it_ford_L1.py <depth_m> <velocity_ms> [vehicle_class]")
        print(f"  vehicle_class options: {list(THRESHOLDS_M2S.keys())}  (default: {DEFAULT_CLASS})")
        sys.exit(1)

    depth_m = float(sys.argv[1])
    velocity_ms = float(sys.argv[2])
    vehicle_class = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_CLASS

    if vehicle_class not in THRESHOLDS_M2S:
        print(f"Unknown vehicle class '{vehicle_class}'. Options: {list(THRESHOLDS_M2S.keys())}")
        sys.exit(1)

    verdict, hazard = ford_L1(depth_m, velocity_ms, vehicle_class)
    threshold = THRESHOLDS_M2S[vehicle_class]

    print(verdict)
    print(f"depth={depth_m:.2f}m  velocity={velocity_ms:.1f}m/s  hazard={hazard:.3f}m2/s  threshold={threshold:.2f}  class={vehicle_class}  source=Shand2011_ARR")
