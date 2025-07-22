import React, { useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

function Dashboard() {
  const [sqlInput, setSqlInput] = useState("");
  const [apiResult, setApiResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [askInput, setAskInput] = useState("");
  const [askResult, setAskResult] = useState(null);
  const [error, setError] = useState(null);

 
  const renderResultTable = (rows) => {
    if (!Array.isArray(rows) || rows.length === 0) {
      return <div>No rows.</div>;
    }

    
    const first = rows[0];
    const isObjectRow = !Array.isArray(first) && typeof first === "object";

    let headers = [];
    if (isObjectRow) {
      headers = Object.keys(first);
    } else if (Array.isArray(first)) {
      headers = first.map((_, i) => `col_${i}`);
    }

    return (
      <table
        style={{
          borderCollapse: "collapse",
          marginTop: 8,
          minWidth: "60%",
        }}
      >
        <thead>
          <tr>
            {headers.map((h, i) => (
              <th
                key={i}
                style={{
                  border: "1px solid #ccc",
                  padding: "4px 8px",
                  background: "#f0f0f0",
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rIdx) => (
            <tr key={rIdx}>
              {(isObjectRow ? headers.map((h) => row[h]) : row).map(
                (val, cIdx) => (
                  <td
                    key={cIdx}
                    style={{ border: "1px solid #ccc", padding: "4px 8px" }}
                  >
                    {String(val)}
                  </td>
                )
              )}
            </tr>
          ))}
        </tbody>
      </table>
    );
  };

  /* Backend Calls */

  const runSqlQuery = async () => {
    if (!sqlInput.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await axios.get(`${API_BASE}/query`, {
        params: { sql: sqlInput },
      });
      setApiResult(resp.data);
    } catch (err) {
      console.error(err);
      setError(
        `Failed to run SQL query. ${(err?.response?.data?.error) || ""}`.trim()
      );
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
      const resp = await axios.get(`${API_BASE}/ask`, {
        params: { question },
      });
      setAskResult(resp.data);
    } catch (err) {
      console.error(err);
      setError(
        `Failed to ask question. ${(err?.response?.data?.error) || ""}`.trim()
      );
    } finally {
      setLoading(false);
    }
  };

  const quickAsk = (q) => {
    setAskInput(q);
    askQuestion(q);
  };

  

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      {/* SQL Box */}
      <h2>SQL Query Box</h2>
      <input
        value={sqlInput}
        onChange={(e) => setSqlInput(e.target.value)}
        placeholder="Enter SQL, e.g.: SELECT * FROM ad_sales_metrics"
        style={{ width: "80%" }}
      />
      <button onClick={runSqlQuery} disabled={loading}>
        Run SQL
      </button>

      {apiResult && (
        <div style={{ marginTop: 16 }}>
          <h4>Result:</h4>
          {Array.isArray(apiResult.result)
            ? renderResultTable(apiResult.result)
            : (
              <pre style={{ background: "#eee", padding: 8, overflowX: "auto" }}>
                {JSON.stringify(apiResult, null, 2)}
              </pre>
            )}
        </div>
      )}

      {/* Ask NL */}
      <h2 style={{ marginTop: 40 }}>Ask a Natural Language Question</h2>
      <input
        value={askInput}
        onChange={(e) => setAskInput(e.target.value)}
        placeholder="Ask e.g. 'Total sales for item 101?'"
        style={{ width: "80%" }}
      />
      <button onClick={() => askQuestion()} disabled={loading}>
        Ask
      </button>

      <div style={{ margin: "12px 0" }}>
        <button onClick={() => quickAsk("What is my total sales?")}>
          Quick: Total Sales
        </button>
        <button onClick={() => quickAsk("Top 5 products by ad sales?")}>
          Quick: Top 5 Ad Sales
        </button>
        <button onClick={() => quickAsk("Which product had the highest CPC?")}>
          Quick: Highest CPC
        </button>
        <button onClick={() => quickAsk("Calculate the RoAS")}>
          Quick: RoAS
        </button>
      </div>

      {askResult && (
        <div style={{ marginTop: 16 }}>
          <h4>AI Result:</h4>
          {askResult.error && (
            <div style={{ color: "red", marginBottom: 8 }}>
              {askResult.error}
            </div>
          )}

          {askResult.summary && (
            <p>
              <strong>{askResult.summary}</strong>
            </p>
          )}

          {askResult.sql && (
            <div style={{ marginBottom: 8 }}>
              SQL used:
              <pre
                style={{
                  background: "#333",
                  color: "#fff",
                  padding: 8,
                  overflowX: "auto",
                }}
              >
                {askResult.sql}
              </pre>
            </div>
          )}

          {Array.isArray(askResult.rows)
            ? renderResultTable(askResult.rows)
            : askResult.answer && Array.isArray(askResult.answer)
              ? renderResultTable(askResult.answer)
              : null}
        </div>
      )}

      {/* Chart */}
      <h2 style={{ marginTop: 40 }}>Daily Sales Chart</h2>
      <img
        src={`${API_BASE}/chart?cb=${Date.now()}`}
        alt="Daily Sales Chart"
        style={{ maxWidth: "100%", border: "1px solid #ccc" }}
      />

      {/* Status */}
      {loading && <div>Loading...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
    </div>
  );
}

export default Dashboard;
