import sys

DEPTH_THRESHOLD_M = 0.15

def ford_L0(depth_m: float) -> str:
    return "FORD" if depth_m < DEPTH_THRESHOLD_M else "NO-FORD"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 can_it_ford_L0.py <depth_m>")
        sys.exit(1)

    depth_m = float(sys.argv[1])
    verdict = ford_L0(depth_m)

    print(verdict)
    print(f"depth={depth_m:.2f}m  threshold={DEPTH_THRESHOLD_M:.2f}m  source=NWS_TADD")
