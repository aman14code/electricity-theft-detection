import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Navbar from './components/Navbar';
import Loader from './components/Loader';

// Pages
import Home from './pages/Home';
import CollectionPage from './pages/CollectionPage';
import Heritage from './pages/Heritage';
import WatchDetails from './pages/WatchDetails';

function App() {
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <>
      <AnimatePresence>
        {loading && <Loader />}
      </AnimatePresence>
      
      {!loading && (
        <>
          <Navbar />
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route path="/" element={<Home />} />
              <Route path="/collection" element={<CollectionPage />} />
              <Route path="/heritage" element={<Heritage />} />
              <Route path="/watch/:id" element={<WatchDetails />} />
            </Routes>
          </AnimatePresence>
        </>
      )}
    </>
  );
}

export default App;
