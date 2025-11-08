export function OpeningsPill({ remaining }: { remaining: number }) {
  const color = remaining > 0 ? 'bg-emerald-500/20 text-emerald-200' : 'bg-slate-700 text-slate-300';
  return <span className={`rounded-full px-2 py-1 text-xs font-semibold ${color}`}>{remaining}</span>;
}
