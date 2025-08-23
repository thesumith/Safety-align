import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { FaCloudUploadAlt, FaFilePdf, FaCog, FaPlay } from 'react-icons/fa';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = ({ 
  settings, 
  setSettings, 
  onStartComparison, 
  onComparisonComplete, 
  onComparisonError 
}) => {
  const [files, setFiles] = useState({
    comparator: null,
    our: null
  });
  const [uploading, setUploading] = useState(false);

  const onDropComparator = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFiles(prev => ({ ...prev, comparator: acceptedFiles[0] }));
    }
  }, []);

  const onDropOur = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFiles(prev => ({ ...prev, our: acceptedFiles[0] }));
    }
  }, []);

  const { getRootProps: getComparatorRootProps, getInputProps: getComparatorInputProps, isDragActive: isComparatorDragActive } = useDropzone({
    onDrop: onDropComparator,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false
  });

  const { getRootProps: getOurRootProps, getInputProps: getOurInputProps, isDragActive: isOurDragActive } = useDropzone({
    onDrop: onDropOur,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!files.comparator || !files.our) {
      alert('Please upload both PDF files');
      return;
    }

    setUploading(true);
    onStartComparison();

    try {
      const formData = new FormData();
      formData.append('comparator_pdf', files.comparator);
      formData.append('our_pdf', files.our);
      formData.append('similarity_threshold', settings.similarityThreshold);

      const response = await axios.post('/api/compare', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        onComparisonComplete(response.data, response.data.output_dir);
      } else {
        onComparisonError(response.data.error || 'Comparison failed');
      }
    } catch (error) {
      console.error('Comparison error:', error);
      onComparisonError(error.response?.data?.error || 'An error occurred during comparison');
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (type) => {
    setFiles(prev => ({ ...prev, [type]: null }));
  };

  return (
    <motion.div 
      className="file-upload-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="row">
        <div className="col-8">
          <div className="upload-section">
            <h2>Upload RSI Documents</h2>
            <p className="text-muted">Upload two PDF files to compare their content</p>
            
            <div className="upload-grid">
              <div className="upload-card">
                <h3>Comparator RSI</h3>
                <div 
                  {...getComparatorRootProps()} 
                  className={`dropzone ${isComparatorDragActive ? 'dragover' : ''}`}
                >
                  <input {...getComparatorInputProps()} />
                  <FaCloudUploadAlt className="upload-icon" />
                  <p>Drag & drop comparator PDF here, or click to select</p>
                  <span className="file-type">PDF files only</span>
                </div>
                {files.comparator && (
                  <div className="file-info">
                    <FaFilePdf className="file-icon" />
                    <span>{files.comparator.name}</span>
                    <button 
                      className="btn btn-sm btn-danger"
                      onClick={() => removeFile('comparator')}
                    >
                      Remove
                    </button>
                  </div>
                )}
              </div>

              <div className="upload-card">
                <h3>Our RSI</h3>
                <div 
                  {...getOurRootProps()} 
                  className={`dropzone ${isOurDragActive ? 'dragover' : ''}`}
                >
                  <input {...getOurInputProps()} />
                  <FaCloudUploadAlt className="upload-icon" />
                  <p>Drag & drop our RSI PDF here, or click to select</p>
                  <span className="file-type">PDF files only</span>
                </div>
                {files.our && (
                  <div className="file-info">
                    <FaFilePdf className="file-icon" />
                    <span>{files.our.name}</span>
                    <button 
                      className="btn btn-sm btn-danger"
                      onClick={() => removeFile('our')}
                    >
                      Remove
                    </button>
                  </div>
                )}
              </div>
            </div>

            <motion.button
              className="btn btn-primary btn-lg compare-btn"
              onClick={handleSubmit}
              disabled={!files.comparator || !files.our || uploading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <FaPlay />
              {uploading ? 'Comparing...' : 'Start Comparison'}
            </motion.button>
          </div>
        </div>

        <div className="col-4">
          <div className="settings-panel">
            <div className="settings-header">
              <FaCog className="settings-icon" />
              <h3>Settings</h3>
            </div>
            
            <div className="setting-group">
              <label className="form-label">Similarity Threshold</label>
              <div className="slider-container">
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.similarityThreshold}
                  onChange={(e) => setSettings(prev => ({ 
                    ...prev, 
                    similarityThreshold: parseFloat(e.target.value) 
                  }))}
                  className="slider"
                />
                <span className="slider-value">{settings.similarityThreshold}</span>
              </div>
              <small className="text-muted">
                Higher values require more exact matches
              </small>
            </div>

            <div className="setting-group">
              <label className="form-label">Report Formats</label>
              <div className="checkbox-group">
                <label className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={settings.generateExcel}
                    onChange={(e) => setSettings(prev => ({ 
                      ...prev, 
                      generateExcel: e.target.checked 
                    }))}
                  />
                  <span>Excel Report</span>
                </label>
                <label className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={settings.generatePdf}
                    onChange={(e) => setSettings(prev => ({ 
                      ...prev, 
                      generatePdf: e.target.checked 
                    }))}
                  />
                  <span>PDF Report</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default FileUpload;
