import { FiltersPanel } from '../features/jobs/components/FiltersPanel';
import { JobsTable } from '../features/jobs/components/JobsTable';
import { JobOverviewDrawer } from '../features/jobs/components/JobOverviewDrawer';
import { LinkCandidatesDialog } from '../features/jobs/components/LinkCandidatesDialog';
import { SuggestedCandidatesPanel } from '../features/jobs/components/SuggestedCandidatesPanel';
import { useJobsStore } from '../state/jobsStore';
import { useJobs } from '../features/jobs/api';

function JobsPage() {
  const { filters } = useJobsStore();
  const { data: jobs } = useJobs({
    status: filters.status,
    priority: filters.priority,
    team: filters.team,
    owner: filters.owner,
    slaBreach: filters.slaBreach ? 'true' : undefined
  });

  return (
    <div className="relative">
      <h2 className="text-lg font-semibold text-slate-100">Jobs Admin</h2>
      <p className="text-sm text-slate-400">Control headcount, SLA and candidate linking in one board.</p>
      <FiltersPanel />
      <JobsTable jobs={jobs ?? []} />
      <SuggestedCandidatesPanel />
      <JobOverviewDrawer />
      <LinkCandidatesDialog />
    </div>
  );
}

export default JobsPage;
