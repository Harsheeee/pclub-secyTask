import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface Metric {
  client_id: string;
  accuracy: number;
  loss: number;
  timestamp: string;
  global_accuracy: number;
  global_loss: number;
}

const Dashboard: React.FC = () => {
  const navigate  = useNavigate();
  const groupName = localStorage.getItem('group_name') ?? '';

  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState('');

  const serverUrl = 'http://127.0.0.1:5000';

    useEffect(() => {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/login");
      }
    }, [navigate]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await axios.get(`${serverUrl}/metrics`, {
          params: { group_name: groupName }
        });
        if (res.data.status === 'success') {
          setMetrics(res.data.metrics as Metric[]);
          setError('');
        } else {
          setError(res.data.message || 'backend error');
        }
      } catch (err: any) {
        setError(err.message || 'network error');
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
    return () => {};
  }, [groupName]);


  const handleExit = async () => {
    try{
      const res = await axios.post(`${serverUrl}/exit`, {
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
    <div className='dashboard'>
      <div className="top-right-buttons">
        <button className="exit" onClick={handleExit}>Exit</button>
        <button className="backHome" onClick={() => navigate("/home")}>Home</button>
      </div>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <h2>Client Dashboard</h2>
      </div>
      <p><strong>Group:</strong> {groupName}</p>

      <h3>Training Metrics</h3>
      {loading && <p>Loading…</p>}
      {error   && <p style={{ color: 'red' }}>{error}</p>}

      {!loading && metrics.length === 0 && !error && <p>No metrics logged yet.</p>}

      {metrics.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Client</th>
              <th>Global Accuracy</th>
              <th>Global Loss</th>
              <th>Accuracy</th>
              <th>Loss</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {metrics.map((m, idx) => (
              <tr key={idx}>
                <td>{m.client_id}</td>
                <td>{m.global_accuracy.toFixed(4)}</td>
                <td>{m.global_loss.toFixed(4)}</td>
                <td>{m.accuracy.toFixed(4)}</td>
                <td>{m.loss.toFixed(4)}</td>
                <td>{new Date(m.timestamp).toLocaleTimeString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default Dashboard;
