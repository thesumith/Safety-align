import React from 'react';
import { motion } from 'framer-motion';
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
    <motion.div 
      className="loading-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="loading-container">
        <motion.div 
          className="loading-spinner"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <FaSpinner />
        </motion.div>
        
        <h2>Comparing RSI Documents</h2>
        <p className="loading-subtitle">This may take a few moments...</p>
        
        <div className="loading-steps">
          {steps.map((step, index) => (
            <motion.div 
              key={index}
              className="loading-step"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: step.delay, duration: 0.5 }}
            >
              <motion.div 
                className="step-icon"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ 
                  delay: step.delay + 0.5, 
                  duration: 0.5,
                  repeat: Infinity,
                  repeatDelay: 2
                }}
              >
                <step.icon />
              </motion.div>
              <span className="step-text">{step.text}</span>
            </motion.div>
          ))}
        </div>
        
        <div className="loading-progress">
          <motion.div 
            className="progress-bar"
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{ duration: 4, ease: "easeInOut" }}
          />
        </div>
      </div>
    </motion.div>
  );
};

export default LoadingSpinner;
