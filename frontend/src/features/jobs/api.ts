import axios from 'axios';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export type Job = {
  id: string;
  title: string;
  team?: string;
  hiringManager?: string;
  status: string;
  priority: string;
  headcountRequested: number;
  headcountFilled: number;
  openingsRemaining: number;
  ageDays: number;
  slaBreach: boolean;
};

export type JobOverview = {
  job: Job;
  funnel: Record<string, number>;
  topReasonsRejection: string[];
  avgTimeInStage: { stage: string; days: number }[];
};

export type CandidateSummary = {
  id: string;
  name: string;
  seniority?: string;
  englishLevel?: string;
  stage: string;
  score?: number;
};

const client = axios.create({ baseURL: '/api' });

export function useJobs(params: Record<string, string | undefined>) {
  return useQuery<Job[]>(['jobs', 'list', params], async () => {
    const response = await client.get<Job[]>('/jobs', { params });
    return response.data;
  }, {
    placeholderData: [
      {
        id: 'seed-job-1',
        title: 'Senior Backend Engineer',
        team: 'Platform',
        hiringManager: 'María R.',
        status: 'Open',
        priority: 'High',
        headcountRequested: 2,
        headcountFilled: 1,
        openingsRemaining: 1,
        ageDays: 32,
        slaBreach: true
      },
      {
        id: 'seed-job-2',
        title: 'Data Scientist',
        team: 'AI',
        hiringManager: 'Carlos U.',
        status: 'Open',
        priority: 'Medium',
        headcountRequested: 1,
        headcountFilled: 0,
        openingsRemaining: 1,
        ageDays: 10,
        slaBreach: false
      }
    ]
  });
}

export function useJobOverview(id: string | null) {
  return useQuery<JobOverview>(['jobs', 'overview', id], async () => {
    const response = await client.get<JobOverview>(`/jobs/${id}/overview`);
    return response.data;
  }, {
    enabled: Boolean(id),
    placeholderData: id ? {
      job: {
        id,
        title: 'Loading job',
        status: 'Open',
        priority: 'Medium',
        headcountRequested: 1,
        headcountFilled: 0,
        openingsRemaining: 1,
        ageDays: 0,
        slaBreach: false
      } as Job,
      funnel: { sourced: 12, screen: 5, interview: 3, offer: 1, hired: 0, rejected: 2 },
      topReasonsRejection: ['lack of python'],
      avgTimeInStage: [{ stage: 'screen', days: 3 }]
    } : undefined
  });
}

export function useLinkCandidate(jobId: string | null) {
  const queryClient = useQueryClient();
  return useMutation(async (candidateId: string) => {
    if (!jobId) throw new Error('jobId required');
    await client.post(`/jobs/${jobId}/candidates/link`, { candidateId });
  }, {
    onSuccess: () => {
      queryClient.invalidateQueries(['jobs', 'overview', jobId ?? '']);
    }
  });
}
