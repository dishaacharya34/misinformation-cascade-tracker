import React from "react";
import { useRef, useState } from "react";
import { UploadCloud, FileSpreadsheet, X, LoaderCircle } from "lucide-react";

export default function FileUploader({ onAnalyze, loading = false }) {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");

  function selectFile(selected) {
    setError("");

    if (!selected) return;

    if (!selected.name.toLowerCase().endsWith(".csv")) {
      setError("Please choose a CSV file.");
      return;
    }

    if (selected.size > 10 * 1024 * 1024) {
      setError("The maximum file size is 10 MB.");
      return;
    }

    setFile(selected);
  }

  function handleDrop(event) {
    event.preventDefault();
    selectFile(event.dataTransfer.files?.[0]);
  }

  function handleAnalyze() {
    if (!file) {
      setError("Choose a CSV file first.");
      return;
    }

    onAnalyze(file);
  }

  return (
    <section
      className="panel uploader-panel"
      onDragOver={(event) => event.preventDefault()}
      onDrop={handleDrop}
    >
      <div className="panel-header">
        <div>
          <h3>Analyze a dataset</h3>
          <p>Upload social media posts or news claim data for automatic analysis.</p>
        </div>
        <div className="upload-icon">
          <UploadCloud size={21} />
        </div>
      </div>

      <button
        type="button"
        className="dropzone"
        onClick={() => inputRef.current?.click()}
        disabled={loading}
      >
        <div className="dropzone-icon">
          <UploadCloud size={27} />
        </div>
        <strong>Drop your CSV file here</strong>
        <span>or click to browse your computer</span>
        <small>CSV format · Maximum 10 MB</small>
      </button>

      <input
        ref={inputRef}
        type="file"
        accept=".csv,text/csv"
        hidden
        onChange={(event) => {
          selectFile(event.target.files?.[0]);
          event.target.value = "";
        }}
      />

      {file && (
        <div className="selected-file">
          <FileSpreadsheet size={20} />
          <div className="selected-file-info">
            <strong>{file.name}</strong>
            <span>{(file.size / 1024).toFixed(1)} KB</span>
          </div>
          <button
            type="button"
            className="icon-button"
            aria-label="Remove selected file"
            disabled={loading}
            onClick={() => {
              setFile(null);
              setError("");
            }}
          >
            <X size={17} />
          </button>
        </div>
      )}

      {error && <p className="error-message">{error}</p>}

      <button
        type="button"
        className="primary-button analyze-button"
        onClick={handleAnalyze}
        disabled={!file || loading}
      >
        {loading ? (
          <>
            <LoaderCircle size={17} className="spin" />
            Analyzing dataset...
          </>
        ) : (
          "Analyze dataset"
        )}
      </button>
    </section>
  );
}
