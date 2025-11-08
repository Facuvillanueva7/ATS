const mockCandidates = [
  { id: 'cand-1', name: 'Ana Ruiz', seniority: 'Senior', english: 'C1', lastStage: 'Interview' },
  { id: 'cand-2', name: 'Luis Fernández', seniority: 'Mid', english: 'B2', lastStage: 'Screen' }
];

function CandidatesPage() {
  return (
    <div>
      <h2 className="text-lg font-semibold text-slate-100">Candidates</h2>
      <p className="text-sm text-slate-400">Track profiles, scores and applications.</p>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {mockCandidates.map((candidate) => (
          <article key={candidate.id} className="rounded-lg border border-slate-800 bg-slate-900 p-4">
            <header className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-slate-100">{candidate.name}</h3>
              <span className="rounded-full bg-indigo-500/20 px-2 py-1 text-xs text-indigo-200">{candidate.seniority}</span>
            </header>
            <p className="mt-2 text-sm text-slate-300">English {candidate.english}</p>
            <p className="text-xs text-slate-400">Last stage: {candidate.lastStage}</p>
            <button className="mt-4 rounded bg-slate-700 px-3 py-2 text-sm text-slate-100">View profile</button>
          </article>
        ))}
      </div>
    </div>
  );
}

export default CandidatesPage;
