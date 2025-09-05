import pandas as pd
import matplotlib
matplotlib.use('Agg')                     # A non-interactive backend for Matplotlib that prevents it from trying to open a GUI window
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template
import io
import base64

# Initialize the Flask application
app = Flask(__name__)

def generate_plots():
    """
    This function contains the data analysis and plotting code from your script.
    It returns the plot images as base64 encoded strings.
    """
    # --- 1. Data Loading and Preparation ---
    try:
        df = pd.read_csv('Data_Detective.csv')
    except FileNotFoundError:
        return None, None # Handle case where file is not found

    df['Ad Spend (₹)'] = df['Ad Spend (₹)'].replace({'₹': '', ',': ''}, regex=True).astype(float)
    df['Cost Per Conversion'] = df.apply(
        lambda row: row['Ad Spend (₹)'] / row['Conversions'] if row['Conversions'] > 0 else 0,
        axis=1
    )

    # --- 2. Chart 1: Average Cost Per Conversion by Platform (Bar Chart) ---
    avg_cpc_by_platform = df.groupby('Platform')['Cost Per Conversion'].mean().sort_values()
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 6))
    ax1 = sns.barplot(x=avg_cpc_by_platform.index, y=avg_cpc_by_platform.values, palette='viridis')
    ax1.set_title('Chart 1: Average Cost Per Conversion (ROI) by Platform', fontsize=16, weight='bold')
    ax1.set_xlabel('Platform', fontsize=12)
    ax1.set_ylabel('Average Cost Per Conversion (₹)', fontsize=12)
    for p in ax1.patches:
        ax1.annotate(f'₹{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 9), textcoords='offset points', fontsize=12, weight='bold')
    
    # Save plot to a bytes buffer and encode it
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png', bbox_inches='tight')
    chart1_url = base64.b64encode(buf1.getbuffer()).decode('ascii')
    buf1.close()
    plt.close() # Close the plot to free memory

    # --- 3. Chart 2: Total Ad Spend vs. Total Conversions ---
    platform_summary = df.groupby('Platform').agg({'Ad Spend (₹)': 'sum', 'Conversions': 'sum'}).reset_index()
    fig, ax1_chart2 = plt.subplots(figsize=(12, 7))
    ax1_chart2.set_title('Chart 2: Total Ad Spend vs. Total Conversions by Platform', fontsize=16, weight='bold')
    ax1_chart2.set_xlabel('Platform', fontsize=12)
    ax1_chart2.set_ylabel('Total Ad Spend (₹)', color='skyblue')
    ax1_chart2.bar(platform_summary['Platform'], platform_summary['Ad Spend (₹)'], color='skyblue')
    ax1_chart2.tick_params(axis='y', labelcolor='skyblue')
    ax2_chart2 = ax1_chart2.twinx()
    ax2_chart2.set_ylabel('Total Conversions', color='tomato')
    ax2_chart2.plot(platform_summary['Platform'], platform_summary['Conversions'], color='tomato', marker='o', linewidth=2.5)
    ax2_chart2.tick_params(axis='y', labelcolor='tomato')
    fig.tight_layout()

    # Save plot to a bytes buffer and encode it
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', bbox_inches='tight')
    chart2_url = base64.b64encode(buf2.getbuffer()).decode('ascii')
    buf2.close()
    plt.close()

    return chart1_url, chart2_url

@app.route('/')
def home():
    """
    Main route for the web application.
    It calls the plotting function and renders the HTML template.
    """
    chart1, chart2 = generate_plots()
    
    insights = {
        "title": "Data Detective: Marketing Performance Analysis",
        "best_roi": "Google provides the best Return on Investment (ROI) with an average Cost Per Conversion (CPC) of approximately ₹801.",
        "needs_optimization": "Instagram is the platform most in need of optimization, driven by campaign CAM-09's extremely high CPC of ₹8,750.",
        "recommendation": "My primary recommendation is to re-evaluate the Instagram strategy, specifically pausing CAM-09, and reallocating that budget toward our top-performing platform, Google, to maximize overall conversions."
    }

    if chart1 is None:
        return "Error: Could not load the data file. Make sure the CSV is in the correct location."

    return render_template('index.html', insights=insights, chart1=chart1, chart2=chart2)

if __name__ == '__main__':
    # Runs the Flask app
    app.run(debug=True)
