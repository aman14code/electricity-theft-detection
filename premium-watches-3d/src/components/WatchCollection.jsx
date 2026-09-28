import React from 'react';
import { motion } from 'framer-motion';
import Tilt from 'react-parallax-tilt';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { watches } from '../data/watches';
import './WatchCollection.css';

const cardVariants = {
  hidden: { opacity: 0, y: 50 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.2,
      duration: 0.8,
      ease: [0.16, 1, 0.3, 1]
    }
  })
};

const WatchCollection = () => {
  return (
    <section className="collection-section" id="collection">
      <div className="container">
        <div className="section-header">
          <motion.h2
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8 }}
          >
            The <span className="text-gradient-gold">Masterpieces</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.8 }}
          >
            Explore our curated selection of horological marvels.
          </motion.p>
        </div>

        <div className="collection-grid">
          {watches.map((watch, i) => (
            <motion.div
              key={watch.id}
              custom={i}
              variants={cardVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
            >
              <Link to={`/watch/${watch.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                <Tilt 
                  tiltMaxAngleX={10} 
                  tiltMaxAngleY={10} 
                  scale={1.02} 
                  transitionSpeed={2500}
                  className="watch-card glass"
                >
                  <div className="card-tag">{watch.tag}</div>
                  <div className="card-image-wrapper">
                    <img src={watch.image} alt={watch.name} className="card-image" />
                  </div>
                  <div className="card-info">
                    <h3>{watch.name}</h3>
                    <p className="price">{watch.price}</p>
                    <button className="btn-outline flex-center gap-2 card-btn">
                      View Details <ArrowRight size={16} />
                    </button>
                  </div>
                </Tilt>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default WatchCollection;
