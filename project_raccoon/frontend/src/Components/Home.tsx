import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import axios from "axios";

const HomePage: React.FC = () => {
  const [groupName, setGroupName] = useState("income");
  const [numClients, setNumClients] = useState<number | "">("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!groupName.trim()) {
      setError("Group name is required");
      return;
    }
    if (numClients === "" || numClients <= 0) {
      setError("Number of clients must be a positive number");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5000/simulate', {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          group_name: groupName,
          num_clients: numClients,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to create group");
      }

      localStorage.setItem("group_name", groupName);

      navigate("/dashboard", {
        state: {
          group_name: groupName,
          num_clients: numClients,
        },
      });
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleExit = async () => {
    try{
      const res = await axios.post(`http://127.0.0.1:5000/exit`, {
        group_name: groupName
      });
      if (res.data.status !== 'success') {
        setError(res.data.message || 'backend error');
      }
    } catch (err: any) {
      setError(err.message || 'network error');
    }
    localStorage.removeItem("token");
    navigate('/');
  };

  return (
    <div className="home">
      <h1>Welcome to Project Raccoon</h1>
      <div className="top-right-buttons">
        <button className="exit" onClick={handleExit}>Exit</button>
        <button className="dash" onClick={() => navigate("/dashboard")}>Dashboard</button>
      </div>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="groupName">Select Group:</label>
          <select
            id="groupName"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            style={{ width: "100%", padding: 8, marginTop: 4 }}
          >
            <option value="income">income</option>
            <option value="credit">credit</option>
            <option value="smoking">smoking</option>
            <option value="lsd">lsd</option>
          </select>
        </div>
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="numClients">Number of Clients:</label>
          <input
            id="numClients"
            type="number"
            min={1}
            value={numClients}
            onChange={(e) =>
              setNumClients(e.target.value === "" ? "" : Number(e.target.value))
            }
            style={{ width: "100%", padding: 8, marginTop: 4 }}
            placeholder="Enter number of clients"
          />
        </div>
        {error && <div style={{ color: "red", marginBottom: 16 }}>{error}</div>}
        <button className="submit" type="submit" disabled={loading} style={{ padding: "8px 16px" }}>
          {loading ? "Submitting..." : "Submit"}
        </button>
      </form>
    </div>
  );
};

export default HomePage;
