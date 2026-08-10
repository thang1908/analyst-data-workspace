import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  return (
    <div style={{ fontFamily: "Inter, sans-serif", padding: 32, background: "#0f172a", color: "#f8fafc", minHeight: "100vh" }}>
      <h1>Trusted CSV to Dashboard — Web Shell</h1>
      <p>FEAT-01 Data & Platform Foundation Baseline</p>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
