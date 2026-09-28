import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import Tilt from 'react-parallax-tilt';
import { ArrowRight, Play } from 'lucide-react';
import './Hero.css';

const Hero = () => {
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 1000], [0, 200]);
  const y2 = useTransform(scrollY, [0, 1000], [0, -150]);
  const opacity = useTransform(scrollY, [0, 500], [1, 0]);

  return (
    <section className="hero bg-gradient-radial">
      <div className="container hero-container">
        <motion.div 
          className="hero-content"
          initial={{ opacity: 0, x: -100 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
          style={{ y: y1, opacity }}
        >
          <motion.div 
            className="badge"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            2026 EXCLUSIVE COLLECTION
          </motion.div>
          
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.8 }}
          >
            Time Reimagined in <span className="text-gradient-gold">Obsidian</span>
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.8 }}
          >
            Experience the pinnacle of horology. Crafted with precision, designed for eternity. The new Chronos Series redefines luxury.
          </motion.p>
          
          <motion.div 
            className="hero-cta"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
          >
            <button className="btn-primary flex-center gap-2">
              Explore Collection <ArrowRight size={20} />
            </button>
            <button className="btn-video flex-center gap-2">
              <span className="play-icon-wrapper"><Play size={16} fill="currentColor" /></span>
              Watch Film
            </button>
          </motion.div>
        </motion.div>

        <motion.div 
          className="hero-visual"
          initial={{ opacity: 0, scale: 0.8, rotate: 10 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ duration: 1.5, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
          style={{ y: y2 }}
        >
          <div className="glow-ring"></div>
          <Tilt 
            tiltMaxAngleX={15} 
            tiltMaxAngleY={15} 
            perspective={1000} 
            scale={1.05} 
            transitionSpeed={2000}
            gyroscope={true}
          >
            <img src="/watch_black_gold.png" alt="Premium Watch" className="hero-watch-img" />
          </Tilt>
          
          <motion.div 
            className="floating-card glass top-card"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.5, duration: 0.8 }}
          >
            <h4>Swiss Made</h4>
            <p>Automatic Caliber</p>
          </motion.div>
          
          <motion.div 
            className="floating-card glass bottom-card"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.7, duration: 0.8 }}
          >
            <h4>Water Resistant</h4>
            <p>300m / 1000ft</p>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default Hero;
