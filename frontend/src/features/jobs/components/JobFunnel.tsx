export function JobFunnel({ funnel }: { funnel: Record<string, number> }) {
  const stages = ['sourced', 'screen', 'interview', 'offer', 'hired', 'rejected'];
  return (
    <div className="mt-4 space-y-2">
      {stages.map((stage) => (
        <div key={stage} className="flex items-center justify-between text-sm text-slate-300">
          <span className="capitalize">{stage}</span>
          <div className="flex items-center gap-2">
            <div className="h-2 w-32 overflow-hidden rounded bg-slate-800">
              <div
                className="h-full bg-indigo-500"
                style={{ width: `${Math.min(100, (funnel[stage] ?? 0) * 10)}%` }}
              />
            </div>
            <span className="text-xs text-slate-400">{funnel[stage] ?? 0}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
