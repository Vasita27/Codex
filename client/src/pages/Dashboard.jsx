import { useState } from 'react';
import axios from 'axios';

function Dashboard() {
  const [repoUrl, setRepoUrl] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const token = localStorage.getItem('token');

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  const askQuestion = async () => {
    if (!repoUrl || !question) {
      alert('Please enter both the repository URL and your question.');
      return;
    }

    try {
      const response = await axios.post('http://localhost:5001/ask', {
        repoUrl,
        question
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      setAnswer(response.data.answer);
    } catch (error) {
      console.error('Error asking question:', error);
      alert('Something went wrong. Please check the repo URL or try again later.');
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>🔍 GitHub Repo Q&A Dashboard</h1>

      <div style={{ margin: '1rem 0' }}>
        <input
          type="text"
          placeholder="Enter GitHub repository URL"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          style={{ width: '400px', padding: '0.5rem', marginRight: '1rem' }}
        />

        <input
          type="text"
          placeholder="Ask a question about the repo"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={{ width: '400px', padding: '0.5rem' }}
        />
      </div>

      <button onClick={askQuestion} style={{ padding: '0.5rem 1rem', marginRight: '1rem' }}>
        Ask Question
      </button>

      <button onClick={handleLogout} style={{ padding: '0.5rem 1rem', backgroundColor: 'tomato', color: 'white' }}>
        Logout
      </button>

      {answer && (
        <div style={{ marginTop: '2rem' }}>
          <h3>💬 Answer:</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
