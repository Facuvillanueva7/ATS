import { useEffect } from 'react';
import { useJobOverview } from '../api';
import { useJobsStore } from '../../../state/jobsStore';
import { JobFunnel } from './JobFunnel';

export function JobOverviewDrawer() {
  const { selectedJobId, setSelectedJobId } = useJobsStore();
  const { data } = useJobOverview(selectedJobId);

  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setSelectedJobId(null);
      }
    };
    window.addEventListener('keydown', listener);
    return () => window.removeEventListener('keydown', listener);
  }, [setSelectedJobId]);

  if (!selectedJobId || !data) return null;

  return (
    <aside className="fixed right-0 top-0 h-full w-[400px] border-l border-slate-800 bg-slate-900/95 p-6 shadow-xl">
      <div className="flex items-start justify-between">
        <h2 className="text-lg font-semibold text-slate-100">{data.job.title}</h2>
        <button onClick={() => setSelectedJobId(null)} className="text-slate-400 hover:text-slate-100">✕</button>
      </div>
      <p className="mt-2 text-sm text-slate-300">Openings remaining: {data.job.openingsRemaining}</p>
      <p className="text-sm text-slate-300">Age: {data.job.ageDays} days</p>
      <JobFunnel funnel={data.funnel} />
      <div className="mt-4">
        <h3 className="text-sm font-semibold text-slate-200">Top rejection reasons</h3>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-400">
          {data.topReasonsRejection.length === 0 && <li>No data yet</li>}
          {data.topReasonsRejection.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
