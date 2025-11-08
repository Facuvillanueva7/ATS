import { ReactNode } from 'react';
import { NavLink } from 'react-router-dom';

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-slate-600 text-white' : 'text-slate-200 hover:bg-slate-700'}`;

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <h1 className="text-xl font-semibold tracking-tight">Orion ATS</h1>
          <nav className="flex gap-2">
            <NavLink to="/jobs" className={navLinkClass}>
              Jobs Admin
            </NavLink>
            <NavLink to="/candidates" className={navLinkClass}>
              Candidates
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-6">{children}</main>
    </div>
  );
}
