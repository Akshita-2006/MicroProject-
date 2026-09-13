"""Report increased availability alongside conditional accuracy, without mixing populations."""
from pathlib import Path
import pandas as pd
from src.analysis.report_system import table

ROOT=Path(__file__).resolve().parents[2]


def main():
    out=ROOT/'experiments/results/combined_system'
    validation=pd.read_csv(ROOT/'experiments/results/missing_history_validation/validation_results.csv')
    scores=pd.read_csv(out/'regression_metrics.csv')
    issued=pd.read_csv(out/'issued_episode_metrics.csv')
    warnings=pd.read_csv(out/'warning_metrics.csv')
    initial=pd.read_csv(ROOT/'experiments/results/v2/issued_episode_metrics.csv').set_index('station').loc['ALL']
    current=issued.set_index('station').loc['ALL']
    tp,fp,fn,tn=[int(warnings[c].sum()) for c in ['true_positive','false_positive','false_negative','true_negative']]
    text=f'''# Missing-history fallback evaluation

The complete-history model remains unchanged. When a 73-hour calendar window contains missing past values, a separately trained XGBoost fallback uses native missing-value handling. It never fills or fabricates target values, and still abstains when current AQI is missing. Validation chooses between native missing handling with and without missingness indicators, using incomplete-history MAE at each required horizon. The nearest required horizon supplies the configuration for intermediate hours. Calibration uses missing-history July–December 2022 cases separately for each forecast hour.

## What changed and why

The prior complete-case policy excluded many otherwise usable forecast origins. Training the fallback on all training origins with observed current/target AQI allows it to learn from incomplete history. Existing complete-history forecasts are preserved, so differences in their recorded accuracy cannot be attributed to this change. Test outcomes do not choose the fallback policy.

Validation-only comparison on incomplete histories:

{table(validation[validation.subset=='incomplete'][['horizon','variant','n','mae','persistence_mae']])}

## Coverage and combined accuracy

Evaluable daily windows increased from {int(initial.eligible_windows):,} of {int(initial.scheduled_windows):,} ({initial.evaluated_fraction:.1%}) to {int(current.eligible_windows):,} of {int(current.scheduled_windows):,} ({current.evaluated_fraction:.1%}). Produced windows increased from {int(initial.produced_windows):,} to {int(current.produced_windows):,}. Remaining omitted cases include missing current observations and missing future truth. Evaluable coverage is not identical to forecast availability.

Combined retrospective test regression (a broader population than the old complete-case table):

{table(scores[scores.station=='ALL'])}

## Warnings and episode timing

Binary daily warning TP={tp}, FP={fp}, FN={fn}, TN={tn}; precision={tp/(tp+fp):.3f}, recall={tp/(tp+fn):.3f}, F1={2*tp/(2*tp+fp+fn):.3f}. These metrics concern whether any sustained episode occurs in a window.

Episode-segment matching and timing within each same-origin trajectory:

{table(issued[issued.station=='ALL'].drop(columns='station').T.reset_index().set_axis(['metric','value'],axis=1))}

Timing means remain conditional on matched segments and censoring. More complete coverage does not establish accurate event duration, an external holdout, verified pollutant alignment, or real-time validity. The test era was previously inspected. No comparison between different evaluation populations should be described as a pure accuracy improvement.

Files: experiments/results/combined_system contains combined predictions, numeric results, fixed-lead event results, daily binary warnings and same-origin episode matches. The two source populations are checked for duplicate forecast keys before combining. Each returned forecast identifies its route.
'''
    (ROOT/'reports/missing_history_fallback.md').write_text(text,encoding='utf-8')
    print('Generated missing-history coverage and evaluation report')


if __name__=='__main__':
    main()
