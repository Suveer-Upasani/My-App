from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from datetime import timedelta
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['SESSION_FILE_DIR'] = os.getenv('SESSION_FILE_DIR', '/path/to/default')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=4)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists('static'):
    os.makedirs('static')

@app.route("/")
def direct():
    session.permanent = True
    session.clear()
    return render_template('home.html')  

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get('file')
        if file and file.filename.endswith('csv'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            if os.path.getsize(file_path) == 0:
                return "Empty", 400

            try:
                df = pd.read_csv(file_path) 
                session['csv_data'] = df.to_dict(orient='records')
                return redirect(url_for('process_data'))

            except Exception as e:
                return f"Error processing CSV file: {str(e)}", 500
    return render_template('upload.html')

@app.route("/process", methods=["GET"])
def process_data():
    csv_data = session.get('csv_data', {})
    if not csv_data:
        return jsonify({"error": "No data to process"}), 400

    df = pd.DataFrame.from_dict(csv_data)
    try:
        plt.figure(figsize=(10, 10))
        df.plot(kind='bar', x=df.columns[0], y=df.columns[1:])
        plt.title('CSV in BAR format')
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        bar_plot_path = 'static/bar_plot.png'
        plt.savefig(bar_plot_path)
        plt.close()

        plt.figure(figsize=(10, 10))
        df.hist(bins=10)
        plt.title('CSV histogram')
        plt.xlabel(df.columns[0])
        plt.ylabel('Frequency')
        histogram_plot_path = 'static/histogram.png'
        plt.savefig(histogram_plot_path)
        plt.close()

        session['bar_plot'] = bar_plot_path
        session['histogram'] = histogram_plot_path

        return redirect(url_for('display'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/display")
def display():
    csv_data = session.get('csv_data', {})
    if not csv_data:
        return "No data to display", 400
    df = pd.DataFrame.from_dict(csv_data)
    rows = df.head().to_html()

    bar_plot = session.get('bar_plot')
    histogram = session.get('histogram')

    if not bar_plot or not histogram:
        return "No plots to display", 400

    return render_template("display.html", rows=rows, bar_plot=bar_plot, histogram=histogram)

if __name__ == "__main__":
    app.run(debug=True)
