"""
Streamlit Web Application for RSI Comparison Tool
Provides a user-friendly web interface for comparing RSI documents
"""

import streamlit as st
import os
import tempfile
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from src.main import RSIComparisonTool

# Page configuration
st.set_page_config(
    page_title="RSI Comparison Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .section-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .similarity-high {
        color: #28a745;
        font-weight: bold;
    }
    .similarity-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .similarity-low {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔍 RSI Comparison Tool</h1>', unsafe_allow_html=True)
    st.markdown("Compare Regulatory Safety Information documents and identify missing content")
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        
        # Similarity threshold
        similarity_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Threshold for determining if content is similar enough to be considered present"
        )
        
        # Report formats
        st.subheader("Report Formats")
        generate_html = st.checkbox("HTML Report", value=True)
        generate_excel = st.checkbox("Excel Report", value=True)
        generate_pdf = st.checkbox("PDF Report", value=True)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool compares two RSI documents and identifies:
        - Missing sections
        - Missing content within sections
        - Similarity scores for each section
        
        **Supported formats:** PDF (digital and scanned)
        """)
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Comparator RSI (Reference)")
        comparator_file = st.file_uploader(
            "Upload Comparator RSI PDF",
            type=['pdf'],
            key='comparator'
        )
        
        if comparator_file:
            st.success(f"✅ Uploaded: {comparator_file.name}")
            
            # Show file info
            file_details = {
                "Filename": comparator_file.name,
                "File size": f"{comparator_file.size / 1024:.1f} KB",
                "File type": comparator_file.type
            }
            st.json(file_details)
    
    with col2:
        st.subheader("📋 Our RSI (To Check)")
        our_file = st.file_uploader(
            "Upload Our RSI PDF",
            type=['pdf'],
            key='our_rsi'
        )
        
        if our_file:
            st.success(f"✅ Uploaded: {our_file.name}")
            
            # Show file info
            file_details = {
                "Filename": our_file.name,
                "File size": f"{our_file.size / 1024:.1f} KB",
                "File type": our_file.type
            }
            st.json(file_details)
    
    # Comparison button
    if comparator_file and our_file:
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Comparison", type="primary", use_container_width=True):
                with st.spinner("Processing PDFs and comparing documents..."):
                    try:
                        # Save uploaded files to temporary directory
                        with tempfile.TemporaryDirectory() as temp_dir:
                            comparator_path = os.path.join(temp_dir, "comparator.pdf")
                            our_path = os.path.join(temp_dir, "our_rsi.pdf")
                            
                            with open(comparator_path, "wb") as f:
                                f.write(comparator_file.getbuffer())
                            with open(our_path, "wb") as f:
                                f.write(our_file.getbuffer())
                            
                            # Run comparison
                            tool = RSIComparisonTool(similarity_threshold)
                            results = tool.compare_rsis(comparator_path, our_path, temp_dir)
                            
                            # Store results in session state
                            st.session_state.comparison_results = results
                            st.session_state.comparison_completed = True
                            
                            st.success("✅ Comparison completed successfully!")
                            
                    except Exception as e:
                        st.error(f"❌ Error during comparison: {str(e)}")
                        st.session_state.comparison_completed = False
    
    # Display results
    if hasattr(st.session_state, 'comparison_completed') and st.session_state.comparison_completed:
        display_results(st.session_state.comparison_results, generate_html, generate_excel, generate_pdf)

def display_results(results, generate_html, generate_excel, generate_pdf):
    """Display comparison results"""
    
    comparison_results = results['comparison_results']
    summary = results['summary']
    
    # Summary metrics
    st.markdown("---")
    st.subheader("📊 Comparison Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Overall Similarity</h3>
            <h2>{summary['overall_similarity']:.1%}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Sections Compared</h3>
            <h2>{summary['total_sections_compared']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Sections with Issues</h3>
            <h2>{summary['sections_with_issues']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Missing Sections</h3>
            <h2>{len(summary['missing_sections'])}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Similarity chart
    st.subheader("📈 Section Similarity Scores")
    
    # Prepare data for chart
    chart_data = []
    for section_name, result in comparison_results.items():
        if not section_name.startswith('extra_'):
            chart_data.append({
                'Section': section_name.replace('_', ' ').title(),
                'Similarity': result.similarity_score,
                'Missing Items': len(result.missing_content),
                'Present Items': len(result.present_content)
            })
    
    if chart_data:
        df_chart = pd.DataFrame(chart_data)
        
        # Create bar chart
        fig = px.bar(
            df_chart,
            x='Section',
            y='Similarity',
            color='Similarity',
            color_continuous_scale='RdYlGn',
            title='Section Similarity Scores',
            labels={'Similarity': 'Similarity Score', 'Section': 'Section Name'}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed results
    st.subheader("🔍 Detailed Section Analysis")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Summary Table", "❌ Missing Content", "📄 Section Details"])
    
    with tab1:
        # Summary table
        summary_data = []
        for section_name, result in comparison_results.items():
            if not section_name.startswith('extra_'):
                summary_data.append({
                    'Section': section_name.replace('_', ' ').title(),
                    'Similarity': f"{result.similarity_score:.1%}",
                    'Missing Items': len(result.missing_content),
                    'Present Items': len(result.present_content),
                    'Method': result.comparison_method.replace('_', ' ').title()
                })
        
        if summary_data:
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True)
    
    with tab2:
        # Missing content
        missing_data = []
        for section_name, result in comparison_results.items():
            if not section_name.startswith('extra_') and result.missing_content:
                for item in result.missing_content:
                    missing_data.append({
                        'Section': section_name.replace('_', ' ').title(),
                        'Missing Content': item,
                        'Similarity': f"{result.similarity_score:.1%}"
                    })
        
        if missing_data:
            df_missing = pd.DataFrame(missing_data)
            st.dataframe(df_missing, use_container_width=True)
        else:
            st.info("🎉 No missing content found!")
    
    with tab3:
        # Detailed section view
        for section_name, result in comparison_results.items():
            if section_name.startswith('extra_'):
                continue
                
            with st.expander(f"{section_name.replace('_', ' ').title()} (Similarity: {result.similarity_score:.1%})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**❌ Missing Information:**")
                    if result.missing_content:
                        for i, item in enumerate(result.missing_content[:5]):
                            st.markdown(f"{i+1}. {item}")
                        if len(result.missing_content) > 5:
                            st.markdown(f"... and {len(result.missing_content) - 5} more items")
                    else:
                        st.success("No missing information")
                
                with col2:
                    st.markdown("**✅ Present Information:**")
                    if result.present_content:
                        for i, item in enumerate(result.present_content[:3]):
                            st.markdown(f"{i+1}. {item}")
                        if len(result.present_content) > 3:
                            st.markdown(f"... and {len(result.present_content) - 3} more items")
                    else:
                        st.warning("No present information")
                
                st.markdown(f"**Method:** {result.comparison_method.replace('_', ' ').title()}")
    
    # Download reports
    if generate_html or generate_excel or generate_pdf:
        st.subheader("📥 Download Reports")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if generate_html:
                html_content = generate_html_report(results)
                st.download_button(
                    label="📄 Download HTML Report",
                    data=html_content,
                    file_name=f"rsi_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html"
                )
        
        with col2:
            if generate_excel:
                excel_content = generate_excel_report(results)
                st.download_button(
                    label="📊 Download Excel Report",
                    data=excel_content,
                    file_name=f"rsi_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col3:
            if generate_pdf:
                pdf_content = generate_pdf_report(results)
                st.download_button(
                    label="📋 Download PDF Report",
                    data=pdf_content,
                    file_name=f"rsi_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )

def generate_html_report(results):
    """Generate HTML report content"""
    from src.report_generator import ReportGenerator
    
    report_gen = ReportGenerator()
    html_content = report_gen._generate_html_content(
        results['comparison_results'], 
        results['summary']
    )
    return html_content

def generate_excel_report(results):
    """Generate Excel report content"""
    # This would require more complex handling for binary data
    # For now, we'll create a simple Excel file
    import io
    
    # Create a simple Excel report
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Summary sheet
        summary_data = [
            ['Metric', 'Value'],
            ['Overall Similarity', f"{results['summary']['overall_similarity']:.1%}"],
            ['Total Sections Compared', results['summary']['total_sections_compared']],
            ['Sections with Issues', results['summary']['sections_with_issues']],
            ['Missing Sections', len(results['summary']['missing_sections'])]
        ]
        
        df_summary = pd.DataFrame(summary_data[1:], columns=summary_data[0])
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Detailed comparison sheet
        comparison_data = []
        for section_name, result in results['comparison_results'].items():
            if not section_name.startswith('extra_'):
                comparison_data.append([
                    section_name.replace('_', ' ').title(),
                    f"{result.similarity_score:.1%}",
                    result.comparison_method.replace('_', ' ').title(),
                    len(result.missing_content),
                    len(result.present_content)
                ])
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data, columns=[
                'Section', 'Similarity Score', 'Comparison Method', 
                'Missing Items Count', 'Present Items Count'
            ])
            df_comparison.to_excel(writer, sheet_name='Detailed Comparison', index=False)
    
    output.seek(0)
    return output.getvalue()

def generate_pdf_report(results):
    """Generate PDF report content"""
    # This would require more complex handling for binary data
    # For now, return a placeholder
    return b"PDF report generation not implemented in web interface"

if __name__ == "__main__":
    main()
