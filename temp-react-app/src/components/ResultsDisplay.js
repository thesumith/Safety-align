import React, { useState } from 'react';
import { FaDownload, FaChartBar, FaExclamationTriangle, FaCheckCircle, FaFileAlt, FaRedo } from 'react-icons/fa';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import axios from 'axios';
import './ResultsDisplay.css';

const ResultsDisplay = ({ results, outputDir, onReset }) => {
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState(null);

  const summary = results.summary || {};
  const detailedResults = results.detailed_results || {};

  const getSimilarityColor = (score) => {
    if (score >= 0.8) return '#28a745';
    if (score >= 0.6) return '#ffc107';
    return '#dc3545';
  };

  const getStatusIcon = (score) => {
    if (score >= 0.8) return <FaCheckCircle className="status-icon success" />;
    if (score >= 0.6) return <FaExclamationTriangle className="status-icon warning" />;
    return <FaExclamationTriangle className="status-icon danger" />;
  };

  const formatSectionName = (name) => {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
      .replace('extra ', '');
  };

  const handleDownload = async (reportType) => {
    setDownloading(true);
    setDownloadError(null);

    try {
      const response = await axios.get(`/api/download/${reportType}`, {
        params: { output_dir: outputDir },
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `rsi_comparison_report.${reportType}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
      setDownloadError(`Failed to download ${reportType} report`);
    } finally {
      setDownloading(false);
    }
  };

  // Prepare chart data
  const pieData = [
    { name: 'High Similarity', value: Object.values(detailedResults).filter(r => r.similarity_score >= 0.8).length, color: '#28a745' },
    { name: 'Medium Similarity', value: Object.values(detailedResults).filter(r => r.similarity_score >= 0.6 && r.similarity_score < 0.8).length, color: '#ffc107' },
    { name: 'Low Similarity', value: Object.values(detailedResults).filter(r => r.similarity_score < 0.6).length, color: '#dc3545' }
  ];

  const barData = Object.entries(detailedResults).map(([name, result]) => ({
    section: formatSectionName(name),
    similarity: (result.similarity_score * 100).toFixed(1),
    score: result.similarity_score
  }));

  return (
    <div className="results-display animate-fade-in">
      <div className="results-header">
        <h2>Analysis Summary</h2>
        <button className="btn btn-outline" onClick={onReset}>
          <FaRedo />
          New Comparison
        </button>
      </div>

      <div className="results-grid">
        {/* Summary Cards */}
        <div className="summary-cards">
          <div className="summary-card">
            <div className="card-icon">
              <FaChartBar />
            </div>
            <div className="card-content">
              <h3>Overall Similarity</h3>
              <div className="metric-value" style={{ color: getSimilarityColor(summary.overall_similarity || 0) }}>
                {((summary.overall_similarity || 0) * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="card-icon">
              <FaFileAlt />
            </div>
            <div className="card-content">
              <h3>Sections Compared</h3>
              <div className="metric-value">
                {summary.total_sections_compared || 0}
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="card-icon">
              <FaExclamationTriangle />
            </div>
            <div className="card-content">
              <h3>Issues Found</h3>
              <div className="metric-value">
                {summary.sections_with_issues || 0}
              </div>
            </div>
          </div>

          <div className="summary-card">
            <div className="card-icon">
              <FaCheckCircle />
            </div>
            <div className="card-content">
              <h3>Missing Sections</h3>
              <div className="metric-value">
                {(summary.missing_sections || []).length}
              </div>
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="charts-section">
          <div className="chart-container">
            <h3>Similarity Distribution</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="chart-legend">
              {pieData.map((item, index) => (
                <div key={index} className="legend-item">
                  <div className="legend-color" style={{ backgroundColor: item.color }}></div>
                  <span>{item.name}: {item.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="chart-container">
            <h3>Section-by-Section Comparison</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="section" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip formatter={(value) => `${value}%`} />
                <Bar dataKey="similarity" fill="#3498db" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Issues List */}
        {summary.sections_needing_attention && summary.sections_needing_attention.length > 0 && (
          <div className="issues-section">
            <h3>Sections Needing Attention</h3>
            <div className="issues-list">
              {summary.sections_needing_attention.map((issue, index) => (
                <div key={index} className="issue-item">
                  <div className="issue-header">
                    <span className="issue-section">{formatSectionName(issue.section)}</span>
                    <div className="issue-score">
                      {getStatusIcon(issue.similarity_score)}
                      <span style={{ color: getSimilarityColor(issue.similarity_score) }}>
                        {(issue.similarity_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="issue-details">
                    <span className="issue-count">{issue.issues} missing items</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Download Section */}
        <div className="download-section">
          <h3>Download Reports</h3>
          <div className="download-buttons">
            <button 
              className="btn btn-primary"
              onClick={() => handleDownload('html')}
              disabled={downloading}
            >
              <FaDownload />
              HTML Report
            </button>
            <button 
              className="btn btn-primary"
              onClick={() => handleDownload('excel')}
              disabled={downloading}
            >
              <FaDownload />
              Excel Report
            </button>
            <button 
              className="btn btn-primary"
              onClick={() => handleDownload('pdf')}
              disabled={downloading}
            >
              <FaDownload />
              PDF Report
            </button>
          </div>
          {downloading && (
            <div className="download-status">
              <div className="spinner"></div>
              <span>Downloading...</span>
            </div>
          )}
          {downloadError && (
            <div className="download-error">
              {downloadError}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;
