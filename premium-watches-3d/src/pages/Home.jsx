import React from 'react';
import { motion } from 'framer-motion';
import Hero from '../components/Hero';
import WatchCollection from '../components/WatchCollection';

const Home = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.5 }}
    >
      <Hero />
      <WatchCollection />
    </motion.div>
  );
};

export default Home;
