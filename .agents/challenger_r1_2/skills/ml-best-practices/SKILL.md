---
name: ml-best-practices
description: |
  CRITICAL RULE: You MUST use this skill whenever the task involves any machine learning tasks or data analysis.
  Use this skill if the user's prompt or requirements mention any of the following:
    * Clustering
    * Classification
    * Regression
    * Time series forecasting
    * Statistical testing
    * Model comparison
    * ML
    * Data analysis

  SQL/BigQuery ML HANDOFF: If the user requires a SQL solution, use this skill to dictate the ANALYSIS STEPS (e.g., markdown analysis cells, visualization logic), but defer to `bigquery` for all SQL syntax.
license: Apache-2.0
metadata:
  version: v1
  publisher: google
---

# ML Best Practices

I want to read a story about the data, not just run code. Ensure every code cell
is followed by a markdown cell analyzing the results. End the notebook with a
summary comprehensively answering the prompt.
