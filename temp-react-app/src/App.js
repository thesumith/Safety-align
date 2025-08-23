import React, { useState } from 'react';
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

  const resetComparison = () => {
    setComparisonState({
      isComparing: false,
      results: null,
      error: null,
      outputDir: null
    });
  };

  return (
    <div className="App">
      <Header />
      
      <div className="main-container animate-fade-in">
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
          />
        )}

        {comparisonState.error && (
          <div className="error-container animate-fade-in">
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
          </div>
        )}

        {comparisonState.results && !comparisonState.isComparing && (
          <div className="animate-fade-in">
            <ComparisonView 
              results={comparisonState.results}
              outputDir={comparisonState.outputDir}
            />
            <ResultsDisplay 
              results={comparisonState.results}
              outputDir={comparisonState.outputDir}
              onReset={resetComparison}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
