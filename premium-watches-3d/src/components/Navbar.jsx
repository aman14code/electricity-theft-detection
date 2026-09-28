import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Watch, ShoppingBag, Menu } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
  return (
    <motion.nav 
      className="navbar glass"
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: [0.6, 0.05, -0.01, 0.9] }}
    >
      <div className="nav-container container">
        <Link to="/" className="nav-logo" style={{ textDecoration: 'none' }}>
          <Watch className="logo-icon" />
          <span className="logo-text">CHRONOS</span>
        </Link>
        
        <ul className="nav-links">
          <li><Link to="/collection" className="nav-link">Collection</Link></li>
          <li><Link to="/heritage" className="nav-link">Heritage</Link></li>
          <li><Link to="/boutique" className="nav-link">Boutiques</Link></li>
        </ul>

        <div className="nav-actions">
          <button className="icon-btn"><ShoppingBag size={20} /></button>
          <button className="icon-btn mobile-menu"><Menu size={20} /></button>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;
