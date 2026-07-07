import pandas as pd

def test_scenario_sweep_schema():
    df = pd.read_csv("scenario_sweep.csv")
    expected_columns = ["depth_m", "velocity_ms", "L0_verdict", "L1_haz", "L1_verdict"]
    assert list(df.columns) == expected_columns
    assert df["depth_m"].dtype == float
    assert df["velocity_ms"].dtype == float
    assert df["L1_haz"].dtype == float
