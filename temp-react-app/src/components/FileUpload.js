import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaCloudUploadAlt, FaFilePdf, FaPlay } from 'react-icons/fa';
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
  const [pdfUrls, setPdfUrls] = useState({
    comparator: null,
    our: null
  });

  const onDropComparator = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      // Revoke previous URL if it exists
      if (pdfUrls.comparator) {
        URL.revokeObjectURL(pdfUrls.comparator);
      }
      
      const newFile = acceptedFiles[0];
      const newUrl = URL.createObjectURL(newFile);
      
      setFiles(prev => ({ ...prev, comparator: newFile }));
      setPdfUrls(prev => ({ ...prev, comparator: newUrl }));
    }
  }, [pdfUrls.comparator]);

  const onDropOur = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      // Revoke previous URL if it exists
      if (pdfUrls.our) {
        URL.revokeObjectURL(pdfUrls.our);
      }
      
      const newFile = acceptedFiles[0];
      const newUrl = URL.createObjectURL(newFile);
      
      setFiles(prev => ({ ...prev, our: newFile }));
      setPdfUrls(prev => ({ ...prev, our: newUrl }));
    }
  }, [pdfUrls.our]);

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

  // Cleanup URLs when component unmounts
  useEffect(() => {
    return () => {
      if (pdfUrls.comparator) {
        URL.revokeObjectURL(pdfUrls.comparator);
      }
      if (pdfUrls.our) {
        URL.revokeObjectURL(pdfUrls.our);
      }
    };
  }, [pdfUrls.comparator, pdfUrls.our]);

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
        // Use backend PDF URLs from response
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
    // Revoke URL if it exists
    if (pdfUrls[type]) {
      URL.revokeObjectURL(pdfUrls[type]);
    }
    
    setFiles(prev => ({ ...prev, [type]: null }));
    setPdfUrls(prev => ({ ...prev, [type]: null }));
  };

  return (
    <div className="file-upload-container animate-fade-in">
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
                <div className="file-actions">
                  <button 
                    className="btn btn-sm btn-outline"
                    onClick={() => {
                      if (pdfUrls.comparator) {
                        window.open(pdfUrls.comparator, '_blank');
                      }
                    }}
                    title="Preview PDF"
                    disabled={!pdfUrls.comparator}
                  >
                    Preview
                  </button>
                  <button 
                    className="btn btn-sm btn-danger"
                    onClick={() => removeFile('comparator')}
                  >
                    Remove
                  </button>
                </div>
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
                <div className="file-actions">
                  <button 
                    className="btn btn-sm btn-outline"
                    onClick={() => {
                      if (pdfUrls.our) {
                        window.open(pdfUrls.our, '_blank');
                      }
                    }}
                    title="Preview PDF"
                    disabled={!pdfUrls.our}
                  >
                    Preview
                  </button>
                  <button 
                    className="btn btn-sm btn-danger"
                    onClick={() => removeFile('our')}
                  >
                    Remove
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <button
          className="btn btn-primary btn-lg compare-btn"
          onClick={handleSubmit}
          disabled={!files.comparator || !files.our || uploading}
        >
          <FaPlay />
          {uploading ? 'Comparing...' : 'Start Comparison'}
        </button>
      </div>
    </div>
  );
};

export default FileUpload;
