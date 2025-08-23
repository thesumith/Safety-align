import React from 'react';
import { motion } from 'framer-motion';
import { FaSearch, FaFileAlt, FaChartBar } from 'react-icons/fa';
import './Header.css';

const Header = () => {
  return (
    <motion.header 
      className="header"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="header-content">
        <motion.div 
          className="header-title"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <FaSearch className="header-icon" />
          <div>
            <h1>RSI Comparison Tool</h1>
            <p>Compare Regulatory Safety Information documents with precision</p>
          </div>
        </motion.div>
        
        <motion.div 
          className="header-features"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <div className="feature-item">
            <FaFileAlt className="feature-icon" />
            <span>PDF Processing</span>
          </div>
          <div className="feature-item">
            <FaChartBar className="feature-icon" />
            <span>Smart Analysis</span>
          </div>
        </motion.div>
      </div>
    </motion.header>
  );
};

export default Header;
