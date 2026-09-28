import React from 'react';
import { motion } from 'framer-motion';
import { Watch } from 'lucide-react';
import './Loader.css';

const Loader = () => {
  return (
    <motion.div 
      className="loader-container"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0, y: -50 }}
      transition={{ duration: 0.8, ease: [0.6, 0.05, -0.01, 0.9] }}
    >
      <motion.div 
        className="loader-content"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Watch size={64} className="loader-icon" />
        </motion.div>
        <motion.h2 
          className="loader-text"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          CHRONOS
        </motion.h2>
      </motion.div>
    </motion.div>
  );
};

export default Loader;
