import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FaEye, FaEyeSlash, FaExpand, FaCompress, FaFileAlt, FaExclamationTriangle, FaCheckCircle, FaFilePdf } from 'react-icons/fa';
import PDFViewer from './PDFViewer';
import './ComparisonView.css';

const ComparisonView = ({ results, outputDir }) => {
  const [expandedSections, setExpandedSections] = useState(new Set());
  const [selectedSection, setSelectedSection] = useState(null);
  const [viewMode, setViewMode] = useState('split'); // 'split', 'full', or 'pdf'

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

  // Define SMPC section order (4.1, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9)
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

  const sortSectionsInSmpcOrder = (sections) => {
    const sortedEntries = [];
    
    // First, add sections in SMPC order
    for (const sectionName of smpcSectionOrder) {
      if (sections[sectionName]) {
        sortedEntries.push([sectionName, sections[sectionName]]);
      }
    }
    
    // Then add any remaining sections (should be minimal after filtering)
    for (const [sectionName, result] of Object.entries(sections)) {
      if (!smpcSectionOrder.includes(sectionName)) {
        sortedEntries.push([sectionName, result]);
      }
    }
    
    return sortedEntries;
  };

  const sections = results.detailed_results || {};
  const sortedSections = sortSectionsInSmpcOrder(sections);

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
          <button 
            className={`btn btn-sm ${viewMode === 'pdf' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setViewMode('pdf')}
          >
            <FaFilePdf /> PDF View
          </button>
        </div>
      </div>

      <div className={`comparison-container ${viewMode}`}>
        {viewMode === 'split' && (
          <div className="split-view">
            <div className="comparison-panel">
              <div className="panel-header">
                <h3>Comparator RSI</h3>
                <span className="panel-subtitle">Reference Document</span>
              </div>
              <div className="panel-content">
                {sortedSections.map(([sectionName, result]) => (
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
                {sortedSections.map(([sectionName, result]) => (
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
        )}

        {viewMode === 'full' && (
          <div className="full-view">
            <div className="sections-list">
              {sortedSections.map(([sectionName, result]) => (
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

        {viewMode === 'pdf' && (
          <PDFViewer 
            comparatorPdfUrl={results.comparator_pdf_url || `/api/pdf/comparator?output_dir=${outputDir}`}
            ourPdfUrl={results.our_pdf_url || `/api/pdf/our?output_dir=${outputDir}`}
            outputDir={outputDir}
          />
        )}
      </div>
    </motion.div>
  );
};

export default ComparisonView;
