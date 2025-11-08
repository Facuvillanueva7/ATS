export function SlaBadge({ breach }: { breach: boolean }) {
  if (!breach) {
    return <span className="rounded-full bg-slate-700 px-2 py-1 text-xs text-slate-200">On track</span>;
  }
  return <span className="rounded-full bg-rose-500/20 px-2 py-1 text-xs font-semibold text-rose-300">SLA breach</span>;
}
