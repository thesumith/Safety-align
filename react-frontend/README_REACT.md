# RSI Comparison Tool - React Frontend

A modern, responsive React.js frontend for the RSI Comparison Tool. This frontend provides an intuitive user interface for comparing Regulatory Safety Information documents with advanced features and beautiful visualizations.

## 🚀 Features

### Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Smooth Animations**: Powered by Framer Motion for delightful user interactions
- **Modern Styling**: Clean, professional design with gradient backgrounds and card-based layouts
- **Interactive Components**: Hover effects, loading states, and smooth transitions

### File Upload & Processing
- **Drag & Drop**: Intuitive file upload with visual feedback
- **File Validation**: Automatic PDF validation and error handling
- **Progress Indicators**: Real-time upload and processing status
- **Multiple File Support**: Upload comparator and target RSI documents

### Comparison Features
- **Split View**: Side-by-side comparison of documents
- **Full View**: Detailed section-by-section analysis
- **Interactive Sections**: Expandable/collapsible section details
- **Visual Indicators**: Color-coded similarity scores and status icons

### Results & Analytics
- **Summary Dashboard**: Key metrics and overview statistics
- **Interactive Charts**: Pie charts and bar charts using Recharts
- **Issues Tracking**: Highlighted sections needing attention
- **Download Options**: Excel and PDF report downloads

### Settings & Configuration
- **Similarity Threshold**: Adjustable comparison sensitivity
- **Report Formats**: Configurable output formats
- **Real-time Updates**: Instant feedback on setting changes

## 🛠️ Technology Stack

- **React 18**: Latest React with hooks and modern patterns
- **Framer Motion**: Smooth animations and transitions
- **React Dropzone**: Drag-and-drop file upload
- **Recharts**: Interactive data visualizations
- **Axios**: HTTP client for API communication
- **React Icons**: Comprehensive icon library
- **CSS3**: Modern styling with Flexbox and Grid

## 📦 Installation

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Running Flask backend (see main README.md)

### Setup Instructions

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm start
   ```

3. **Build for Production**:
   ```bash
   npm run build
   ```

4. **Run Tests**:
   ```bash
   npm test
   ```

## 🏗️ Project Structure

```
src/
├── components/           # React components
│   ├── Header.js        # Application header
│   ├── FileUpload.js    # File upload interface
│   ├── ComparisonView.js # Comparison results display
│   ├── ResultsDisplay.js # Analytics and downloads
│   ├── LoadingSpinner.js # Loading states
│   └── *.css            # Component-specific styles
├── App.js               # Main application component
├── App.css              # Global application styles
├── index.js             # Application entry point
└── index.css            # Global styles and utilities
```

## 🎨 Component Overview

### Header Component
- Application branding and navigation
- Feature highlights with icons
- Responsive design for mobile devices

### FileUpload Component
- Drag-and-drop file upload zones
- File validation and error handling
- Settings panel with similarity threshold
- Report format configuration

### ComparisonView Component
- Split view for side-by-side comparison
- Full view for detailed analysis
- Interactive section expansion
- Visual similarity indicators

### ResultsDisplay Component
- Summary statistics cards
- Interactive charts and visualizations
- Issues tracking and highlighting
- Report download functionality

### LoadingSpinner Component
- Animated loading states
- Progress indicators
- Step-by-step process visualization

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENVIRONMENT=development
```

### API Configuration
The frontend communicates with the Flask backend via:
- **Base URL**: `http://localhost:5000` (configurable via proxy)
- **Endpoints**:
  - `POST /api/compare` - Document comparison
  - `GET /api/download/{type}` - Report downloads

## 🎯 Key Features Explained

### Drag & Drop Upload
- Uses `react-dropzone` for intuitive file handling
- Visual feedback during drag operations
- Automatic file type validation
- Error handling for invalid files

### Interactive Charts
- **Pie Chart**: Shows similarity distribution across sections
- **Bar Chart**: Section-by-section comparison scores
- **Responsive**: Adapts to different screen sizes
- **Interactive**: Hover tooltips and legends

### Split View Comparison
- Side-by-side document comparison
- Synchronized scrolling between panels
- Expandable section details
- Visual indicators for missing content

### Real-time Updates
- Live similarity threshold adjustment
- Instant feedback on setting changes
- Progress indicators during processing
- Error handling with user-friendly messages

## 📱 Responsive Design

The application is fully responsive with:
- **Desktop**: Full-featured interface with side-by-side views
- **Tablet**: Optimized layouts with touch-friendly controls
- **Mobile**: Stacked layouts with simplified navigation

### Breakpoints
- **Desktop**: 1200px and above
- **Tablet**: 768px - 1199px
- **Mobile**: Below 768px

## 🎨 Styling System

### CSS Architecture
- **Component-scoped styles**: Each component has its own CSS file
- **Utility classes**: Global utility classes for common patterns
- **CSS Grid & Flexbox**: Modern layout techniques
- **CSS Variables**: Consistent theming and colors

### Color Scheme
- **Primary**: #3498db (Blue)
- **Secondary**: #2c3e50 (Dark Blue)
- **Success**: #28a745 (Green)
- **Warning**: #ffc107 (Yellow)
- **Danger**: #dc3545 (Red)
- **Neutral**: #6c757d (Gray)

## 🚀 Performance Optimizations

- **Code Splitting**: Automatic code splitting with React.lazy
- **Memoization**: React.memo for expensive components
- **Debounced Inputs**: Optimized form handling
- **Lazy Loading**: Components loaded on demand
- **Optimized Bundles**: Tree shaking and minification

## 🧪 Testing

### Running Tests
```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Snapshot Tests**: UI regression testing

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure Flask backend is running
   - Check proxy configuration in package.json

2. **File Upload Issues**:
   - Verify file is PDF format
   - Check file size limits
   - Ensure backend upload directory exists

3. **Chart Display Issues**:
   - Check browser compatibility
   - Verify data format from API
   - Ensure Recharts is properly installed

### Development Tips

1. **Hot Reloading**: Changes automatically reflect in browser
2. **Error Boundaries**: Graceful error handling in production
3. **Console Logging**: Detailed debugging information
4. **React DevTools**: Component inspection and debugging

## 📈 Future Enhancements

- **Real-time Collaboration**: Multi-user document comparison
- **Advanced Analytics**: Machine learning insights
- **Document Versioning**: Historical comparison tracking
- **API Integration**: Third-party document sources
- **Offline Support**: Progressive Web App features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the main README.md
- Open an issue on GitHub
- Contact the development team

---

**Built with ❤️ using React.js and modern web technologies**
