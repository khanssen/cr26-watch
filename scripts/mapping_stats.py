"""Structural properties of the KSI -> SP 800-53 mapping for a CR26 version.
Usage: python scripts/mapping_stats.py [path.json] [--baseline moderate-ids.txt] [--out report.md]
  --out writes UTF-8 directly (use it on Windows PowerShell 5.1, where `>` writes UTF-16).
"""
import sys, collections
from common import load, ksis, frr_rules, norm_ctrl, version, utf8_stdout

ALL_FAMS = ["ac","at","au","ca","cm","cp","ia","ir","ma","mp","pe","pl","pm","ps","pt","ra","sa","sc","si","sr"]

def main(argv):
    path = next((a for a in argv if a.endswith(".json")), None)
    base = None
    if "--baseline" in argv:
        base = {norm_ctrl(l) for l in open(argv[argv.index("--baseline")+1], encoding="utf-8-sig") if l.strip()}
    doc = load(path)
    c2k = collections.defaultdict(list); k2n = {}
    for kid, theme, ind in ksis(doc):
        cs = [norm_ctrl(c) for c in ind.get("controls", [])]
        k2n[kid] = len(cs)
        for c in cs: c2k[c].append(kid)
    fams = collections.Counter(c.split("-")[0] for c in c2k)
    enh = sum(1 for c in c2k if "." in c)
    multi = {c: k for c, k in c2k.items() if len(k) > 1}
    ctl = doc.get("CTL", {})
    n_ctl = sum(len(f) for f in ctl.values())
    n_par = sum(len(b.get("parameters", [])) for f in ctl.values() for b in f.values())
    n_vpar = sum(len(cls.get("parameters", [])) for f in ctl.values() for b in f.values()
                 for cls in b.get("varies_by_class", {}).values())
    print(f"# KSI -> SP 800-53 mapping stats, CR26 {version(doc)}\n")
    print(f"- KSIs: {len(k2n)}; unmapped KSIs: {[k for k,n in k2n.items() if n==0]}")
    print(f"- Distinct control ids: {len(c2k)} ({len(c2k)-enh} base + {enh} enhancements) across {len(fams)} families")
    print(f"- Families absent: {[f.upper() for f in ALL_FAMS if f not in fams]}")
    print(f"- Fan-out per KSI: min {min(k2n.values())} / median {sorted(k2n.values())[len(k2n)//2]} / max {max(k2n.values())}")
    print(f"- Controls mapped from >1 KSI: {len(multi)} of {len(c2k)}; max fan-in {max(len(k) for k in c2k.values())}")
    print(f"- CTL: {n_ctl} control entries; {n_par} uniform parameter values; {n_vpar} class-varying values")
    if base:
        cov = base & set(c2k)
        print(f"- Baseline coverage: {len(cov)} of {len(base)} ids touched ({100*len(cov)/len(base):.0f}%)")
    bsl = next((r for rid, *_ , r in frr_rules(doc) if rid == "FRC-CSF-BSL"), None)
    if bsl:
        print("\n## KSI reference coverage of the CR26 Rev5 baselines (FRC-CSF-BSL)\n")
        print("| Class | Baseline ids | Referenced by any KSI | No KSI reference | Families with none |")
        print("|---|---|---|---|---|")
        prev = None
        for cls, cb in sorted(bsl.get("varies_by_class", {}).items()):
            sel = {norm_ctrl(x) for fam in cb.get("rev5_controls_list", {}).values() for x in fam}
            hit = sel & set(c2k)
            none_fams = sorted({c.split("-")[0].upper() for c in sel} - {c.split("-")[0].upper() for c in hit})
            print(f"| {cls.upper()} | {len(sel)} | {len(hit)} ({100*len(hit)/len(sel):.1f}%) | {len(sel)-len(hit)} | {', '.join(none_fams) or '-'} |")
            if prev is not None and prev[1] <= sel:
                inc = sel - prev[1]
                print(f"|  | +{len(inc)} over {prev[0].upper()} | {len(inc & set(c2k))} of the increment | {len(inc - set(c2k))} of the increment | |")
            prev = (cls, sel)
        allsel = set().union(*({norm_ctrl(x) for fam in cb.get("rev5_controls_list", {}).values() for x in fam}
                              for cb in bsl.get("varies_by_class", {}).values()))
        outside = sorted(set(c2k) - allsel)
        print(f"\n- KSI-referenced ids in no Rev5 baseline: {len(outside)} ({', '.join(outside)})")
    print("\n## Top fan-in controls")
    for c, k in sorted(c2k.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"- {c}: {len(k)} -> {', '.join(k)}")
    print("\n## Fan-out per KSI")
    for k, n in sorted(k2n.items(), key=lambda x: -x[1]):
        print(f"- {k}: {n}")

def _run(argv):
    utf8_stdout()
    if "--out" in argv:
        i = argv.index("--out"); out = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            real, sys.stdout = sys.stdout, f
            try: main(argv)
            finally: sys.stdout = real
        print(f"wrote {out}")
    else:
        main(argv)

if __name__ == "__main__":
    _run(sys.argv[1:])
