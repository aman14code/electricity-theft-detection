import React from 'react';
import { motion } from 'framer-motion';
import WatchCollection from '../components/WatchCollection';

const CollectionPage = () => {
  return (
    <motion.div
      initial={{ opacity: 0, x: 100 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -100 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      style={{ paddingTop: '80px' }}
    >
      <div className="container" style={{ textAlign: 'center', margin: '4rem auto 0' }}>
        <h1 className="text-gradient-gold">Full Collection</h1>
        <p style={{ marginTop: '1rem' }}>Discover every piece from our master watchmakers.</p>
      </div>
      <WatchCollection />
    </motion.div>
  );
};

export default CollectionPage;
