import json
import sys
from pathlib import Path

import numpy as np
from joblib import dump
from sklearn.gaussian_process import GaussianProcessClassifier, GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, Matern, WhiteKernel
from sklearn.preprocessing import StandardScaler

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "data" / "track1_sweep_v2" / "manifest.csv"
OUTDIR = REPO / "analysis"
THRESHOLD = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
SEED = 0

FEATURES = ["depth_m", "velocity_ms", "vehicle_mass_kg", "bbox_l_m", "bbox_w_m", "bbox_h_m"]
INTERIOR_DEPTHS = [0.30, 0.45]
INTERIOR_VELOCITIES = [1.5]
MIN_Z_LAYERS = 2
N_GRID = 64


def water_z_layers(bbox, depth, n_grid):
    length, width, height = bbox
    lim = max(2.2 * length, 3.5 * width, 6.0 * depth)
    dx = lim / n_grid
    h = dx / 2.0
    floor = 3.0 * dx
    return len(np.arange(floor + 0.5 * h, floor + depth, h))


def load():
    import csv

    rows = list(csv.DictReader(open(MANIFEST)))
    keep = []
    for r in rows:
        bbox = (float(r["bbox_l_m"]), float(r["bbox_w_m"]), float(r["bbox_h_m"]))
        n = water_z_layers(bbox, float(r["depth_m"]), N_GRID)
        if n >= MIN_Z_LAYERS:
            keep.append(r)
        else:
            print("EXCLUDED (%d water layer(s), under-resolved): %s" % (n, r["run_id"]))
    rows = keep
    X = np.array([[float(r[f]) for f in FEATURES] for r in rows])
    y = np.array([float(r["final_disp_m"]) for r in rows])
    depth = np.array([float(r["depth_m"]) for r in rows])
    vel = np.array([float(r["velocity_ms"]) for r in rows])
    cls = np.array([r["vehicle_class"] for r in rows])
    rid = np.array([r["run_id"] for r in rows])
    return rows, X, y, depth, vel, cls, rid


def make_regressor(n_features):
    kernel = ConstantKernel(1.0, (1e-3, 1e3)) * Matern(
        length_scale=np.ones(n_features), length_scale_bounds=(1e-2, 1e3), nu=2.5
    ) + WhiteKernel(noise_level=1e-4, noise_level_bounds=(1e-9, 1e1))
    return GaussianProcessRegressor(
        kernel=kernel, normalize_y=True, n_restarts_optimizer=8, random_state=SEED
    )


def make_classifier(n_features):
    kernel = ConstantKernel(1.0, (1e-3, 1e3)) * RBF(
        length_scale=np.ones(n_features), length_scale_bounds=(1e-2, 1e3)
    )
    return GaussianProcessClassifier(kernel=kernel, n_restarts_optimizer=8, random_state=SEED)


def fit_reg(Xtr, ytr, log_space):
    sc = StandardScaler().fit(Xtr)
    t = np.log10(ytr) if log_space else ytr
    g = make_regressor(Xtr.shape[1]).fit(sc.transform(Xtr), t)
    return sc, g


def pred_reg(sc, g, Xte, log_space):
    mu, sd = g.predict(sc.transform(Xte), return_std=True)
    if not log_space:
        return mu, sd
    return mu, sd


def cv_regression(X, y, folds, log_space):
    mus, sds, trues = [], [], []
    for tr, te in folds:
        sc, g = fit_reg(X[tr], y[tr], log_space)
        mu, sd = pred_reg(sc, g, X[te], log_space)
        mus.append(mu)
        sds.append(sd)
        trues.append(np.log10(y[te]) if log_space else y[te])
    mu = np.concatenate(mus)
    sd = np.concatenate(sds)
    yt = np.concatenate(trues)
    z = (yt - mu) / sd
    resid = yt - mu
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((yt - yt.mean()) ** 2))
    return {
        "n": int(len(yt)),
        "rmse": float(np.sqrt(np.mean(resid**2))),
        "mae": float(np.mean(np.abs(resid))),
        "r2": float(1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan"),
        "z_mean": float(z.mean()),
        "z_std": float(z.std(ddof=1)),
        "z_absmax": float(np.abs(z).max()),
        "cov68": float(np.mean(np.abs(z) <= 1.0)),
        "cov95": float(np.mean(np.abs(z) <= 1.959964)),
        "z": z.tolist(),
        "mu": mu.tolist(),
        "true": yt.tolist(),
    }


def loo_folds(n):
    return [(np.setdiff1d(np.arange(n), [i]), np.array([i])) for i in range(n)]


def group_folds(values, levels):
    out = []
    idx = np.arange(len(values))
    for lv in levels:
        te = idx[np.isclose(values, lv)]
        tr = np.setdiff1d(idx, te)
        out.append((lv, tr, te))
    return out


def cv_classifier_loo(X, ylab):
    n = len(ylab)
    preds = np.zeros(n, dtype=int)
    probs = np.zeros(n)
    skipped = []
    for i in range(n):
        tr = np.setdiff1d(np.arange(n), [i])
        if len(np.unique(ylab[tr])) < 2:
            skipped.append(int(i))
            preds[i] = -1
            probs[i] = np.nan
            continue
        sc = StandardScaler().fit(X[tr])
        g = make_classifier(X.shape[1]).fit(sc.transform(X[tr]), ylab[tr])
        preds[i] = int(g.predict(sc.transform(X[i : i + 1]))[0])
        probs[i] = float(g.predict_proba(sc.transform(X[i : i + 1]))[0, 1])
    return preds, probs, skipped


def confusion(ytrue, ypred):
    m = ypred >= 0
    tp = int(np.sum((ytrue == 1) & (ypred == 1) & m))
    fn = int(np.sum((ytrue == 1) & (ypred == 0) & m))
    fp = int(np.sum((ytrue == 0) & (ypred == 1) & m))
    tn = int(np.sum((ytrue == 0) & (ypred == 0) & m))
    return tp, fn, fp, tn


def main():
    rows, X, y, depth, vel, cls, rid = load()
    n = len(y)
    ylab = (y <= THRESHOLD).astype(int)
    res = {"threshold": THRESHOLD, "n": n, "n_ford": int(ylab.sum()), "features": FEATURES}
    res["ford_runs"] = [rid[i] for i in range(n) if ylab[i] == 1]

    print("=" * 72)
    print("THRESHOLD = %.4f m | FORD (positive) = %d / %d" % (THRESHOLD, ylab.sum(), n))
    print("FORD runs:", ", ".join(res["ford_runs"]) if ylab.sum() else "NONE")
    print("=" * 72)

    for log_space in [False, True]:
        tag = "log10" if log_space else "raw"
        r = cv_regression(X, y, loo_folds(n), log_space)
        res["reg_loocv_" + tag] = r
        print("\n--- GPR leave-one-condition-out (%d folds), %s space ---" % (n, tag))
        print("  RMSE=%.4f  MAE=%.4f  R2=%.4f" % (r["rmse"], r["mae"], r["r2"]))
        print("  standardized residuals: mean=%+.3f sd=%.3f max|z|=%.2f"
              % (r["z_mean"], r["z_std"], r["z_absmax"]))
        print("  coverage: 68%% nominal -> %.1f%% actual | 95%% nominal -> %.1f%% actual"
              % (100 * r["cov68"], 100 * r["cov95"]))

    log_space = False
    print("\n--- GPR leave-one-DEPTH-row-out (%s space) ---" % ("log10" if log_space else "raw"))
    res["depth_rows"] = []
    for lv, tr, te in group_folds(depth, sorted(set(depth))):
        interior = any(np.isclose(lv, d) for d in INTERIOR_DEPTHS)
        sc, g = fit_reg(X[tr], y[tr], log_space)
        mu, sd = pred_reg(sc, g, X[te], log_space)
        yt = np.log10(y[te]) if log_space else y[te]
        z = (yt - mu) / sd
        rec = {
            "level": float(lv), "interior": bool(interior), "n_test": int(len(te)),
            "rmse": float(np.sqrt(np.mean((yt - mu) ** 2))),
            "z_absmax": float(np.abs(z).max()), "cov95": float(np.mean(np.abs(z) <= 1.959964)),
        }
        res["depth_rows"].append(rec)
        print("  depth=%.2f  %-14s n_test=%2d  RMSE=%.4f  max|z|=%5.2f  cov95=%.0f%%"
              % (lv, "INTERPOLATION" if interior else "EXTRAPOLATION", len(te),
                 rec["rmse"], rec["z_absmax"], 100 * rec["cov95"]))

    print("\n--- GPR leave-one-VELOCITY-column-out (%s space) ---" % ("log10" if log_space else "raw"))
    res["vel_cols"] = []
    for lv, tr, te in group_folds(vel, sorted(set(vel))):
        interior = any(np.isclose(lv, v) for v in INTERIOR_VELOCITIES)
        sc, g = fit_reg(X[tr], y[tr], log_space)
        mu, sd = pred_reg(sc, g, X[te], log_space)
        yt = np.log10(y[te]) if log_space else y[te]
        z = (yt - mu) / sd
        rec = {
            "level": float(lv), "interior": bool(interior), "n_test": int(len(te)),
            "rmse": float(np.sqrt(np.mean((yt - mu) ** 2))),
            "z_absmax": float(np.abs(z).max()), "cov95": float(np.mean(np.abs(z) <= 1.959964)),
        }
        res["vel_cols"].append(rec)
        print("  vel=%.2f  %-14s n_test=%2d  RMSE=%.4f  max|z|=%5.2f  cov95=%.0f%%"
              % (lv, "INTERPOLATION" if interior else "EXTRAPOLATION", len(te),
                 rec["rmse"], rec["z_absmax"], 100 * rec["cov95"]))

    print("\n--- GPC leave-one-condition-out (36 folds) ---")
    if len(np.unique(ylab)) < 2:
        print("  SINGLE CLASS at this threshold. Classifier not fittable. Skipped.")
        res["clf"] = {"fittable": False}
    else:
        preds, probs, skipped = cv_classifier_loo(X, ylab)
        tp, fn, fp, tn = confusion(ylab, preds)
        acc = (tp + tn) / max(1, (tp + tn + fp + fn))
        majority = max((ylab == 0).sum(), (ylab == 1).sum()) / n
        rec = {
            "fittable": True, "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "accuracy": float(acc), "majority_baseline": float(majority),
            "ford_recall": float(tp / max(1, tp + fn)),
            "skipped_single_class_folds": skipped,
            "ford_probs": [probs[i] for i in range(n) if ylab[i] == 1],
        }
        res["clf"] = rec
        print("  confusion: TP=%d FN=%d FP=%d TN=%d" % (tp, fn, fp, tn))
        print("  accuracy = %.4f   majority-class baseline = %.4f" % (acc, majority))
        print("  FORD-class recall = %.3f  (%d of %d held-out FORD runs recovered)"
              % (rec["ford_recall"], tp, tp + fn))
        print("  held-out FORD probabilities:",
              ", ".join("%.3f" % p for p in rec["ford_probs"]))

        print("\n--- GPC leave-one-DEPTH-row-out ---")
        res["clf_depth"] = []
        for lv, tr, te in group_folds(depth, sorted(set(depth))):
            interior = any(np.isclose(lv, d) for d in INTERIOR_DEPTHS)
            note = ""
            if len(np.unique(ylab[tr])) < 2:
                note = "TRAIN SINGLE-CLASS, not fittable"
                acc_f = float("nan")
            else:
                sc = StandardScaler().fit(X[tr])
                g = make_classifier(X.shape[1]).fit(sc.transform(X[tr]), ylab[tr])
                p = g.predict(sc.transform(X[te]))
                acc_f = float(np.mean(p == ylab[te]))
                if ylab[te].sum() == 0:
                    note = "no FORD in held-out row, accuracy vacuous"
            res["clf_depth"].append(
                {"level": float(lv), "interior": bool(interior),
                 "n_ford_test": int(ylab[te].sum()), "n_ford_train": int(ylab[tr].sum()),
                 "accuracy": acc_f, "note": note})
            print("  depth=%.2f %-14s ford_in_train=%d ford_in_test=%d acc=%s  %s"
                  % (lv, "INTERPOLATION" if interior else "EXTRAPOLATION",
                     ylab[tr].sum(), ylab[te].sum(),
                     "n/a" if np.isnan(acc_f) else "%.3f" % acc_f, note))

    sc_r, g_r = fit_reg(X, y, False)
    dump({"scaler": sc_r, "model": g_r, "features": FEATURES, "target": "final_disp_m"},
         OUTDIR / "gp_regressor.joblib")
    res["reg_kernel"] = str(g_r.kernel_)
    res["reg_lml"] = float(g_r.log_marginal_likelihood_value_)
    print("\nfitted GPR kernel: %s" % g_r.kernel_)

    if len(np.unique(ylab)) >= 2:
        sc_c = StandardScaler().fit(X)
        g_c = make_classifier(X.shape[1]).fit(sc_c.transform(X), ylab)
        dump({"scaler": sc_c, "model": g_c, "features": FEATURES,
              "threshold_m": THRESHOLD, "positive_class": "FORD"},
             OUTDIR / "gp_classifier.joblib")
        res["clf_kernel"] = str(g_c.kernel_)
        print("fitted GPC kernel: %s" % g_c.kernel_)

    json.dump(res, open(OUTDIR / "gp_surrogate_metrics.json", "w"), indent=2)
    print("\nwrote %s" % (OUTDIR / "gp_surrogate_metrics.json"))


main()
