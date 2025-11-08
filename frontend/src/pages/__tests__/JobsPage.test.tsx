import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import JobsPage from '../JobsPage';
import { useJobsStore } from '../../state/jobsStore';

vi.mock('../../features/jobs/api', () => ({
  useJobs: () => ({ data: [
    {
      id: 'job-1',
      title: 'Backend Engineer',
      team: 'Platform',
      hiringManager: 'Ana',
      status: 'Open',
      priority: 'High',
      headcountRequested: 2,
      headcountFilled: 1,
      openingsRemaining: 1,
      ageDays: 20,
      slaBreach: false
    }
  ] })
}));

const renderPage = () => {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <JobsPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('JobsPage', () => {
  it('renders jobs table with data', () => {
    renderPage();
    expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
  });

  it('opens link dialog when clicking link', () => {
    renderPage();
    fireEvent.click(screen.getByText('Link'));
    expect(screen.getByText('Link candidates')).toBeInTheDocument();
  });

  it('applies filters', () => {
    renderPage();
    fireEvent.change(screen.getByLabelText('Status'), { target: { value: 'open' } });
    fireEvent.submit(screen.getByText('Apply').closest('form')!);
    expect(useJobsStore.getState().filters.status).toBe('open');
  });
});
