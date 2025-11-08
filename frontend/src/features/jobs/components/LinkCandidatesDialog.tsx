import { FormEvent, useState } from 'react';
import { useLinkCandidate } from '../api';
import { useJobsStore } from '../../../state/jobsStore';

const sampleCandidates = [
  { id: 'cand-1', name: 'Ana Ruiz', seniority: 'Senior', englishLevel: 'C1', skills: ['Python', 'Azure'] },
  { id: 'cand-2', name: 'Luis Fernández', seniority: 'Mid', englishLevel: 'B2', skills: ['React', 'Node'] },
];

export function LinkCandidatesDialog() {
  const { selectedJobId, linkDialogOpen, toggleLinkDialog } = useJobsStore();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const linkMutation = useLinkCandidate(selectedJobId);

  if (!linkDialogOpen) return null;

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    for (const id of selectedIds) {
      await linkMutation.mutateAsync(id);
    }
    setSelectedIds([]);
    toggleLinkDialog(false);
  };

  const toggle = (id: string) => {
    setSelectedIds((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id]
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <form onSubmit={onSubmit} className="w-[420px] rounded-lg bg-slate-900 p-6 shadow-xl">
        <h2 className="text-lg font-semibold text-slate-100">Link candidates</h2>
        <p className="mt-1 text-sm text-slate-400">Select candidates to link to the job.</p>
        <div className="mt-4 space-y-3">
          {sampleCandidates.map((candidate) => (
            <label key={candidate.id} className="flex cursor-pointer items-start gap-3 rounded border border-slate-800 bg-slate-800/40 p-3">
              <input
                type="checkbox"
                checked={selectedIds.includes(candidate.id)}
                onChange={() => toggle(candidate.id)}
              />
              <div>
                <div className="text-sm font-semibold text-slate-100">{candidate.name}</div>
                <div className="text-xs text-slate-400">
                  {candidate.seniority} • English {candidate.englishLevel} • {candidate.skills.join(', ')}
                </div>
              </div>
            </label>
          ))}
        </div>
        <div className="mt-6 flex justify-end gap-2">
          <button type="button" className="rounded bg-slate-700 px-3 py-2 text-sm" onClick={() => toggleLinkDialog(false)}>
            Cancel
          </button>
          <button type="submit" className="rounded bg-indigo-600 px-3 py-2 text-sm text-white" disabled={linkMutation.isLoading}>
            Link selected
          </button>
        </div>
      </form>
    </div>
  );
}
