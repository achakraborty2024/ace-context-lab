"""Render exact pilot data; optional matplotlib dependency."""
import base64
import html
import json
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=Path(sys.argv[1] if len(sys.argv)>1 else 'results/pilot')
rows=json.loads((p/'summary.json').read_text())
manifest=json.loads((p/'manifest.json').read_text())
nseeds=len(manifest['seeds']); steps=manifest['steps']
decisions=nseeds*steps*len(manifest['scenarios'])*len(manifest['modes'])
simulated=manifest['backend']=='deterministic-simulation'
scenarios=list(dict.fromkeys(r['scenario'] for r in rows))
modes=list(dict.fromkeys(r['mode'] for r in rows))
colors=['#64748b','#9f1239','#c0840a','#8b5cf6','#0284c7','#059669']
fig,axes=plt.subplots(1,2,figsize=(13,5.5))
for j,metric in enumerate(('utility','unsafe')):
    for i,mode in enumerate(modes):
        vals=[next(r[metric] for r in rows if r['scenario']==s and r['mode']==mode) for s in scenarios]
        if metric=='unsafe': vals=[100*v for v in vals]
        axes[j].bar([x+(i-2.5)*.13 for x in range(len(scenarios))],vals,width=.125,label=mode,color=colors[i])
    axes[j].set_xticks(range(len(scenarios)),[s.replace('_','\n') for s in scenarios],fontsize=9)
    axes[j].axhline(0,color='#334155',linewidth=.6)
    axes[j].spines[['top','right']].set_visible(False)
    axes[j].set_ylabel('Mean synthetic utility' if metric=='utility' else 'Incorrect direct actions (% of all tasks)')
    axes[j].set_title('Task utility after the midpoint' if metric=='utility' else 'Operational errors after the midpoint',loc='left')
fig.suptitle('Evolving context under changing rules',x=.065,ha='left',fontsize=18,fontweight='bold')
handles,labels=axes[0].get_legend_handles_labels()
fig.legend(handles,labels,ncol=6,loc='lower center',bbox_to_anchor=(.5,.02),frameon=False)
fig.text(.065,.005,f"{manifest['backend']} • {nseeds} seeds × {steps} tasks per method/scenario",fontsize=9,color='#475569')
fig.tight_layout(rect=(0,.08,1,.92))
fig.savefig(p/'comparison.png',dpi=180)
fig.savefig(p/'comparison.svg')
plt.close(fig)
image=base64.b64encode((p/'comparison.png').read_bytes()).decode()
trs=''.join('<tr>'+''.join(f'<td>{html.escape(str(x))}</td>' for x in
    [r['scenario'],r['mode'],f"{r['utility']:.4f}",f"{100*r['unsafe']:.2f}%",f"{100*r['lookup']:.2f}%"] )+'</tr>' for r in rows)
(p/'report.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>ACE Context Lab — Pilot</title>
<style>body{font:16px/1.6 system-ui;max-width:1160px;margin:40px auto;padding:0 24px;color:#172b43;background:#f8fafc}h1{font-size:36px;line-height:1.2}p{max-width:850px}.tag{color:#047857;font-weight:700}img{width:100%;background:white;border-radius:12px}table{border-collapse:collapse;width:100%;background:white}td,th{padding:9px 12px;text-align:left;border-bottom:1px solid #e2e8f0}th{background:#e2e8f0}.box{padding:20px;border-left:4px solid #0284c7;background:#e0f2fe}footer{margin-top:30px;color:#475569}</style>
<p class="tag">REPRODUCIBLE PILOT / 15 SEPTEMBER 2026</p><h1>When yesterday's playbook<br>stops being useful</h1><p>144,000 simulated decisions across six memory policies and five scenarios. These are deterministic mechanism tests, not measured LLM performance.</p>
<div class="box"><b>The main finding:</b> Version filtering matches gated memory with clean feedback. Trust filtering helps only when feedback is marked untrusted. Unannounced policy changes still cause errors.</div>
<img alt="Utility and error rates for all six methods in all five scenarios" src="data:image/png;base64,'''+image+'''">
<h2>Exact post-midpoint results</h2><p>Utility: correct = 1; incorrect = −2; inspect = 0.7. Inspect always succeeds in this simulator. Each row averages 20 seeds and 120 post-midpoint tasks per seed.</p><table><thead><tr><th>Scenario</th><th>Mode</th><th>Utility</th><th>Errors</th><th>Lookups</th></tr></thead><tbody>'''+trs+'''</tbody></table><footer>Source: summary.json and traces.jsonl in this result directory. Full configuration and source hashes: manifest.json. Confidence intervals and paired comparisons: paired.json. The reported trust flag is a simulator assumption, not a demonstrated security classifier.</footer></html>''')
report=p/'report.html'
text=report.read_text().replace('144,000 simulated decisions',f'{decisions:,} decisions').replace('20 seeds and 120 post-midpoint tasks',f'{nseeds} seeds and {steps-steps//2} post-midpoint tasks').replace('inspect = 0.7',f"inspect = {1-manifest['lookup_cost']:.2f}")
if not simulated:
    text=text.replace('These are deterministic mechanism tests, not measured LLM performance.','External model run in a synthetic environment; inspect the model manifest and calls.')
    text=text.replace('The main finding:', 'Reference pilot finding (compare your new results):')
report.write_text(text)
print(report)
