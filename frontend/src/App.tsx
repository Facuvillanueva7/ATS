import { Suspense } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import JobsPage from './pages/JobsPage';
import CandidatesPage from './pages/CandidatesPage';

function App() {
  return (
    <Layout>
      <Suspense fallback={<div className="p-8">Loading...</div>}>
        <Routes>
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/candidates" element={<CandidatesPage />} />
          <Route path="*" element={<Navigate to="/jobs" replace />} />
        </Routes>
      </Suspense>
    </Layout>
  );
}

export default App;
