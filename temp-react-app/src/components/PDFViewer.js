import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Document, Page, pdfjs } from 'react-pdf';
import { FaDownload, FaExpand, FaCompress, FaSync, FaEye, FaEyeSlash, FaSearch, FaSearchMinus, FaSearchPlus, FaChevronLeft, FaChevronRight, FaList, FaBookmark } from 'react-icons/fa';
import './PDFViewer.css';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

const PDFViewer = ({ comparatorPdfUrl, ourPdfUrl, outputDir, sections = {} }) => {
  const [pdfLoaded, setPdfLoaded] = useState({ comparator: false, our: false });
  const [pdfError, setPdfError] = useState({ comparator: null, our: null });
  const [zoomLevel, setZoomLevel] = useState({ comparator: 1, our: 1 });
  const [showControls, setShowControls] = useState(true);
  const [syncZoom, setSyncZoom] = useState(true);
  const [syncScroll, setSyncScroll] = useState(true);
  const [currentPage, setCurrentPage] = useState({ comparator: 1, our: 1 });
  const [totalPages, setTotalPages] = useState({ comparator: 0, our: 0 });
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState({ comparator: [], our: [] });
  const [numPages, setNumPages] = useState({ comparator: 0, our: 0 });
  const [showSectionNavigator, setShowSectionNavigator] = useState(false);
  const [sectionPositions, setSectionPositions] = useState({});

  // Refs for PDF containers
  const comparatorRef = useRef(null);
  const ourRef = useRef(null);
  const comparatorDocumentRef = useRef(null);
  const ourDocumentRef = useRef(null);

  // Common RSI sections for navigation
  const commonSections = [
    'Indications',
    'Contraindications', 
    'Warnings and Precautions',
    'Adverse Reactions',
    'Drug Interactions',
    'Dosage and Administration',
    'Overdosage',
    'Storage and Handling',
    'Clinical Studies',
    'Patient Information'
  ];

  useEffect(() => {
    // Reset states when PDF URLs change
    setPdfLoaded({ comparator: false, our: false });
    setPdfError({ comparator: null, our: null });
    setZoomLevel({ comparator: 1, our: 1 });
    setCurrentPage({ comparator: 1, our: 1 });
    setTotalPages({ comparator: 0, our: 0 });
    setSearchResults({ comparator: [], our: [] });
    setNumPages({ comparator: 0, our: 0 });
    setSectionPositions({});
  }, [comparatorPdfUrl, ourPdfUrl]);

  // Function to handle synchronized scrolling
  const handleScroll = useCallback((type, event) => {
    if (!syncScroll) return;
    
    const sourceElement = event.target;
    const sourceScrollTop = sourceElement.scrollTop;
    const sourceScrollHeight = sourceElement.scrollHeight;
    const sourceClientHeight = sourceElement.clientHeight;
    
    // Calculate scroll percentage
    const scrollPercentage = sourceScrollTop / (sourceScrollHeight - sourceClientHeight);
    
    // Apply to the other PDF viewer
    const targetType = type === 'comparator' ? 'our' : 'comparator';
    const targetRef = targetType === 'comparator' ? comparatorRef : ourRef;
    
    if (targetRef.current) {
      const targetElement = targetRef.current;
      const targetScrollHeight = targetElement.scrollHeight;
      const targetClientHeight = targetElement.clientHeight;
      const targetScrollTop = scrollPercentage * (targetScrollHeight - targetClientHeight);
      
      targetElement.scrollTop = targetScrollTop;
    }
  }, [syncScroll]);

  // Function to handle synchronized zoom
  const handleZoomChange = useCallback((type, newZoom) => {
    const clampedZoom = Math.max(0.5, Math.min(3, newZoom));
    setZoomLevel(prev => ({ ...prev, [type]: clampedZoom }));
    
    if (syncZoom) {
      setZoomLevel(prev => ({ 
        comparator: clampedZoom, 
        our: clampedZoom 
      }));
    }
  }, [syncZoom]);

  // Function to handle synchronized page navigation
  const handlePageChange = useCallback((type, newPage) => {
    const clampedPage = Math.max(1, Math.min(numPages[type] || 1, newPage));
    setCurrentPage(prev => ({ ...prev, [type]: clampedPage }));
    
    if (syncScroll) {
      setCurrentPage(prev => ({ 
        comparator: clampedPage, 
        our: clampedPage 
      }));
    }
  }, [syncScroll, numPages]);

  // Function to search within PDFs
  const handleSearch = useCallback((term) => {
    setSearchTerm(term);
    if (!term.trim()) {
      setSearchResults({ comparator: [], our: [] });
      return;
    }
    
    // This would integrate with PDF.js search functionality
    console.log(`Searching for: ${term}`);
  }, []);

  // Function to navigate to a specific section
  const navigateToSection = useCallback((sectionName) => {
    console.log(`Navigating to section: ${sectionName}`);
    
    // For now, we'll scroll to the top and try to find the section
    // In a real implementation, this would use PDF.js to find text positions
    if (comparatorRef.current) {
      comparatorRef.current.scrollTop = 0;
    }
    if (ourRef.current) {
      ourRef.current.scrollTop = 0;
    }
    
    // Set a flag to indicate we're looking for this section
    setSectionPositions(prev => ({
      ...prev,
      [sectionName]: { searching: true, timestamp: Date.now() }
    }));
    
    // Clear the flag after a short delay
    setTimeout(() => {
      setSectionPositions(prev => ({
        ...prev,
        [sectionName]: { searching: false }
      }));
    }, 2000);
  }, []);

  const onDocumentLoadSuccess = (type, { numPages }) => {
    setNumPages(prev => ({ ...prev, [type]: numPages }));
    setPdfLoaded(prev => ({ ...prev, [type]: true }));
    setPdfError(prev => ({ ...prev, [type]: null }));
  };

  const onDocumentLoadError = (type, error) => {
    console.error(`PDF Error for ${type}:`, error);
    setPdfLoaded(prev => ({ ...prev, [type]: false }));
    setPdfError(prev => ({ ...prev, [type]: error }));
  };

  const resetZoom = () => {
    setZoomLevel({ comparator: 1, our: 1 });
  };

  const downloadPdf = (type) => {
    const url = type === 'comparator' ? comparatorPdfUrl : ourPdfUrl;
    const filename = type === 'comparator' ? 'comparator_rsi.pdf' : 'our_rsi.pdf';
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const openPdfInNewTab = (type) => {
    const url = type === 'comparator' ? comparatorPdfUrl : ourPdfUrl;
    window.open(url, '_blank');
  };

  const renderSectionNavigator = () => {
    if (!showSectionNavigator) return null;

    return (
      <motion.div 
        className="section-navigator"
        initial={{ opacity: 0, x: -300 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -300 }}
        transition={{ duration: 0.3 }}
      >
        <div className="section-navigator-header">
          <h4>Section Navigator</h4>
          <button
            className="btn btn-sm btn-outline"
            onClick={() => setShowSectionNavigator(false)}
          >
            ×
          </button>
        </div>
        <div className="section-list">
          {commonSections.map((section) => (
            <button
              key={section}
              className={`section-item ${sectionPositions[section]?.searching ? 'searching' : ''}`}
              onClick={() => navigateToSection(section)}
            >
              <FaBookmark className="section-icon" />
              <span>{section}</span>
              {sectionPositions[section]?.searching && (
                <div className="searching-indicator">
                  <div className="loading-spinner"></div>
                </div>
              )}
            </button>
          ))}
        </div>
      </motion.div>
    );
  };

  const renderPdfViewer = (type, url, title) => {
    if (!url) {
      return (
        <div className="pdf-placeholder">
          <div className="placeholder-content">
            <FaEye className="placeholder-icon" />
            <p>No PDF available</p>
          </div>
        </div>
      );
    }

    return (
      <div className="pdf-container">
        <div className="pdf-header">
          <h4>{title}</h4>
          <div className="pdf-controls">
            <div className="page-controls">
              <button
                className="btn btn-sm btn-outline"
                onClick={() => handlePageChange(type, currentPage[type] - 1)}
                disabled={currentPage[type] <= 1}
                title="Previous Page"
              >
                <FaChevronLeft />
              </button>
              <span className="page-info">
                {currentPage[type]} / {numPages[type] || '?'}
              </span>
              <button
                className="btn btn-sm btn-outline"
                onClick={() => handlePageChange(type, currentPage[type] + 1)}
                disabled={currentPage[type] >= (numPages[type] || 1)}
                title="Next Page"
              >
                <FaChevronRight />
              </button>
            </div>
            
            <button
              className="btn btn-sm btn-outline"
              onClick={() => downloadPdf(type)}
              title="Download PDF"
            >
              <FaDownload />
            </button>
            <button
              className="btn btn-sm btn-outline"
              onClick={() => openPdfInNewTab(type)}
              title="Open in New Tab"
            >
              <FaExpand />
            </button>
            <div className="zoom-controls">
              <button
                className="btn btn-sm btn-outline"
                onClick={() => handleZoomChange(type, zoomLevel[type] - 0.1)}
                disabled={zoomLevel[type] <= 0.5}
                title="Zoom Out"
              >
                <FaSearchMinus />
              </button>
              <span className="zoom-level">{Math.round(zoomLevel[type] * 100)}%</span>
              <button
                className="btn btn-sm btn-outline"
                onClick={() => handleZoomChange(type, zoomLevel[type] + 0.1)}
                disabled={zoomLevel[type] >= 3}
                title="Zoom In"
              >
                <FaSearchPlus />
              </button>
            </div>
          </div>
        </div>
        
        <div 
          className="pdf-frame-container"
          ref={type === 'comparator' ? comparatorRef : ourRef}
          onScroll={(e) => handleScroll(type, e)}
        >
          {pdfError[type] ? (
            <div className="pdf-error">
              <p>Error loading PDF: {pdfError[type]}</p>
              <button 
                className="btn btn-sm btn-primary"
                onClick={() => window.location.reload()}
              >
                <FaSync /> Retry
              </button>
            </div>
          ) : (
            <div className="pdf-content">
              <Document
                ref={type === 'comparator' ? comparatorDocumentRef : ourDocumentRef}
                file={url}
                onLoadSuccess={(pdf) => onDocumentLoadSuccess(type, pdf)}
                onLoadError={(error) => onDocumentLoadError(type, error)}
                loading={
                  <div className="pdf-loading">
                    <div className="loading-spinner"></div>
                    <p>Loading PDF...</p>
                  </div>
                }
                error={
                  <div className="pdf-error">
                    <p>Failed to load PDF</p>
                    <button 
                      className="btn btn-sm btn-primary"
                      onClick={() => window.location.reload()}
                    >
                      <FaSync /> Retry
                    </button>
                  </div>
                }
              >
                <Page
                  pageNumber={currentPage[type]}
                  scale={zoomLevel[type]}
                  loading={
                    <div className="page-loading">
                      <div className="loading-spinner"></div>
                    </div>
                  }
                />
              </Document>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <motion.div 
      className="pdf-viewer"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="pdf-viewer-header">
        <h2>PDF Comparison View</h2>
        <div className="viewer-controls">
          <div className="search-controls">
            <input
              type="text"
              placeholder="Search in PDFs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch(searchTerm)}
              className="search-input"
            />
            <button
              className="btn btn-sm btn-outline"
              onClick={() => handleSearch(searchTerm)}
              title="Search in PDFs"
            >
              <FaSearch />
            </button>
          </div>
          
          <button
            className={`btn btn-sm ${showSectionNavigator ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setShowSectionNavigator(!showSectionNavigator)}
            title="Section Navigator"
          >
            <FaList /> Sections
          </button>
          
          <button
            className={`btn btn-sm ${syncZoom ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setSyncZoom(!syncZoom)}
            title="Sync zoom between PDFs"
          >
            <FaSync /> Sync Zoom
          </button>
          
          <button
            className={`btn btn-sm ${syncScroll ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setSyncScroll(!syncScroll)}
            title="Sync scroll between PDFs"
          >
            <FaSync /> Sync Scroll
          </button>
          
          <button
            className="btn btn-sm btn-outline"
            onClick={resetZoom}
            title="Reset zoom to 100%"
          >
            <FaCompress /> Reset Zoom
          </button>
          
          <button
            className="btn btn-sm btn-outline"
            onClick={() => setShowControls(!showControls)}
            title="Toggle controls"
          >
            {showControls ? <FaEyeSlash /> : <FaEye />}
          </button>
        </div>
      </div>

      <div className={`pdf-comparison-container ${showSectionNavigator ? 'with-navigator' : ''}`}>
        {renderSectionNavigator()}
        <div className="pdf-panel">
          {renderPdfViewer(
            'comparator', 
            comparatorPdfUrl, 
            'Comparator RSI (Reference)'
          )}
        </div>
        
        <div className="pdf-panel">
          {renderPdfViewer(
            'our', 
            ourPdfUrl, 
            'Our RSI (Under Review)'
          )}
        </div>
      </div>

      {showControls && (
        <div className="pdf-info">
          <div className="info-item">
            <strong>Tip:</strong> Use the zoom controls to adjust the view. Enable "Sync Zoom" to keep both PDFs at the same zoom level.
          </div>
          <div className="info-item">
            <strong>Navigation:</strong> Use page controls to navigate through PDFs. Enable "Sync Scroll" to synchronize scrolling between both PDF viewers.
          </div>
          <div className="info-item">
            <strong>Sections:</strong> Use the "Sections" button to quickly navigate to specific RSI sections in both PDFs.
          </div>
          <div className="info-item">
            <strong>Search:</strong> Use the search box to find specific content in both PDFs simultaneously.
          </div>
          <div className="info-item">
            <strong>PDF Viewing:</strong> PDFs are rendered using react-pdf for better compatibility and performance.
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default PDFViewer;
