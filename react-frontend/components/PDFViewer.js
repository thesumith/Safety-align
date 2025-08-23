import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaDownload, FaExpand, FaCompress, FaSync, FaEye, FaEyeSlash } from 'react-icons/fa';
import './PDFViewer.css';

const PDFViewer = ({ comparatorPdfUrl, ourPdfUrl, outputDir }) => {
  const [pdfLoaded, setPdfLoaded] = useState({ comparator: false, our: false });
  const [pdfError, setPdfError] = useState({ comparator: null, our: null });
  const [zoomLevel, setZoomLevel] = useState({ comparator: 1, our: 1 });
  const [showControls, setShowControls] = useState(true);
  const [syncZoom, setSyncZoom] = useState(true);

  useEffect(() => {
    // Reset states when PDF URLs change
    setPdfLoaded({ comparator: false, our: false });
    setPdfError({ comparator: null, our: null });
    setZoomLevel({ comparator: 1, our: 1 });
  }, [comparatorPdfUrl, ourPdfUrl]);

  const handlePdfLoad = (type) => {
    setPdfLoaded(prev => ({ ...prev, [type]: true }));
    setPdfError(prev => ({ ...prev, [type]: null }));
  };

  const handlePdfError = (type, error) => {
    console.error(`PDF Error for ${type}:`, error);
    setPdfLoaded(prev => ({ ...prev, [type]: false }));
    setPdfError(prev => ({ ...prev, [type]: error }));
  };

  const handleZoomChange = (type, newZoom) => {
    const clampedZoom = Math.max(0.5, Math.min(3, newZoom));
    setZoomLevel(prev => ({ ...prev, [type]: clampedZoom }));
    
    if (syncZoom) {
      setZoomLevel(prev => ({ 
        comparator: clampedZoom, 
        our: clampedZoom 
      }));
    }
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

  const renderPdfFrame = (type, url, title) => {
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
              >
                -
              </button>
              <span className="zoom-level">{Math.round(zoomLevel[type] * 100)}%</span>
              <button
                className="btn btn-sm btn-outline"
                onClick={() => handleZoomChange(type, zoomLevel[type] + 0.1)}
                disabled={zoomLevel[type] >= 3}
              >
                +
              </button>
            </div>
          </div>
        </div>
        
        <div className="pdf-frame-container">
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
            <object
              data={url}
              type="application/pdf"
              className="pdf-frame"
              style={{ transform: `scale(${zoomLevel[type]})` }}
              onLoad={() => handlePdfLoad(type)}
              onError={() => handlePdfError(type, 'Failed to load PDF')}
            >
              <iframe
                src={url}
                className="pdf-frame"
                style={{ transform: `scale(${zoomLevel[type]})` }}
                onLoad={() => handlePdfLoad(type)}
                onError={() => handlePdfError(type, 'Failed to load PDF')}
                title={`${title} PDF Viewer`}
                onLoadStart={() => console.log(`Loading PDF for ${type}: ${url}`)}
              />
              <div className="pdf-fallback">
                <p>Your browser doesn't support PDF viewing.</p>
                <a href={url} target="_blank" rel="noopener noreferrer" className="btn btn-primary">
                  Open PDF in New Tab
                </a>
              </div>
            </object>
          )}
          
          {!pdfLoaded[type] && !pdfError[type] && (
            <div className="pdf-loading">
              <div className="loading-spinner"></div>
              <p>Loading PDF...</p>
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
          <button
            className={`btn btn-sm ${syncZoom ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setSyncZoom(!syncZoom)}
            title="Sync zoom between PDFs"
          >
            <FaSync /> Sync Zoom
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
          <button
            className="btn btn-sm btn-outline"
            onClick={() => {
              console.log('PDF URLs:', { comparatorPdfUrl, ourPdfUrl, outputDir });
              // Test PDF access
              fetch(`/api/test-pdf-access?output_dir=${outputDir}`)
                .then(res => res.json())
                .then(data => console.log('PDF Access Test:', data))
                .catch(err => console.error('PDF Access Test Error:', err));
            }}
            title="Debug PDF access"
          >
            Debug
          </button>
        </div>
      </div>

      <div className="pdf-comparison-container">
        <div className="pdf-panel">
          {renderPdfFrame(
            'comparator', 
            comparatorPdfUrl, 
            'Comparator RSI (Reference)'
          )}
        </div>
        
        <div className="pdf-panel">
          {renderPdfFrame(
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
            <strong>Navigation:</strong> Scroll within each PDF frame to navigate through the documents.
          </div>
          <div className="info-item">
            <strong>PDF Viewing:</strong> If PDFs don't display properly, use the "Open in New Tab" button for better viewing.
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default PDFViewer;
