import React, { useState } from "react";
import Header from "./Header";
import "./FileToFileSummarizer.css"; // or "./ReadmeGenerator.css"

const FileToFileSummarizer = () => {
  const [githubUrl, setGithubUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [summaryContent, setSummaryContent] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [step, setStep] = useState("input");

  const isValidGitHubUrl = (url) => {
    const githubUrlRegex =
      /^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\/?$/;
    return githubUrlRegex.test(url);
  };

  const generateSummary = async () => {
    if (!githubUrl.trim()) {
      setError("Please enter a GitHub repository URL");
      return;
    }
    if (!isValidGitHubUrl(githubUrl)) {
      setError("Please enter a valid GitHub repository URL");
      return;
    }
    setLoading(true);
    setError("");
    setSuccess("");
    setStep("generating");
    try {
      const response = await fetch("/api/file-summary/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ githubUrl: githubUrl.trim() }),
      });
      const data = await response.json();
      if (!data.success) {
        setError(data.error || "Failed to generate summary");
        setStep("input");
        return;
      }
      setSummaryContent(data.data.summary_content);
      setStep("complete");
      setSuccess("Summary generated successfully!");
    // eslint-disable-next-line no-unused-vars
    } catch (err) {
      setError("Failed to generate summary. Please try again.");
      setStep("input");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(summaryContent);
      setSuccess("Summary copied to clipboard!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(`Failed to copy to clipboard: ${err.message}`);
    }
  };

  const downloadSummary = () => {
    const blob = new Blob([summaryContent], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "repo_file_summaries_flash.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setSuccess("Summary downloaded successfully!");
    setTimeout(() => setSuccess(""), 3000);
  };

  const reset = () => {
    setGithubUrl("");
    setSuccess("");
    setError("");
    setSummaryContent("");
    setStep("input");
  };

  return (
    <div className="readmegen-outer-bg">
      <Header />
      <div className="readmegen-container">
        <div className="header">
          <h1>File-to-File Summarizer</h1>
          <p>Generate, preview, copy, or download a Markdown summary of every file in any GitHub repository using AI</p>
        </div>

        {error && <div className="alert error">{error}</div>}
        {success && <div className="alert success">{success}</div>}

        {step === "input" && (
          <div className="card" style={{ textAlign: "left" }}>
            <h2>Enter GitHub Repository</h2>
            <div className="form-group">
              <label>GitHub Repository URL</label>
              <input
                type="url"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                placeholder="https://github.com/username/repository-name"
                disabled={loading}
              />
            </div>
            <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
              <button
                onClick={generateSummary}
                disabled={loading}
                style={{ padding: '0.5rem 1rem' }}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span> Generating Summary...
                  </>
                ) : (
                  "Generate Summary"
                )}
              </button>
            </div>
          </div>
        )}

        {step === "generating" && (
          <div className="card center">
            <div className="loader"></div>
            <h2>Generating Your File Summaries...</h2>
            <p>Please wait while we analyze your code.</p>
          </div>
        )}

        {step === "complete" && summaryContent && (
          <div className="card">
            <h2>Summary Generated Successfully!</h2>
            <div className="actions">
              <button onClick={copyToClipboard}>Copy</button>
              <button onClick={downloadSummary}>Download</button>
              <button onClick={reset}>New Summary</button>
            </div>
            <div className="preview-container">
              <pre className="preview">{summaryContent}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileToFileSummarizer;
