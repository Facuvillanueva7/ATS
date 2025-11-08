import { FormEvent } from 'react';
import { useJobsStore } from '../../../state/jobsStore';

export function FiltersPanel() {
  const { filters, setFilters } = useJobsStore();

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    setFilters({
      status: formData.get('status')?.toString() || undefined,
      priority: formData.get('priority')?.toString() || undefined,
      team: formData.get('team')?.toString() || undefined,
      owner: formData.get('owner')?.toString() || undefined,
      slaBreach: formData.get('sla') === 'on'
    });
  };

  return (
    <form onSubmit={onSubmit} className="mb-4 grid grid-cols-2 gap-4 rounded-lg border border-slate-800 bg-slate-900 p-4">
      <label className="flex flex-col text-xs uppercase tracking-wide text-slate-400">
        Status
        <select name="status" defaultValue={filters.status} className="mt-1 rounded bg-slate-800 p-2 text-sm text-slate-100">
          <option value="">All</option>
          <option value="open">Open</option>
          <option value="onhold">On Hold</option>
        </select>
      </label>
      <label className="flex flex-col text-xs uppercase tracking-wide text-slate-400">
        Priority
        <select name="priority" defaultValue={filters.priority} className="mt-1 rounded bg-slate-800 p-2 text-sm text-slate-100">
          <option value="">All</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </label>
      <label className="flex flex-col text-xs uppercase tracking-wide text-slate-400">
        Team
        <input name="team" defaultValue={filters.team} className="mt-1 rounded bg-slate-800 p-2 text-sm text-slate-100" />
      </label>
      <label className="flex flex-col text-xs uppercase tracking-wide text-slate-400">
        Owner
        <input name="owner" defaultValue={filters.owner} className="mt-1 rounded bg-slate-800 p-2 text-sm text-slate-100" />
      </label>
      <label className="flex items-center gap-2 text-xs uppercase tracking-wide text-slate-400">
        <input type="checkbox" name="sla" defaultChecked={filters.slaBreach} className="h-4 w-4" /> SLA Breach
      </label>
      <div className="flex justify-end">
        <button type="submit" className="rounded bg-indigo-500 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-400">
          Apply
        </button>
      </div>
    </form>
  );
}
