#!/usr/bin/env python3
"""
Generate real per-machine anomaly analysis by replaying each machine's raw
SMD telemetry through the same BaselineCalculator + AnomalyDetector used by
the live Machine Analyzer dashboard (machine_analyzer.py). This is genuine
computation over that machine's actual data -- not the static demo charts
in analysis_visualizations.py.

Outputs, per machine, to data/processed/per_machine/<machine-name>/:
  - anomaly_timeline.png      anomaly score across the full replay
  - threshold_sensitivity.png % of readings flagged across a threshold sweep
                               (unsupervised -- NOT a confusion matrix)
  - incident_log.json/.csv    every fault actually triggered by detect_faults()
  - summary.json              run metadata + severity/fault-type breakdown
  - summary_dashboard.png     visual rendering of summary.json (stat cards,
                               severity donut, top fault types, top actions)
  - incident_insights.md      incident_log.json distilled into actionable,
                               readable insights (top faults, prioritized
                               recommendations, incident clusters). The raw
                               JSON/CSV logs are kept unchanged alongside it.

Deliberately NOT generated here: confusion matrices, classification
precision/recall/F1, DoS simulation, chaos simulation, remediation results.
No ground-truth labels exist for this dataset and no remediation engine
exists in machine_analyzer.py, so those stay as the existing global static
reports in analysis_visualizations.py rather than being fabricated per machine.
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

from machine_analyzer import BaselineCalculator, AnomalyDetector

SEVERITY_ORDER = ['critical', 'high', 'medium', 'low']
SEVERITY_COLORS = {
    'critical': '#ff006e',
    'high': '#ffbe0b',
    'medium': '#00d9ff',
    'low': '#00ff41',
}
SEVERITY_RANK = {s: i for i, s in enumerate(SEVERITY_ORDER)}

plt.style.use('dark_background')

SMD_DIR = Path(__file__).parent / 'data' / 'raw' / 'smd'
OUTPUT_DIR = Path(__file__).parent / 'data' / 'processed' / 'per_machine'

PANEL_BG = '#0f1729'
FIG_BG = '#0a0e27'


def replay_machine(machine_name, threshold=0.52, window_size=100):
    """Replay a machine's raw file through the real, unsupervised detection
    pipeline. Returns (scores, incidents)."""
    path = SMD_DIR / f'{machine_name}.txt'
    baseline_calc = BaselineCalculator(window_size=window_size)
    detector = AnomalyDetector(baseline_calc)
    detector.anomaly_threshold = threshold

    scores = []
    incidents = []

    with open(path, 'r') as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader):
            features = [float(x) for x in row]
            score, _ = detector.calculate_anomaly_score(features)
            scores.append(score)

            if score > threshold:
                faults = detector.detect_faults(features, score)
                for fault_id, name, severity, affected, recommendations in faults:
                    incidents.append({
                        'row': row_idx,
                        'anomaly_score': round(score, 4),
                        'fault_id': fault_id,
                        'fault_name': name,
                        'severity': severity,
                        'affected_features': affected,
                        'recommendations': [r['action'] for r in recommendations],
                    })

    return scores, incidents


def sweep_thresholds(scores, thresholds=None):
    """Unsupervised threshold sensitivity: fraction of readings flagged at
    each threshold. No ground truth is used -- this is not precision/recall."""
    if thresholds is None:
        thresholds = np.arange(0.30, 0.85, 0.05)
    scores_arr = np.array(scores)
    flagged_pct = [(scores_arr > t).mean() * 100 for t in thresholds]
    return thresholds, flagged_pct


def _style_axes(ax):
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors='#cccccc')
    ax.grid(alpha=0.15)
    for spine in ('top', 'right'):
        ax.spines[spine].set_visible(False)
    for spine in ('bottom', 'left'):
        ax.spines[spine].set_color('#444')


def generate_timeline_chart(machine_name, scores, threshold, output_path):
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(FIG_BG)
    _style_axes(ax)

    scores_arr = np.array(scores)
    x = np.arange(len(scores_arr))
    ax.plot(x, scores_arr, color='#00d9ff', linewidth=0.5, alpha=0.7, zorder=2)
    ax.axhline(threshold, color='#ff006e', linestyle='--', linewidth=1.2,
               label=f'Anomaly threshold ({threshold})', zorder=3)

    above = scores_arr > threshold
    if above.any():
        ax.scatter(x[above], scores_arr[above], color='#ff006e', s=14,
                   zorder=4, label=f'Incidents triggered ({int(above.sum())})')

    ax.set_title(f'{machine_name} — Anomaly Score Timeline (real replay, {len(scores_arr)} readings)',
                 fontsize=13, fontweight='bold', color='white', pad=12)
    ax.set_xlabel('Reading index', color='#cccccc')
    ax.set_ylabel('Anomaly Score', color='#cccccc')
    ax.set_ylim(0, 1)
    ax.legend(loc='upper right', frameon=False, labelcolor='#cccccc')

    fig.tight_layout()
    fig.savefig(output_path, dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


def generate_threshold_chart(machine_name, thresholds, flagged_pct, current_threshold, output_path):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(FIG_BG)
    _style_axes(ax)

    ax.plot(thresholds, flagged_pct, 'o-', color='#00ff41', linewidth=2, markersize=5)
    ax.axvline(current_threshold, color='#ffbe0b', linestyle='--', linewidth=1.2,
               label=f'Configured threshold ({current_threshold})')

    ax.set_title(f'{machine_name} — Threshold Sensitivity (unsupervised, no ground truth)',
                 fontsize=13, fontweight='bold', color='white', pad=12)
    ax.set_xlabel('Anomaly Threshold', color='#cccccc')
    ax.set_ylabel('% of Readings Flagged', color='#cccccc')
    ax.legend(loc='upper right', frameon=False, labelcolor='#cccccc')

    fig.tight_layout()
    fig.savefig(output_path, dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


def write_incident_log(incidents, out_dir):
    with open(out_dir / 'incident_log.json', 'w') as f:
        json.dump(incidents, f, indent=2)

    with open(out_dir / 'incident_log.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'anomaly_score', 'fault_id', 'fault_name', 'severity',
                          'affected_features', 'recommendations'])
        for inc in incidents:
            writer.writerow([
                inc['row'], inc['anomaly_score'], inc['fault_id'], inc['fault_name'],
                inc['severity'], ';'.join(inc['affected_features']),
                ';'.join(inc['recommendations'])
            ])


def summarize_incidents(incidents):
    """Aggregate the raw incident list into actionable insights: which
    faults happened most, which recommendations matter most, and where
    incidents clustered in time. Pure aggregation of real data -- no new
    facts are invented."""
    fault_counts = {}
    severity_counts = {}
    recommendation_counts = {}

    for inc in incidents:
        entry = fault_counts.setdefault(inc['fault_name'], {
            'count': 0, 'severity': inc['severity'], 'fault_id': inc['fault_id']
        })
        entry['count'] += 1
        severity_counts[inc['severity']] = severity_counts.get(inc['severity'], 0) + 1
        for rec in inc['recommendations']:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1

    top_faults = sorted(
        fault_counts.items(),
        key=lambda kv: (-kv[1]['count'], SEVERITY_RANK.get(kv[1]['severity'], 9))
    )
    top_recommendations = sorted(recommendation_counts.items(), key=lambda kv: -kv[1])

    # Group incident rows into contiguous bursts (gap tolerance = 50 readings)
    clusters = []
    if incidents:
        rows = sorted(set(inc['row'] for inc in incidents))
        cluster_start = prev = rows[0]
        for r in rows[1:]:
            if r - prev > 50:
                clusters.append((cluster_start, prev))
                cluster_start = r
            prev = r
        clusters.append((cluster_start, prev))

    return {
        'severity_counts': severity_counts,
        'top_faults': top_faults,
        'top_recommendations': top_recommendations,
        'clusters': clusters,
    }


def generate_summary_dashboard(machine_name, summary, insights, output_path):
    """Visual rendering of summary.json (+ the fault/recommendation
    breakdown derived from incident_log.json) for one machine."""
    fig = plt.figure(figsize=(11, 8))
    fig.patch.set_facecolor(FIG_BG)
    gs = fig.add_gridspec(3, 3, height_ratios=[0.55, 1.3, 1.15], hspace=0.75, wspace=0.5,
                          left=0.07, right=0.96, top=0.88, bottom=0.07)

    fig.suptitle(f'{machine_name} — Analysis Summary', fontsize=18, fontweight='bold',
                color='#00ff41', y=0.965)
    fig.text(0.5, 0.915,
             f"{summary['readings_analyzed']:,} readings analyzed  |  "
             f"threshold {summary['anomaly_threshold']}  |  "
             f"generated {summary['generated_at'][:16].replace('T', ' ')}",
             ha='center', fontsize=9, color='#8899aa')

    stat_cards = [
        ('INCIDENTS TRIGGERED', str(summary['total_incidents_triggered']), '#ff006e'),
        ('AVG ANOMALY SCORE', f"{summary['avg_anomaly_score']:.3f}", '#00d9ff'),
        ('MAX ANOMALY SCORE', f"{summary['max_anomaly_score']:.3f}", '#ffbe0b'),
    ]
    for idx, (label, value, color) in enumerate(stat_cards):
        ax = fig.add_subplot(gs[0, idx])
        ax.axis('off')
        box = FancyBboxPatch((0.03, 0.05), 0.94, 0.9,
                             boxstyle="round,pad=0.02,rounding_size=0.08",
                             linewidth=1.5, edgecolor=color, facecolor=PANEL_BG,
                             transform=ax.transAxes)
        ax.add_patch(box)
        ax.text(0.5, 0.6, value, ha='center', va='center', fontsize=17,
                fontweight='bold', color=color, transform=ax.transAxes)
        ax.text(0.5, 0.2, label, ha='center', va='center', fontsize=7.5,
                color='#8899aa', fontweight='bold', transform=ax.transAxes)

    # Severity donut
    ax_sev = fig.add_subplot(gs[1, 0])
    ax_sev.set_facecolor(PANEL_BG)
    counts = [summary['incidents_by_severity'].get(s, 0) for s in SEVERITY_ORDER]
    nonzero = [(s, c) for s, c in zip(SEVERITY_ORDER, counts) if c > 0]
    if nonzero:
        labels, vals = zip(*nonzero)

        def _pct_label(pct):
            # Suppress on-wedge labels for slivers to avoid overlapping text
            return f'{pct:.0f}%' if pct >= 8 else ''

        wedges, texts, autotexts = ax_sev.pie(
            vals, colors=[SEVERITY_COLORS[l] for l in labels], autopct=_pct_label,
            wedgeprops=dict(width=0.42, edgecolor=FIG_BG, linewidth=1.5), startangle=90,
            pctdistance=0.78
        )
        for at in autotexts:
            at.set_color('#0a0e27')
            at.set_fontweight('bold')
            at.set_fontsize(8)
        legend_labels = [f'{l} ({v})' for l, v in zip(labels, vals)]
        ax_sev.legend(legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2,
                     frameon=False, labelcolor='#cccccc', fontsize=7)
    else:
        ax_sev.text(0.5, 0.5, 'No incidents', ha='center', va='center',
                    color='#8899aa', fontsize=9, transform=ax_sev.transAxes)
    ax_sev.set_title('Severity Mix', fontsize=10.5, fontweight='bold', color='white')

    # Top fault types
    ax_fault = fig.add_subplot(gs[1, 1:3])
    ax_fault.set_facecolor(PANEL_BG)
    top6 = insights['top_faults'][:6]
    if top6:
        names = [n.replace(' ', '\n') for n, _ in top6][::-1]
        vals = [d['count'] for _, d in top6][::-1]
        bar_colors = [SEVERITY_COLORS.get(d['severity'], '#888') for _, d in top6][::-1]
        bars = ax_fault.barh(names, vals, color=bar_colors)
        for bar, v in zip(bars, vals):
            ax_fault.text(bar.get_width() + max(vals) * 0.02, bar.get_y() + bar.get_height()/2,
                          str(v), va='center', fontsize=8, color='white', fontweight='bold')
    else:
        ax_fault.text(0.5, 0.5, 'No faults triggered', ha='center', va='center',
                      color='#8899aa', fontsize=9, transform=ax_fault.transAxes)
    ax_fault.set_title('Top Fault Types', fontsize=10.5, fontweight='bold', color='white')
    ax_fault.tick_params(colors='#cccccc', labelsize=7.5)
    ax_fault.grid(axis='x', alpha=0.15)
    for spine in ('top', 'right'):
        ax_fault.spines[spine].set_visible(False)
    for spine in ('bottom', 'left'):
        ax_fault.spines[spine].set_color('#444')

    # Top recommendations (as readable text panel)
    ax_rec = fig.add_subplot(gs[2, :])
    ax_rec.axis('off')
    ax_rec.text(0, 1.0, 'Top Recommendations', fontsize=10.5, fontweight='bold',
               color='white', transform=ax_rec.transAxes, va='top')
    if insights['top_recommendations']:
        rec_lines = [f"•  {rec}   ({count}x)" for rec, count in insights['top_recommendations'][:6]]
    else:
        rec_lines = ['No incidents triggered — no recommendations to show.']
    ax_rec.text(0, 0.8, '\n'.join(rec_lines), fontsize=9, color='#cccccc',
               transform=ax_rec.transAxes, va='top', linespacing=1.8)

    fig.savefig(output_path, dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)


def write_incident_insights(machine_name, incidents, insights, summary, out_dir):
    """Human-readable Markdown summary of incident_log.json -- the raw JSON
    (and CSV) are kept unchanged alongside this for full detail/traceability."""
    lines = [f'# Incident Insights — {machine_name}', '']
    lines.append(f"Generated {summary['generated_at'][:19].replace('T', ' ')} from "
                f"{summary['readings_analyzed']:,} real telemetry readings "
                f"(threshold {summary['anomaly_threshold']}).")
    lines.append('')
    lines.append(f"**{len(incidents)} incidents triggered** across "
                f"**{len(insights['top_faults'])} distinct fault types**, "
                f"in **{len(insights['clusters'])} separate burst(s)**.")
    lines.append('')

    lines.append('## Severity Breakdown')
    lines.append('')
    if insights['severity_counts']:
        for sev in SEVERITY_ORDER:
            if sev in insights['severity_counts']:
                lines.append(f"- **{sev.title()}**: {insights['severity_counts'][sev]} incidents")
    else:
        lines.append('- No incidents triggered on this machine.')
    lines.append('')

    lines.append('## Top Fault Types')
    lines.append('')
    if insights['top_faults']:
        lines.append('| Fault Type | Severity | Occurrences |')
        lines.append('|---|---|---|')
        for name, data in insights['top_faults']:
            lines.append(f"| {name} | {data['severity'].title()} | {data['count']} |")
    else:
        lines.append('_No faults triggered._')
    lines.append('')

    lines.append('## Prioritized Recommendations')
    lines.append('')
    lines.append('Deduplicated across every triggered incident, ranked by how often each was recommended '
                 '(most-recommended actions address the most frequent faults):')
    lines.append('')
    if insights['top_recommendations']:
        for rec, count in insights['top_recommendations']:
            lines.append(f"- {rec} _(recommended {count}x)_")
    else:
        lines.append('_No recommendations — no incidents triggered._')
    lines.append('')

    if insights['clusters']:
        lines.append('## Incident Clusters (contiguous bursts)')
        lines.append('')
        lines.append('Reading ranges where incidents happened back-to-back (gap ≤ 50 readings counts as the same burst):')
        lines.append('')
        lines.append('| Start Row | End Row | Span |')
        lines.append('|---|---|---|')
        for start, end in insights['clusters']:
            lines.append(f"| {start} | {end} | {end - start + 1} readings |")
        lines.append('')

    lines.append('---')
    lines.append('_Full per-incident detail (timestamp, exact score, affected features) is in '
                 '`incident_log.json` / `incident_log.csv` alongside this file._')

    with open(out_dir / 'incident_insights.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def analyze_machine(machine_name, threshold=0.52):
    print(f'[{machine_name}] Replaying real telemetry through AnomalyDetector...')
    scores, incidents = replay_machine(machine_name, threshold=threshold)

    out_dir = OUTPUT_DIR / machine_name
    out_dir.mkdir(parents=True, exist_ok=True)

    generate_timeline_chart(machine_name, scores, threshold, out_dir / 'anomaly_timeline.png')

    thresholds, flagged_pct = sweep_thresholds(scores)
    generate_threshold_chart(machine_name, thresholds, flagged_pct, threshold,
                              out_dir / 'threshold_sensitivity.png')

    write_incident_log(incidents, out_dir)

    insights = summarize_incidents(incidents)

    severity_counts = insights['severity_counts']
    scores_arr = np.array(scores)
    summary = {
        'machine': machine_name,
        'generated_at': datetime.now().isoformat(),
        'readings_analyzed': len(scores),
        'anomaly_threshold': threshold,
        'avg_anomaly_score': round(float(scores_arr.mean()), 4),
        'max_anomaly_score': round(float(scores_arr.max()), 4),
        'readings_above_threshold': int((scores_arr > threshold).sum()),
        'total_incidents_triggered': len(incidents),
        'incidents_by_severity': severity_counts,
        'top_fault_types': [
            {'fault_name': name, 'severity': data['severity'], 'count': data['count']}
            for name, data in insights['top_faults']
        ],
        'incident_clusters': len(insights['clusters']),
        'note': ('Real replay through the live AnomalyDetector/BaselineCalculator '
                 'pipeline (unsupervised, rolling median baseline). Confusion '
                 'matrix and classification metrics are intentionally NOT '
                 'included here -- no ground-truth anomaly labels exist for '
                 'this dataset, so those numbers would be fabricated.'),
    }
    with open(out_dir / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    generate_summary_dashboard(machine_name, summary, insights, out_dir / 'summary_dashboard.png')
    write_incident_insights(machine_name, incidents, insights, summary, out_dir)

    print(f'[{machine_name}] Done: {len(scores)} readings, '
          f'{summary["readings_above_threshold"]} above threshold, '
          f'{len(incidents)} fault incidents triggered.')
    return summary


if __name__ == '__main__':
    machines = sys.argv[1:] or ['machine-1-1', 'machine-1-5', 'machine-2-3']

    results = []
    for m in machines:
        if not (SMD_DIR / f'{m}.txt').exists():
            print(f'[{m}] SKIPPED - no data file found at {SMD_DIR / (m + ".txt")}')
            continue
        results.append(analyze_machine(m))

    print('\n' + '=' * 60)
    print('SUMMARY')
    print('=' * 60)
    for r in results:
        print(f"{r['machine']}: {r['total_incidents_triggered']} incidents, "
              f"avg score {r['avg_anomaly_score']}, "
              f"{r['readings_above_threshold']}/{r['readings_analyzed']} above threshold")
