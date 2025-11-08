import { Job } from '../api';
import { useJobsStore } from '../../../state/jobsStore';
import { OpeningsPill } from './OpeningsPill';
import { SlaBadge } from './SlaBadge';

interface Props {
  jobs: Job[];
}

export function JobsTable({ jobs }: Props) {
  const { selectedJobId, setSelectedJobId, toggleLinkDialog } = useJobsStore();
  return (
    <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-900">
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-800 text-left text-xs uppercase tracking-wider text-slate-300">
          <tr>
            <th className="px-4 py-3">Job</th>
            <th className="px-4 py-3">Team</th>
            <th className="px-4 py-3">Priority</th>
            <th className="px-4 py-3">Headcount</th>
            <th className="px-4 py-3">Openings</th>
            <th className="px-4 py-3">Age</th>
            <th className="px-4 py-3">SLA</th>
            <th className="px-4 py-3">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 text-sm">
          {jobs.map((job) => (
            <tr
              key={job.id}
              className={`${selectedJobId === job.id ? 'bg-slate-800/60' : ''} hover:bg-slate-800/30 cursor-pointer`}
              onClick={() => setSelectedJobId(job.id)}
            >
              <td className="px-4 py-3">
                <div className="font-medium text-slate-50">{job.title}</div>
                <div className="text-xs text-slate-400">{job.hiringManager ?? '—'}</div>
              </td>
              <td className="px-4 py-3 text-slate-300">{job.team ?? '—'}</td>
              <td className="px-4 py-3">
                <span className="rounded-full bg-indigo-500/20 px-2 py-1 text-xs font-semibold text-indigo-300">
                  {job.priority}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-300">
                {job.headcountFilled}/{job.headcountRequested}
              </td>
              <td className="px-4 py-3">
                <OpeningsPill remaining={job.openingsRemaining} />
              </td>
              <td className="px-4 py-3 text-slate-300">{job.ageDays} days</td>
              <td className="px-4 py-3"><SlaBadge breach={job.slaBreach} /></td>
              <td className="px-4 py-3">
                <div className="flex gap-2">
                  <button
                    className="rounded bg-slate-700 px-2 py-1 text-xs text-slate-100"
                    onClick={(event) => {
                      event.stopPropagation();
                      toggleLinkDialog(true);
                      setSelectedJobId(job.id);
                    }}
                  >
                    Link
                  </button>
                  <button
                    className="rounded bg-indigo-600 px-2 py-1 text-xs text-white"
                    onClick={(event) => {
                      event.stopPropagation();
                      setSelectedJobId(job.id);
                    }}
                  >
                    Overview
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
