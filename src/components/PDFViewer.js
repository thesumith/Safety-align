import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaExpand, FaCompress, FaSync, FaFilePdf } from 'react-icons/fa';
import './PDFViewer.css';

const PDFViewer = ({ results, outputDir }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [syncScroll, setSyncScroll] = useState(true);
  const [currentSection, setCurrentSection] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const leftViewerRef = useRef(null);
  const rightViewerRef = useRef(null);
  const containerRef = useRef(null);

  const detailedResults = results.detailed_results || {};
  const summary = results.summary || {};
  const comparatorSections = results.comparator_sections || {};
  const ourSections = results.our_sections || {};

  // SMPC section order for navigation
  const smpcSectionOrder = [
    'therapeutic_indications',      // 4.1 Therapeutic indications
    'contraindications',            // 4.3 Contraindications
    'special_warnings_precautions', // 4.4 Special warnings and precautions
    'interactions_medicinal_products', // 4.5 Interactions
    'fertility_pregnancy_lactation', // 4.6 Fertility, pregnancy and lactation
    'effects_ability_drive_machines', // 4.7 Effects on ability to drive
    'undesirable_effects',          // 4.8 Undesirable effects
    'overdose'                      // 4.9 Overdose
  ];

  const formatSectionName = (name) => {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
      .replace('extra ', '');
  };

  const getSimilarityColor = (score) => {
    if (score >= 0.8) return '#28a745';
    if (score >= 0.6) return '#ffc107';
    return '#dc3545';
  };

  const getStatusIcon = (score) => {
    if (score >= 0.8) return <FaFilePdf className="status-icon success" />;
    if (score >= 0.6) return <FaFilePdf className="status-icon warning" />;
    return <FaFilePdf className="status-icon danger" />;
  };

  // Handle synchronized scrolling
  const handleScroll = (source, event) => {
    if (!syncScroll) return;
    
    const target = source === 'left' ? rightViewerRef.current : leftViewerRef.current;
    if (target && event.target.scrollHeight > event.target.clientHeight) {
      const scrollTop = event.target.scrollTop;
      const scrollHeight = event.target.scrollHeight;
      const clientHeight = event.target.clientHeight;
      
      // Calculate scroll percentage
      const scrollPercentage = scrollTop / (scrollHeight - clientHeight);
      
      // Apply same percentage to other viewer
      const targetScrollHeight = target.scrollHeight;
      const targetClientHeight = target.clientHeight;
      
      if (targetScrollHeight > targetClientHeight) {
        const targetScrollTop = scrollPercentage * (targetScrollHeight - targetClientHeight);
        target.scrollTop = targetScrollTop;
      }
    }
  };

  // Navigate to specific section
  const navigateToSection = (sectionName) => {
    setCurrentSection(sectionName);
    
    // Find the section element in both viewers and scroll to it
    const sectionElements = document.querySelectorAll(`[data-section="${sectionName}"]`);
    sectionElements.forEach(element => {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  };

  // Toggle fullscreen mode
  const toggleFullscreen = () => {
    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  // Handle fullscreen change
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Simulate loading completion
  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="pdf-viewer-loading">
        <div className="loading-spinner"></div>
        <p>Loading PDF viewer...</p>
      </div>
    );
  }

  return (
    <motion.div 
      className={`pdf-viewer-container ${isFullscreen ? 'fullscreen' : ''}`}
      ref={containerRef}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header Controls */}
      <div className="pdf-viewer-header">
        <div className="viewer-controls">
          <button 
            className={`control-btn ${syncScroll ? 'active' : ''}`}
            onClick={() => setSyncScroll(!syncScroll)}
            title={syncScroll ? 'Disable synchronized scrolling' : 'Enable synchronized scrolling'}
          >
            <FaSync />
            {syncScroll ? 'Sync On' : 'Sync Off'}
          </button>
          <button 
            className="control-btn"
            onClick={toggleFullscreen}
            title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          >
            {isFullscreen ? <FaCompress /> : <FaExpand />}
            {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          </button>
        </div>
        
        <div className="viewer-title">
          <h3>Side-by-Side PDF Comparison</h3>
          <p>Synchronized scrolling: {syncScroll ? 'Enabled' : 'Disabled'}</p>
        </div>
      </div>

      {/* Section Navigation */}
      <div className="section-navigation">
        <h4>Navigate to Sections:</h4>
        <div className="section-buttons">
          {smpcSectionOrder.map(sectionName => {
            const result = detailedResults[sectionName];
            if (!result) return null;
            
            return (
              <button
                key={sectionName}
                className={`section-btn ${currentSection === sectionName ? 'active' : ''}`}
                onClick={() => navigateToSection(sectionName)}
                style={{ 
                  borderLeftColor: getSimilarityColor(result.similarity_score),
                  borderLeftWidth: '4px'
                }}
              >
                <span className="section-icon">
                  {getStatusIcon(result.similarity_score)}
                </span>
                <span className="section-name">{formatSectionName(sectionName)}</span>
                <span className="section-score">
                  {(result.similarity_score * 100).toFixed(1)}%
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* PDF Viewers */}
      <div className="pdf-viewers">
        {/* Left PDF Viewer (Comparator) */}
        <div className="pdf-viewer left-viewer">
          <div className="viewer-label">
            <h4>Comparator RSI</h4>
            <span className="file-info">Reference Document</span>
          </div>
          
          <div 
            className="pdf-content"
            ref={leftViewerRef}
            onScroll={(e) => handleScroll('left', e)}
          >
            {Object.entries(detailedResults).map(([sectionName, result]) => (
                             <div 
                 key={`left-${sectionName}`}
                 className={`pdf-section ${result.similarity_score < 0.6 ? 'low-similarity' : result.similarity_score < 0.8 ? 'medium-similarity' : 'high-similarity'}`}
                 data-section={sectionName}
               >
                <div className="section-header">
                  <h5>{formatSectionName(sectionName)}</h5>
                  <div className="section-meta">
                    <span className="section-number">
                      {smpcSectionOrder.indexOf(sectionName) >= 0 
                        ? `4.${smpcSectionOrder.indexOf(sectionName) + 1}` 
                        : 'N/A'}
                    </span>
                    <span className="section-score">
                      {(result.similarity_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                {result.similarity_score < 0.8 && (
                  <div className="section-alert">
                    <span className="alert-icon">⚠️</span>
                    <span className="alert-text">
                      {result.similarity_score < 0.6 
                        ? 'Significant differences detected' 
                        : 'Minor differences detected'}
                    </span>
                  </div>
                )}
                
                <div className="section-content">
                  {comparatorSections[sectionName] && comparatorSections[sectionName].content ? (
                    <div className="content-text">
                      {comparatorSections[sectionName].content.split('\n').map((line, index) => (
                        <p key={index}>{line}</p>
                      ))}
                    </div>
                  ) : (
                    <div className="content-placeholder">
                      <p>Section content not available</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right PDF Viewer (Our RSI) */}
        <div className="pdf-viewer right-viewer">
          <div className="viewer-label">
            <h4>Our RSI</h4>
            <span className="file-info">Target Document</span>
          </div>
          
          <div 
            className="pdf-content"
            ref={rightViewerRef}
            onScroll={(e) => handleScroll('right', e)}
          >
            {Object.entries(detailedResults).map(([sectionName, result]) => (
                             <div 
                 key={`right-${sectionName}`}
                 className={`pdf-section ${result.similarity_score < 0.6 ? 'low-similarity' : result.similarity_score < 0.8 ? 'medium-similarity' : 'high-similarity'}`}
                 data-section={sectionName}
               >
                <div className="section-header">
                  <h5>{formatSectionName(sectionName)}</h5>
                  <div className="section-meta">
                    <span className="section-number">
                      {smpcSectionOrder.indexOf(sectionName) >= 0 
                        ? `4.${smpcSectionOrder.indexOf(sectionName) + 1}` 
                        : 'N/A'}
                    </span>
                    <span className="section-score">
                      {(result.similarity_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                {result.similarity_score < 0.8 && (
                  <div className="section-alert">
                    <span className="alert-icon">⚠️</span>
                    <span className="alert-text">
                      {result.similarity_score < 0.6 
                        ? 'Significant differences detected' 
                        : 'Minor differences detected'}
                    </span>
                  </div>
                )}
                
                <div className="section-content">
                  {ourSections[sectionName] && ourSections[sectionName].content ? (
                    <div className="content-text">
                      {ourSections[sectionName].content.split('\n').map((line, index) => (
                        <p key={index}>{line}</p>
                      ))}
                    </div>
                  ) : (
                    <div className="content-placeholder">
                      <p>Section content not available</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pdf-viewer-footer">
        <div className="footer-info">
          <span>Overall Similarity: {(summary.overall_similarity * 100).toFixed(1)}%</span>
          <span>Sections Compared: {summary.total_sections_compared}</span>
          <span>Issues Found: {summary.sections_with_issues}</span>
        </div>
      </div>
    </motion.div>
  );
};

export default PDFViewer;
