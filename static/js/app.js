// Enhanced JavaScript functionality for RSI Comparison Tool

class RSIComparisonApp {
    constructor() {
        this.currentOutputDir = '';
        this.initializeEventListeners();
        this.initializeDragAndDrop();
    }

    initializeEventListeners() {
        // File upload handling
        document.getElementById('comparatorPdf')?.addEventListener('change', (e) => {
            this.updateFileName(e, 'comparatorFileName');
        });

        document.getElementById('ourPdf')?.addEventListener('change', (e) => {
            this.updateFileName(e, 'ourFileName');
        });

        // Similarity threshold slider
        document.getElementById('similarityThreshold')?.addEventListener('input', (e) => {
            document.getElementById('thresholdValue').textContent = e.target.value;
        });

        // Form submission
        document.getElementById('comparisonForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmission();
        });
    }

    initializeDragAndDrop() {
        const uploadAreas = document.querySelectorAll('.file-upload-area');
        
        uploadAreas.forEach(area => {
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
            });
            
            area.addEventListener('dragleave', () => {
                area.classList.remove('dragover');
            });
            
            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    const file = files[0];
                    if (file.type === 'application/pdf') {
                        const input = area.querySelector('input[type="file"]');
                        input.files = files;
                        input.dispatchEvent(new Event('change'));
                    } else {
                        this.showError('Please upload PDF files only');
                    }
                }
            });
        });
    }

    updateFileName(event, elementId) {
        const fileName = event.target.files[0]?.name || '';
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = fileName;
            element.style.fontWeight = 'bold';
            element.style.color = '#27ae60';
        }
    }

    async handleFormSubmission() {
        const form = document.getElementById('comparisonForm');
        const formData = new FormData(form);
        
        // Validate files
        if (!this.validateFiles(formData)) {
            return;
        }
        
        // Show loading
        this.showLoading();
        
        try {
            const response = await fetch('/api/compare', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.currentOutputDir = result.output_dir;
                this.displayResults(result);
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('An error occurred during comparison: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    validateFiles(formData) {
        const comparatorFile = formData.get('comparator_pdf');
        const ourFile = formData.get('our_pdf');
        
        if (!comparatorFile || !ourFile || comparatorFile.size === 0 || ourFile.size === 0) {
            this.showError('Please select both PDF files');
            return false;
        }
        
        if (!comparatorFile.name.toLowerCase().endsWith('.pdf') || !ourFile.name.toLowerCase().endsWith('.pdf')) {
            this.showError('Only PDF files are supported');
            return false;
        }
        
        // Check file size (50MB limit)
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (comparatorFile.size > maxSize || ourFile.size > maxSize) {
            this.showError('File size must be less than 50MB');
            return false;
        }
        
        return true;
    }

    showLoading() {
        const loadingSection = document.getElementById('loadingSection');
        if (loadingSection) {
            loadingSection.style.display = 'block';
        }
        
        // Hide results and download sections
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('downloadSection').style.display = 'none';
        
        // Disable form
        const form = document.getElementById('comparisonForm');
        if (form) {
            const inputs = form.querySelectorAll('input, button');
            inputs.forEach(input => input.disabled = true);
        }
    }

    hideLoading() {
        const loadingSection = document.getElementById('loadingSection');
        if (loadingSection) {
            loadingSection.style.display = 'none';
        }
        
        // Re-enable form
        const form = document.getElementById('comparisonForm');
        if (form) {
            const inputs = form.querySelectorAll('input, button');
            inputs.forEach(input => input.disabled = false);
        }
    }

    displayResults(data) {
        this.displaySummaryCards(data.summary);
        this.displayDetailedResults(data.detailed_results);
        
        // Show results and download sections
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('downloadSection').style.display = 'block';
        
        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth' 
        });
    }

    displaySummaryCards(summary) {
        const summaryCards = document.getElementById('summaryCards');
        if (!summaryCards) return;
        
        summaryCards.innerHTML = `
            <div class="col-md-3">
                <div class="summary-card">
                    <h3>Overall Similarity</h3>
                    <div class="h2 similarity-${this.getSimilarityClass(summary.overall_similarity)}">
                        ${(summary.overall_similarity * 100).toFixed(1)}%
                    </div>
                    <small>Combined score across all sections</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="summary-card">
                    <h3>Sections Compared</h3>
                    <div class="h2">${summary.total_sections_compared}</div>
                    <small>Total sections analyzed</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="summary-card">
                    <h3>Sections with Issues</h3>
                    <div class="h2 similarity-low">${summary.sections_with_issues}</div>
                    <small>Sections below threshold</small>
                </div>
            </div>
            <div class="col-md-3">
                <div class="summary-card">
                    <h3>Missing Sections</h3>
                    <div class="h2 similarity-low">${summary.missing_sections.length}</div>
                    <small>Completely missing sections</small>
                </div>
            </div>
        `;
    }

    displayDetailedResults(results) {
        const container = document.getElementById('detailedResults');
        if (!container) return;
        
        container.innerHTML = '<h4><i class="fas fa-list"></i> Detailed Section Analysis</h4>';

        Object.entries(results).forEach(([sectionName, result]) => {
            if (sectionName.startsWith('extra_')) return;

            const sectionDiv = document.createElement('div');
            sectionDiv.className = 'card mb-3 section-card';
            
            const similarityClass = this.getSimilarityClass(result.similarity_score);
            
            sectionDiv.innerHTML = `
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">${sectionName.replace('_', ' ').toUpperCase()}</h5>
                    <span class="badge bg-${similarityClass === 'high' ? 'success' : similarityClass === 'medium' ? 'warning' : 'danger'}">
                        ${(result.similarity_score * 100).toFixed(1)}% Similarity
                    </span>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6><i class="fas fa-exclamation-triangle text-danger"></i> Missing Content (${result.missing_count})</h6>
                            ${result.missing_content.length > 0 ? 
                                result.missing_content.map(item => `<div class="alert alert-danger">• ${this.truncateText(item, 150)}</div>`).join('') :
                                '<div class="text-success"><i class="fas fa-check"></i> No missing content</div>'
                            }
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-check text-success"></i> Present Content (${result.present_count})</h6>
                            ${result.present_content.length > 0 ? 
                                result.present_content.map(item => `<div class="alert alert-success">• ${this.truncateText(item, 150)}</div>`).join('') :
                                '<div class="text-muted">No content to display</div>'
                            }
                        </div>
                    </div>
                    <small class="text-muted">Method: ${result.comparison_method.replace('_', ' ').toUpperCase()}</small>
                </div>
            `;
            
            container.appendChild(sectionDiv);
        });
    }

    getSimilarityClass(score) {
        if (score >= 0.8) return 'high';
        if (score >= 0.6) return 'medium';
        return 'low';
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    showError(message) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert-danger');
        existingAlerts.forEach(alert => alert.remove());
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(alertDiv, document.getElementById('comparisonForm'));
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    async downloadReport(type) {
        try {
            const url = `/api/download/${type}?output_dir=${encodeURIComponent(this.currentOutputDir)}`;
            const response = await fetch(url);
            
            if (response.ok) {
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = response.headers.get('content-disposition')?.split('filename=')[1] || `report.${type}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(downloadUrl);
                
                // Show success message
                this.showSuccess(`Report downloaded successfully!`);
            } else {
                const error = await response.json();
                this.showError(error.error || 'Download failed');
            }
        } catch (error) {
            this.showError('Download failed: ' + error.message);
        }
    }

    showSuccess(message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-check-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(alertDiv, document.getElementById('comparisonForm'));
        }
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.rsiApp = new RSIComparisonApp();
    
    // Make download functions globally available
    window.downloadReport = (type) => window.rsiApp.downloadReport(type);
});

// Add some utility functions
window.utils = {
    formatFileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};
