# USGS Shoal Creek Gage Grounding, Sweep Parameter Comparison

Source: USGS-08156800, Shoal Ck at W 12th St, Austin, TX
Pulled via dataretrieval.waterdata, parameter codes 00060 (discharge) and 00065 (gage height)
Period: 2024-10-01 to present (~651-day daily record)
Pulled and verified: July 2026

## Real values (daily statistic_id split, not pooled)

| | Discharge (cfs) | Gage height (ft / m) |
|---|---|---|
| Daily max (00001), peak day in record | 5,040 | 15.41 ft / 4.70 m |
| Daily min (00002), baseflow | 22.9 | 2.19 ft / 0.67 m |
| Daily mean (00003), typical peak day | 571 | 4.28 ft / 1.30 m |
| Daily min (00002), quietest observed | | 0.62 ft / 0.19 m |

## Comparison to Can It Ford sweep bounds

- Sweep depth range: 0.1 to 1.0 m. Peak observed gage height: 4.70 m.
  Sweep tops out well below the extreme tail at this gage, conservative, not extreme-event coverage.
- Discharge ratio, peak-day-max to typical-day-mean: roughly 850x. Supports the rapid-onset, flashy-urban-creek framing motivating this project.
- Velocity (parameter 00055) confirmed unavailable at this gage. Checked directly against both the continuous time series and 731 field-measurement records going back years: zero velocity readings exist in either, even for measurements taken with methods that inherently compute velocity as an intermediate step, such as mid-section current-meter surveys and Acoustic Doppler Current Profiler readings. The modernized USGS Water Data API does not surface that intermediate value for this site. Sweep's velocity bound (0 to 3.0 m/s) remains ungrounded against USGS data for this gage. Recommend citing the tested velocity range from Smith, Modra and Felder 2019 instead, since that is full-scale road/flume velocity, not creek-channel velocity, and is a closer physical match to the fording question than any creek gage would be.

## Caveat, do not skip

Gage height is water-surface elevation in the creek channel cross-section, not water depth over a specific road crossing. This is context for plausibility, not a literal substitute for road-crossing depth. Do not cite as USGS confirms our depths occur.
