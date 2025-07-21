import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000"; // Backend API URL

function Dashboard() {
  const [sqlInput, setSqlInput] = useState("");
  const [apiResult, setApiResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [askInput, setAskInput] = useState("");
  const [askResult, setAskResult] = useState(null);
  const [error, setError] = useState(null);

  const runSqlQuery = async () => {
    if (!sqlInput.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await axios.get(`${API_BASE}/query`, { params: { sql: sqlInput } });
      setApiResult(resp.data);
    } catch (err) {
      console.error(err);
      setError("Failed to run SQL query.");
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async (qOverride) => {
    const question = qOverride ?? askInput;
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await axios.get(`${API_BASE}/ask`, { params: { question } });
      setAskResult(resp.data);
    } catch (err) {
      console.error(err);
      setError("Failed to ask question.");
    } finally {
      setLoading(false);
    }
  };

  const quickAsk = (q) => {
    setAskInput(q);
    askQuestion(q);
  };

  const renderResultTable = (data) => {
    if (!Array.isArray(data) || data.length === 0) return <p>No rows.</p>;
    return (
      <table border="1" cellPadding="4" style={{ marginTop: "10px" }}>
        <thead>
          <tr>
            {data[0].map((_, i) => (
              <th key={i}>col_{i}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rIdx) => (
            <tr key={rIdx}>
              {row.map((val, cIdx) => (
                <td key={cIdx}>{String(val)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  return (
    <div style={{ padding: "20px", maxWidth: "900px", margin: "0 auto" }}>
      <h1>E‑commerce Data Agent</h1>

      <div style={{ marginBottom: "20px" }}>
        <button onClick={() => quickAsk("What is my total sales?")}>Total Sales</button>{" "}
        <button onClick={() => quickAsk("Calculate the RoAS")}>RoAS</button>{" "}
        <button onClick={() => quickAsk("Which product had the highest CPC?")}>Highest CPC</button>
      </div>

      <div style={{ marginBottom: "30px" }}>
        <h2>Ask a Question</h2>
        <input
          type="text"
          value={askInput}
          onChange={(e) => setAskInput(e.target.value)}
          placeholder="e.g., What is my total sales?"
          style={{ width: "70%", marginRight: "10px" }}
        />
        <button onClick={() => askQuestion()}>Ask</button>
        {askResult && (
          <pre style={{ marginTop: "10px", background: "#111", color: "#0f0", padding: "10px", overflowX: "auto" }}>
            {JSON.stringify(askResult, null, 2)}
          </pre>
        )}
      </div>

      <div style={{ marginBottom: "30px" }}>
        <h2>Run Raw SQL</h2>
        <textarea
          rows={4}
          style={{ width: "100%" }}
          placeholder="SELECT * FROM ad_sales_metrics LIMIT 5;"
          value={sqlInput}
          onChange={(e) => setSqlInput(e.target.value)}
        />
        <br />
        <button onClick={runSqlQuery}>Run SQL</button>
        {apiResult && (
          <div style={{ marginTop: "10px" }}>
            <h3>Result</h3>
            {renderResultTable(apiResult.result)}
            <pre style={{ marginTop: "10px", background: "#222", color: "#fff", padding: "10px", overflowX: "auto" }}>
              {JSON.stringify(apiResult, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <div>
        <h2>Daily Sales Chart</h2>
        <img
          src={`${API_BASE}/chart?cb=${Date.now()}`}
          alt="Daily Sales Chart"
          style={{ maxWidth: "100%" }}
        />
      </div>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default Dashboard;
