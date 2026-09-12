import {lazy, Suspense, useEffect, useState} from 'react';
import LandingPage from './components/LandingPage';

const NetworkWorkspace = lazy(() => import('./components/NetworkWorkspace'));

export default function App() {
  const [inWorkspace, setInWorkspace] = useState(() => window.location.hash === '#/app');
  useEffect(() => {
    const navigate = () => {
      const next = window.location.hash === '#/app';
      setInWorkspace(next);
      if (next) window.scrollTo(0, 0);
    };
    window.addEventListener('hashchange', navigate);
    return () => window.removeEventListener('hashchange', navigate);
  }, []);
  return inWorkspace
    ? <Suspense fallback={<div role="status" style={{padding:32}}>Opening Network Intel…</div>}><NetworkWorkspace /></Suspense>
    : <LandingPage />;
}
