import React from 'react';
import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';

const Heritage = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8 }}
      style={{ paddingTop: '80px', minHeight: '100vh' }}
    >
      <div 
        style={{ 
          height: '60vh', 
          background: 'linear-gradient(to bottom, rgba(5,5,5,0.2), var(--bg-dark)), url("/watch_black_gold.png") center/cover',
          backgroundAttachment: 'fixed',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center'
        }}
      >
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 1 }}
          className="glass"
          style={{ padding: '3rem', borderRadius: '24px', maxWidth: '600px' }}
        >
          <Clock size={48} color="var(--gold)" style={{ marginBottom: '1.5rem' }} />
          <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>Our Heritage</h1>
          <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)' }}>A century of uncompromising excellence.</p>
        </motion.div>
      </div>

      <div className="container" style={{ padding: '6rem 2rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center' }}>
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.8 }}
        >
          <h2 style={{ marginBottom: '2rem' }}>Forged in <span className="text-gradient-gold">Tradition</span></h2>
          <p style={{ marginBottom: '1.5rem' }}>Since 1926, Chronos has been at the forefront of horological innovation. What began as a small atelier in the Swiss Alps has grown into a global symbol of prestige and precision.</p>
          <p>Every timepiece is a testament to our master watchmakers, who pour hundreds of hours into finishing each movement by hand, ensuring that a Chronos watch is not just a tool for telling time, but a masterpiece meant to be passed down through generations.</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.8 }}
        >
          <img src="/watch_rose_gold.png" alt="Heritage Movement" style={{ width: '100%', borderRadius: '24px', filter: 'brightness(0.8)' }} />
        </motion.div>
      </div>
    </motion.div>
  );
};

export default Heritage;
