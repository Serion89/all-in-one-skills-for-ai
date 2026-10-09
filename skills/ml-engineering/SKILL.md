---
name: ml-engineering
description: Machine learning engineering from data to production - frame the problem and a baseline, prevent leakage in data splits, make training reproducible, evaluate against the decision that will be made, define offline and online acceptance gates, and monitor drift and degradation after deploy. Use when training, evaluating, shipping, or maintaining a predictive or generative model within a product or pipeline.
license: MIT
metadata:
  author: sahildark789
  version: "1.0.0"
---

# ML Engineering

A model is a component inside a system that makes decisions. The engineering job is to
make sure its measured quality matches the quality the decision needs, and that it stays
that way after deployment.

## 1. Frame the problem

- What decision does the prediction change, and what does each kind of error cost?
- Is ML needed at all? Write the rules-based or heuristic baseline first and record its score.
- Define the label precisely: what event, over what window, observed how, and with what delay.

## 2. Prevent leakage before modeling

- Split data by the unit that will be seen in production (user, device, time), not randomly
  across correlated rows.
- For time series, split chronologically and never let features use information from the future.
- Fit scalers, encoders, and imputers inside the training fold only.
- Check that no feature is a proxy for the label (for example, a field written after the outcome).

## 3. Make training reproducible

- Pin data versions, code commit, dependencies, random seeds, and hyperparameters.
- Log every run: config, metrics, artifacts, and the data snapshot it used.
- Write a model card: intended use, training data, known limitations, and out-of-scope uses.

## 4. Evaluate for the decision

- Report metrics that match the cost structure: precision/recall at an operating threshold,
  calibration, or ranking metrics. Accuracy alone is rarely enough.
- Slice metrics by the segments that matter (region, device, customer tier, language) and
  report the worst slice, not only the average.
- Compare against the baseline with confidence intervals, not a single number.
- For generative systems, evaluate on a fixed task set with rubric-based or reference-based
  scoring, and track regressions on known hard cases.

## 5. Define acceptance gates

Write the gates before looking at the final test score:

- Offline: minimum metric on the held-out set, no slice below a floor, calibration within tolerance.
- Robustness: behavior on missing features, out-of-range inputs, and adversarial-style inputs.
- Operational: latency and memory within the serving budget; cost per prediction recorded.
- Fairness or policy checks where the decision affects people.

## 6. Deploy with a safe path

- Serve the model behind the same interface as the baseline so it can be switched back.
- Roll out in stages: shadow mode, then a small percentage, then full traffic, each with a
  go/no-go check on live metrics.
- Keep the previous model artifact available for instant rollback.

## 7. Monitor after deploy

- **Input drift**: distribution of features compared to training data.
- **Prediction drift**: distribution of outputs over time.
- **Performance**: ground-truth metrics as labels arrive, with the label delay accounted for.
- **System health**: latency, errors, and timeouts.
- Set alert thresholds and a retraining trigger, and record each retrain as a new versioned model.

## Checklist

- [ ] Baseline score recorded; model beats it on the chosen metric with uncertainty stated.
- [ ] Split respects the production unit and time order.
- [ ] Run is reproducible from logged configuration and data version.
- [ ] Worst-slice performance meets the floor.
- [ ] Rollout plan and rollback artifact exist.
- [ ] Drift and performance monitors are live before launch.

## Anti-patterns

- Random splits on user-level or time-series data.
- Tuning thresholds on the test set.
- Reporting a single aggregate metric with no slices.
- Deploying without a baseline to compare against in production.
- Retraining on new data without checking whether the labels changed meaning.
