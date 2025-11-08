const suggestions = [
  { id: 'sug-1', name: 'Mariana Gómez', score: 0.82, mustHave: ['Python', 'Azure'], gaps: ['Leadership'] },
  { id: 'sug-2', name: 'Pedro Diaz', score: 0.74, mustHave: ['SQL', 'ETL'], gaps: ['English B2'] }
];

export function SuggestedCandidatesPanel() {
  return (
    <section className="mt-6 rounded-lg border border-slate-800 bg-slate-900 p-4">
      <header className="mb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">Suggested by AI</h3>
          <p className="text-xs text-slate-400">Embeddings + predictive ranking</p>
        </div>
        <button className="rounded bg-indigo-600 px-3 py-1 text-xs text-white">Add all to shortlist</button>
      </header>
      <ul className="space-y-3">
        {suggestions.map((candidate) => (
          <li key={candidate.id} className="rounded border border-slate-800 bg-slate-800/40 p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-semibold text-slate-100">{candidate.name}</div>
                <div className="text-xs text-slate-400">Score {Math.round(candidate.score * 100)}%</div>
              </div>
              <button className="rounded bg-slate-700 px-2 py-1 text-xs text-slate-200">Add to shortlist</button>
            </div>
            <div className="mt-2 text-xs text-slate-400">
              Must-have: {candidate.mustHave.join(', ')} | Gaps: {candidate.gaps.join(', ')}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
