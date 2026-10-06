import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vehicle_params import AR_R_STABILITY_LIMITS, L1_verdict

DEFAULT_CLASS = "small_passenger"


def ford_L1(depth_m: float, velocity_ms: float, vehicle_class: str = DEFAULT_CLASS) -> tuple:
    return L1_verdict(depth_m, velocity_ms, vehicle_class), round(depth_m * velocity_ms, 6)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 can_it_ford_L1.py <depth_m> <velocity_ms> [vehicle_class]")
        print(f"  vehicle_class options: {list(AR_R_STABILITY_LIMITS)}  (default: {DEFAULT_CLASS})")
        sys.exit(1)

    depth_m = float(sys.argv[1])
    velocity_ms = float(sys.argv[2])
    vehicle_class = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_CLASS

    if vehicle_class not in AR_R_STABILITY_LIMITS:
        print(f"Unknown vehicle class '{vehicle_class}'. Options: {list(AR_R_STABILITY_LIMITS)}")
        sys.exit(1)

    verdict, hazard = ford_L1(depth_m, velocity_ms, vehicle_class)
    lim = AR_R_STABILITY_LIMITS[vehicle_class]

    print(verdict)
    print(f"depth={depth_m:.2f}m (limit {lim['depth_m']:.2f})  velocity={velocity_ms:.2f}m/s (limit {lim['velocity_ms']:.1f})  "
          f"hazard={hazard:.3f}m2/s (limit {lim['haz_m2s']:.2f})  class={vehicle_class}  source=Shand2011_ARR_Table3")
