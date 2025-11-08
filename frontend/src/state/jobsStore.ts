import { create } from 'zustand';

type Filters = {
  status?: string;
  priority?: string;
  team?: string;
  owner?: string;
  slaBreach?: boolean;
};

type JobsState = {
  selectedJobId: string | null;
  filters: Filters;
  linkDialogOpen: boolean;
  setSelectedJobId: (id: string | null) => void;
  setFilters: (filters: Filters) => void;
  toggleLinkDialog: (open: boolean) => void;
};

export const useJobsStore = create<JobsState>((set) => ({
  selectedJobId: null,
  filters: {},
  linkDialogOpen: false,
  setSelectedJobId: (id) => set({ selectedJobId: id }),
  setFilters: (filters) => set({ filters }),
  toggleLinkDialog: (open) => set({ linkDialogOpen: open })
}));
