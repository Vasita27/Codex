import { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function Dashboard() {
  const [repoUrl, setRepoUrl] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [branches, setBranches] = useState([]);
  const [selectedBranch, setSelectedBranch] = useState('');
  const [isLoadingBranches, setIsLoadingBranches] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [error, setError] = useState('');

  const token = localStorage.getItem('token');

  useEffect(() => {
    // Reset branches when repo URL changes
    setBranches([]);
    setSelectedBranch('');
    setAnswer('');
    setError('');
  }, [repoUrl]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  const fetchBranches = async () => {
    if (!repoUrl) {
      setError('Please enter a repository URL first');
      return;
    }

    setIsLoadingBranches(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:5001/api/branches', {
        repoUrl
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (response.data.branches && response.data.branches.length > 0) {
        setBranches(response.data.branches);
        // Default to 'main' or 'master' if available
        const defaultBranch = response.data.branches.find(b => b.name === 'main') || 
                             response.data.branches.find(b => b.name === 'master') ||
                             response.data.branches[0];
        setSelectedBranch(defaultBranch.name);
      } else {
        setError('No branches found for this repository');
      }
    } catch (error) {
      console.error('Error fetching branches:', error);
      setError(error.response?.data?.error || 'Failed to fetch branches. Please check the repository URL and try again.');
    } finally {
      setIsLoadingBranches(false);
    }
  };

  const handleRepoUrlBlur = () => {
    if (repoUrl) {
      fetchBranches();
    }
  };

  const askQuestion = async () => {
    if (!repoUrl || !question || !selectedBranch) {
      setError('Please enter a repository URL, select a branch, and enter your question.');
      return;
    }

    setIsAsking(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:5001/ask', {
        repoUrl,
        branch: selectedBranch,
        question
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      setAnswer(response.data.answer);
    } catch (error) {
      console.error('Error asking question:', error);
      setError(error.response?.data?.error || 'Something went wrong. Please try again later.');
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>🔍 GitHub Repo Q&A Dashboard</h1>
        <button 
          onClick={handleLogout} 
          style={{ 
            padding: '0.5rem 1rem',
            background: '#f44336',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Logout
        </button>
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
            GitHub Repository URL
          </label>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              placeholder="https://github.com/username/repository"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              onBlur={handleRepoUrlBlur}
              style={{ 
                flex: 1, 
                padding: '0.75rem', 
                border: '1px solid #ddd', 
                borderRadius: '4px',
                fontSize: '1rem'
              }}
              disabled={isLoadingBranches || isAsking}
            />
          </div>
        </div>

        {isLoadingBranches && (
          <div style={{ margin: '0.5rem 0', color: '#666' }}>
            Loading branches...
          </div>
        )}

        {branches.length > 0 && (
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Select Branch
            </label>
            <select
              value={selectedBranch}
              onChange={(e) => setSelectedBranch(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '1rem',
                backgroundColor: 'white',
                marginBottom: '1rem'
              }}
              disabled={isAsking}
            >
              {branches.map((branch) => (
                <option key={branch.name} value={branch.name}>
                  {branch.name} {branch.protected ? '🔒' : ''} ({branch.commit_sha})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div style={{ marginBottom: '1.5rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
          Your Question
        </label>
        <textarea
          placeholder="Ask a question about this repository..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={{ 
            width: '100%', 
            minHeight: '120px', 
            padding: '0.75rem', 
            border: '1px solid #ddd', 
            borderRadius: '4px',
            fontSize: '1rem',
            fontFamily: 'inherit',
            marginBottom: '1rem',
            resize: 'vertical'
          }}
          disabled={!selectedBranch || isAsking}
        />
        
        <button 
          onClick={askQuestion} 
          disabled={!selectedBranch || !question.trim() || isAsking}
          style={{ 
            padding: '0.75rem 1.5rem', 
            background: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '1rem',
            opacity: (!selectedBranch || !question.trim() || isAsking) ? 0.7 : 1,
            transition: 'opacity 0.2s',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          {isAsking ? 'Processing...' : 'Ask Question'}
          {isAsking && <span className="spinner">⏳</span>}
        </button>
      </div>

      {error && (
        <div style={{ 
          padding: '1rem', 
          margin: '1rem 0', 
          backgroundColor: '#ffebee', 
          borderLeft: '4px solid #f44336',
          color: '#d32f2f',
          borderRadius: '4px'
        }}>
          {error}
        </div>
      )}

      {answer && (
        <div style={{ 
          marginTop: '2rem', 
          padding: '1.5rem', 
          border: '1px solid #e0e0e0', 
          borderRadius: '8px',
          backgroundColor: '#f9f9f9'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '1rem', color: '#333' }}>Answer:</h3>
          <div style={{ lineHeight: 1.6, fontSize: '1.05rem' }}>
            <ReactMarkdown>{answer}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
