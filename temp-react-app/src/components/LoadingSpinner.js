import React from 'react';
import { FaSpinner, FaFileAlt, FaSearch, FaChartBar } from 'react-icons/fa';
import './LoadingSpinner.css';

const LoadingSpinner = () => {
  const steps = [
    { icon: FaFileAlt, text: 'Processing PDF files...', delay: 0 },
    { icon: FaSearch, text: 'Extracting sections...', delay: 1 },
    { icon: FaChartBar, text: 'Comparing content...', delay: 2 },
    { icon: FaFileAlt, text: 'Generating reports...', delay: 3 }
  ];

  return (
    <div className="loading-overlay animate-fade-in">
      <div className="loading-container">
        <div className="loading-spinner animate-spin">
          <FaSpinner />
        </div>
        
        <h2>Comparing RSI Documents</h2>
        <p className="loading-subtitle">This may take a few moments...</p>
        
        <div className="loading-steps">
          {steps.map((step, index) => (
            <div 
              key={index}
              className="loading-step animate-fade-in"
              style={{ animationDelay: `${step.delay}s` }}
            >
              <div className="step-icon animate-pulse">
                <step.icon />
              </div>
              <span className="step-text">{step.text}</span>
            </div>
          ))}
        </div>
        
        <div className="loading-progress">
          <div className="progress-bar animate-progress"></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner;
