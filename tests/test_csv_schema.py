import pandas as pd

def test_scenario_sweep_schema():
    df = pd.read_csv("data/scenario_sweep.csv")
    expected_columns = ["depth_m", "velocity_ms", "L0_verdict", "L1_haz",
                        "L1_haz_product_only", "L1_verdict",
                        "L1_verdict_small_car", "L1_verdict_four_wd"]
    assert list(df.columns) == expected_columns
    assert df["depth_m"].dtype == float
    assert df["velocity_ms"].dtype == float
    assert df["L1_haz"].dtype == float

def test_l2_results_schema():
    df = pd.read_csv("data/l2_results_from_wandb.csv")
    required = ["depth_m", "velocity_ms", "l1_verdict", "l2_verdict", "divergence"]
    for col in required:
        assert col in df.columns
