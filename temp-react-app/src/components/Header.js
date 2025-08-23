import React from 'react';
import { FaSearch, FaFileAlt, FaChartBar } from 'react-icons/fa';
import './Header.css';

const Header = () => {
  return (
    <header className="header animate-fade-in">
      <div className="header-content">
        <div className="header-title animate-slide-in">
          <FaSearch className="header-icon" />
          <div>
            <h1>RSI Comparison Tool</h1>
            <p>Compare Regulatory Safety Information documents with precision</p>
          </div>
        </div>
        
        <div className="header-features animate-slide-in">
          <div className="feature-item">
            <FaFileAlt className="feature-icon" />
            <span>PDF Processing</span>
          </div>
          <div className="feature-item">
            <FaChartBar className="feature-icon" />
            <span>Smart Analysis</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
