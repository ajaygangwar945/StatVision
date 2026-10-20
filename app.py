import os
import io
import json
import html
import numpy as np
import pandas as pd
import plotly.express as px
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__, static_folder="static", template_folder="templates")

# Maximum upload payload size: 32MB
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {".csv", ".tsv", ".txt"}

@app.after_request
def add_security_headers(response):
    """Inject standard defensive HTTP security headers."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

def process_dataframe(df: pd.DataFrame, dataset_name: str, corr_threshold: float = 0.75):
    """Processes a pandas DataFrame, sanitizes columns, and computes quantitative moments."""
    # Limit to reasonable dimensions to prevent DoS attacks on server memory
    max_safe_cols = 100
    if df.shape[1] > max_safe_cols:
        df = df.iloc[:, :max_safe_cols]

    # Sanitize and HTML-escape all column names to block XSS
    df.columns = [html.escape(str(c).strip()) for c in df.columns]

    total_rows, total_cols = df.shape
    total_nulls = int(df.isnull().sum().sum())

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    # Sample rows (first 20) for table preview with sanitized strings
    sample_df = df.head(20).copy()
    sample_vectors = []
    for record in sample_df.to_dict(orient="records"):
        sanitized_record = {}
        for k, v in record.items():
            if pd.isna(v):
                sanitized_record[k] = "-"
            elif isinstance(v, str):
                sanitized_record[k] = html.escape(v)
            else:
                sanitized_record[k] = v
        sample_vectors.append(sanitized_record)

    # Mathematical moments & five-number summary
    moments_list = []
    if num_cols:
        desc = df[num_cols].describe().T
        # Calculate standard error SE = sigma / sqrt(n)
        desc["std_error"] = desc["std"] / np.sqrt(np.maximum(desc["count"], 1))
        for col, row in desc.iterrows():
            moments_list.append({
                "feature": str(col),
                "count": int(row["count"]) if not pd.isna(row["count"]) else 0,
                "mean": round(float(row["mean"]), 3) if not pd.isna(row["mean"]) else 0.0,
                "std": round(float(row["std"]), 3) if not pd.isna(row["std"]) else 0.0,
                "std_error": round(float(row["std_error"]), 3) if not pd.isna(row["std_error"]) else 0.0,
                "min": round(float(row["min"]), 3) if not pd.isna(row["min"]) else 0.0,
                "q1": round(float(row["25%"]), 3) if not pd.isna(row["25%"]) else 0.0,
                "median": round(float(row["50%"]), 3) if not pd.isna(row["50%"]) else 0.0,
                "q3": round(float(row["75%"]), 3) if not pd.isna(row["75%"]) else 0.0,
                "max": round(float(row["max"]), 3) if not pd.isna(row["max"]) else 0.0
            })

    # Statistical Inferences & Diagnostics
    insights = []
    # 1. Missing values
    if total_nulls > 0:
        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0]
        detail = ", ".join([f"<b>{c}</b> ({cnt})" for c, cnt in null_cols.items()])
        insights.append({
            "type": "danger",
            "pill": "NULL ~ ∅",
            "text": f"Missing values detected in vectors: {detail} (Total {total_nulls:,} null entries)."
        })

    # 2. Skewness
    if num_cols:
        for col in num_cols:
            try:
                skew_val = df[col].skew()
                if not pd.isna(skew_val) and abs(skew_val) > 1.0:
                    dir_text = "right-skewed (positive tail)" if skew_val > 0 else "left-skewed (negative tail)"
                    insights.append({
                        "type": "warning",
                        "pill": "SKEW ~ γ1",
                        "text": f"Feature <b>{col}</b> is {dir_text} (skewness = {skew_val:.2f}). Consider a logarithmic transform."
                    })
            except Exception:
                pass

    # 3. Correlation Matrix (cap to 50 columns to guarantee fast O(N^2) bounds)
    corr_data = None
    all_corrs = []
    safe_corr_cols = num_cols[:50]
    if len(safe_corr_cols) >= 2:
        corr_matrix = df[safe_corr_cols].corr().round(3)
        corr_data = {
            "columns": safe_corr_cols,
            "values": corr_matrix.values.tolist()
        }
        for i in range(len(safe_corr_cols)):
            for j in range(i + 1, len(safe_corr_cols)):
                r = corr_matrix.iloc[i, j]
                if not pd.isna(r):
                    all_corrs.append({
                        "col1": safe_corr_cols[i],
                        "col2": safe_corr_cols[j],
                        "r": round(float(r), 3)
                    })
                    if abs(r) >= corr_threshold:
                        rel_type = "positive" if r > 0 else "negative"
                        insights.append({
                            "type": "info",
                            "pill": "CORR ~ r",
                            "text": f"Strong {rel_type} linear dependence between <b>{safe_corr_cols[i]}</b> and <b>{safe_corr_cols[j]}</b> (r = {r:.2f} ≥ {corr_threshold:.2f})."
                        })

    if not insights:
        insights.append({
            "type": "success",
            "pill": "STATUS ~ ✓",
            "text": "Dataset appears well-conditioned: zero missing entries and low cross-collinearity observed."
        })

    # Chart data: sample up to 5,000 points to ensure smooth client-side WebGL/SVG rendering
    plot_df = df if len(df) <= 5000 else df.sample(5000, random_state=42)
    records = plot_df.replace({np.nan: None}).to_dict(orient="list")

    return {
        "dataset_name": html.escape(dataset_name),
        "rows": total_rows,
        "cols": total_cols,
        "num_cols": num_cols,
        "cat_cols": cat_cols,
        "nulls": total_nulls,
        "columns": df.columns.tolist(),
        "sample_vectors": sample_vectors,
        "moments": moments_list,
        "insights": insights,
        "all_corrs": all_corrs,
        "corr_matrix": corr_data,
        "records": records
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/sample/<name>")
def load_sample(name: str):
    name_clean = secure_filename(name).lower()
    if "iris" in name_clean:
        df = px.data.iris()
        ds_name = "Iris Morphometrics (p=4, N=150)"
    elif "tips" in name_clean or "hospitality" in name_clean:
        df = px.data.tips()
        ds_name = "Hospitality Economics (p=6, N=244)"
    else:
        return jsonify({"error": "Unknown sample dataset"}), 404

    result = process_dataframe(df, ds_name)
    return jsonify(result)

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    if not filename:
        filename = "uploaded_matrix.csv"

    _, ext = os.path.splitext(filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported file type. Only {', '.join(sorted(ALLOWED_EXTENSIONS))} files are supported."}), 400

    try:
        # Limit rows to 100,000 to defend against memory exhaustion DoS
        df = pd.read_csv(file, nrows=100000)
        if df.empty:
            return jsonify({"error": "The uploaded file contains no data rows."}), 400
        result = process_dataframe(df, filename)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to parse CSV file: {html.escape(str(e))}"}), 400

@app.route("/api/export-moments", methods=["POST"])
def export_moments():
    try:
        payload = request.get_json(force=True)
        moments = payload.get("moments", [])
        if not moments or not isinstance(moments, list):
            return jsonify({"error": "No moments data provided"}), 400
        
        df = pd.DataFrame(moments)
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        
        mem = io.BytesIO()
        mem.write(buf.getvalue().encode("utf-8"))
        mem.seek(0)
        
        return send_file(
            mem,
            as_attachment=True,
            download_name="statvision_moments.csv",
            mimetype="text/csv"
        )
    except Exception as e:
        return jsonify({"error": html.escape(str(e))}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true")
    app.run(host="0.0.0.0", port=port, debug=debug)
