import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FaEye, FaEyeSlash, FaExpand, FaCompress, FaFileAlt, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
import './ComparisonView.css';

const ComparisonView = ({ results, outputDir }) => {
  const [expandedSections, setExpandedSections] = useState(new Set());
  const [selectedSection, setSelectedSection] = useState(null);
  const [viewMode, setViewMode] = useState('split'); // 'split' or 'full'

  const toggleSection = (sectionName) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionName)) {
      newExpanded.delete(sectionName);
    } else {
      newExpanded.add(sectionName);
    }
    setExpandedSections(newExpanded);
  };

  const getSimilarityColor = (score) => {
    if (score >= 0.8) return '#28a745';
    if (score >= 0.6) return '#ffc107';
    return '#dc3545';
  };

  const getSimilarityIcon = (score) => {
    if (score >= 0.8) return <FaCheckCircle />;
    if (score >= 0.6) return <FaExclamationTriangle />;
    return <FaExclamationTriangle />;
  };

  const formatSectionName = (name) => {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
      .replace('extra ', '');
  };

  const sections = results.detailed_results || {};

  return (
    <motion.div 
      className="comparison-view"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="comparison-header">
        <h2>Comparison Results</h2>
        <div className="view-controls">
          <button 
            className={`btn btn-sm ${viewMode === 'split' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setViewMode('split')}
          >
            Split View
          </button>
          <button 
            className={`btn btn-sm ${viewMode === 'full' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setViewMode('full')}
          >
            Full View
          </button>
        </div>
      </div>

      <div className={`comparison-container ${viewMode}`}>
        {viewMode === 'split' ? (
          <div className="split-view">
            <div className="comparison-panel">
              <div className="panel-header">
                <h3>Comparator RSI</h3>
                <span className="panel-subtitle">Reference Document</span>
              </div>
              <div className="panel-content">
                {Object.entries(sections).map(([sectionName, result]) => (
                  <div key={`comp-${sectionName}`} className="section-item">
                    <div className="section-header">
                      <span className="section-name">{formatSectionName(sectionName)}</span>
                      <div className="section-actions">
                        <button 
                          className="btn btn-sm btn-outline"
                          onClick={() => toggleSection(`comp-${sectionName}`)}
                        >
                          {expandedSections.has(`comp-${sectionName}`) ? <FaEyeSlash /> : <FaEye />}
                        </button>
                      </div>
                    </div>
                    {expandedSections.has(`comp-${sectionName}`) && (
                      <div className="section-content">
                        {result.missing_content && result.missing_content.length > 0 ? (
                          <div className="content-list">
                            {result.missing_content.slice(0, 3).map((content, index) => (
                              <div key={index} className="content-item missing">
                                {content}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="content-list">
                            {result.present_content && result.present_content.slice(0, 2).map((content, index) => (
                              <div key={index} className="content-item present">
                                {content}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="comparison-panel">
              <div className="panel-header">
                <h3>Our RSI</h3>
                <span className="panel-subtitle">Document Under Review</span>
              </div>
              <div className="panel-content">
                {Object.entries(sections).map(([sectionName, result]) => (
                  <div key={`our-${sectionName}`} className="section-item">
                    <div className="section-header">
                      <span className="section-name">{formatSectionName(sectionName)}</span>
                      <div className="section-actions">
                        <button 
                          className="btn btn-sm btn-outline"
                          onClick={() => toggleSection(`our-${sectionName}`)}
                        >
                          {expandedSections.has(`our-${sectionName}`) ? <FaEyeSlash /> : <FaEye />}
                        </button>
                      </div>
                    </div>
                    {expandedSections.has(`our-${sectionName}`) && (
                      <div className="section-content">
                        <div className="content-list">
                          {result.present_content && result.present_content.slice(0, 3).map((content, index) => (
                            <div key={index} className="content-item present">
                              {content}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="full-view">
            <div className="sections-list">
              {Object.entries(sections).map(([sectionName, result]) => (
                <motion.div 
                  key={sectionName}
                  className="section-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="section-card-header">
                    <div className="section-info">
                      <h4>{formatSectionName(sectionName)}</h4>
                      <div className="similarity-score">
                        <span 
                          className="score-value"
                          style={{ color: getSimilarityColor(result.similarity_score) }}
                        >
                          {(result.similarity_score * 100).toFixed(1)}%
                        </span>
                        <span className="score-icon" style={{ color: getSimilarityColor(result.similarity_score) }}>
                          {getSimilarityIcon(result.similarity_score)}
                        </span>
                      </div>
                    </div>
                    <button 
                      className="btn btn-sm btn-outline"
                      onClick={() => toggleSection(sectionName)}
                    >
                      {expandedSections.has(sectionName) ? <FaCompress /> : <FaExpand />}
                    </button>
                  </div>
                  
                  {expandedSections.has(sectionName) && (
                    <div className="section-card-content">
                      <div className="comparison-details">
                        <div className="detail-group">
                          <h5>Missing Content</h5>
                          <div className="content-list">
                            {result.missing_content && result.missing_content.length > 0 ? (
                              result.missing_content.slice(0, 3).map((content, index) => (
                                <div key={index} className="content-item missing">
                                  {content}
                                </div>
                              ))
                            ) : (
                              <div className="content-item present">No missing content detected</div>
                            )}
                          </div>
                        </div>
                        
                        <div className="detail-group">
                          <h5>Present Content</h5>
                          <div className="content-list">
                            {result.present_content && result.present_content.slice(0, 2).map((content, index) => (
                              <div key={index} className="content-item present">
                                {content}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ComparisonView;
