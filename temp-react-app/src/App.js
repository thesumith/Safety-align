import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import ComparisonView from './components/ComparisonView';
import ResultsDisplay from './components/ResultsDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import './App.css';

function App() {
  const [comparisonState, setComparisonState] = useState({
    isComparing: false,
    results: null,
    error: null,
    outputDir: null
  });

  const [uploadedFiles, setUploadedFiles] = useState(null);

  const [settings, setSettings] = useState({
    similarityThreshold: 0.7,
    generateExcel: true,
    generatePdf: true
  });

  const handleComparisonComplete = (results, outputDir) => {
    setComparisonState({
      isComparing: false,
      results,
      error: null,
      outputDir
    });
  };

  const handleComparisonError = (error) => {
    setComparisonState({
      isComparing: false,
      results: null,
      error,
      outputDir: null
    });
  };

  const handleStartComparison = () => {
    setComparisonState(prev => ({
      ...prev,
      isComparing: true,
      error: null
    }));
  };

  const handleFilesUploaded = (uploadData) => {
    setUploadedFiles(uploadData);
  };

  const resetComparison = () => {
    setComparisonState({
      isComparing: false,
      results: null,
      error: null,
      outputDir: null
    });
    setUploadedFiles(null);
  };

  return (
    <div className="App">
      <Header />
      
      <motion.div 
        className="main-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {comparisonState.isComparing && (
          <LoadingSpinner />
        )}

        {!comparisonState.results && !comparisonState.isComparing && (
          <FileUpload
            settings={settings}
            setSettings={setSettings}
            onStartComparison={handleStartComparison}
            onComparisonComplete={handleComparisonComplete}
            onComparisonError={handleComparisonError}
            onFilesUploaded={handleFilesUploaded}
          />
        )}

        {uploadedFiles && !comparisonState.results && !comparisonState.isComparing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <ComparisonView 
              results={{
                comparator_pdf_url: uploadedFiles.comparator_pdf_url,
                our_pdf_url: uploadedFiles.our_pdf_url
              }}
              outputDir={null}
              showOnlyPdfView={true}
            />
          </motion.div>
        )}

        {comparisonState.error && (
          <motion.div 
            className="error-container"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <div className="error-message">
              <h3>Error</h3>
              <p>{comparisonState.error}</p>
              <button 
                className="btn btn-primary"
                onClick={resetComparison}
              >
                Try Again
              </button>
            </div>
          </motion.div>
        )}

        {comparisonState.results && !comparisonState.isComparing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <ComparisonView 
              results={comparisonState.results}
              outputDir={comparisonState.outputDir}
            />
            <ResultsDisplay 
              results={comparisonState.results}
              outputDir={comparisonState.outputDir}
              onReset={resetComparison}
            />
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}

export default App;
