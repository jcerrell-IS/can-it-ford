    try:
        import sys as _sys
        from pathlib import Path as _Path
        _root = str(_Path(__file__).resolve().parents[1])
        if _root not in _sys.path:
            _sys.path.insert(0, _root)
        from analysis.run_provenance import collect_run_provenance
        res["provenance_v2"] = collect_run_provenance(
            script=__file__,
            mesh_paths=None,  # procedural cube_mesh(); no mesh asset to hash
            solver_source=PROVENANCE.get("solver_source"),
            solver_pinned_sha=PROVENANCE.get("pinned_sha"),
            grid_density=(res.get("geometry") or {}).get("n_grid"),
            vehicle_mass=(res.get("geometry") or {}).get("box_mass_kg"),
            bulk_modulus=BULK,
        )
    except Exception as exc:  # provenance must never break a run
        res["provenance_v2"] = {"schema": "canitford.provenance/2",
                                "error": f"capture failed: {exc!r}"}
