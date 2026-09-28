import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Tilt from 'react-parallax-tilt';
import { ArrowLeft, ShoppingBag } from 'lucide-react';
import { watches } from '../data/watches';

const WatchDetails = () => {
  const { id } = useParams();
  const watch = watches.find(w => w.id === parseInt(id));

  if (!watch) {
    return <div className="container" style={{ paddingTop: '120px' }}>Watch not found</div>;
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 1.05 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="container"
      style={{ paddingTop: '120px', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}
    >
      <Link to="/collection" style={{ color: 'var(--text-secondary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem', width: 'fit-content' }}>
        <ArrowLeft size={20} /> Back to Collection
      </Link>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center' }}>
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.8 }}
        >
          <Tilt tiltMaxAngleX={15} tiltMaxAngleY={15} perspective={1000} scale={1.05} transitionSpeed={2000}>
            <img src={watch.image} alt={watch.name} style={{ width: '100%', maxWidth: '500px', filter: 'drop-shadow(0 30px 40px rgba(0,0,0,0.8))' }} />
          </Tilt>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}
        >
          <div>
            <div style={{ color: 'var(--gold)', letterSpacing: '2px', fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.5rem' }}>{watch.tag}</div>
            <h1 style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>{watch.name}</h1>
            <p style={{ fontSize: '2rem', color: 'var(--text-primary)', fontWeight: 500 }}>{watch.price}</p>
          </div>
          
          <p style={{ fontSize: '1.1rem', lineHeight: 1.8 }}>{watch.description}</p>
          
          <div className="glass" style={{ padding: '2rem', borderRadius: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            {Object.entries(watch.specs).map(([key, value]) => (
              <div key={key}>
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', textTransform: 'uppercase', marginBottom: '0.3rem' }}>{key.replace(/([A-Z])/g, ' $1').trim()}</div>
                <div style={{ fontWeight: 500 }}>{value}</div>
              </div>
            ))}
          </div>

          <button className="btn-primary flex-center gap-2" style={{ alignSelf: 'flex-start', marginTop: '1rem' }}>
            <ShoppingBag size={20} /> Add to Cart
          </button>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default WatchDetails;
