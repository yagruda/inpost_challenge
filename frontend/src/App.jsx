import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Package } from 'lucide-react';
import { SearchBox, ReasoningFeed } from './components/SearchPanel';
import { LockerMap } from './components/LockerMap';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [llmMode, setLlmMode] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/status`)
      .then(res => setLlmMode(res.data.llm_mode))
      .catch(() => {});
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const res = await axios.post(`${API_BASE_URL}/api/search`, { query });
      setResults(res.data);
    } catch (err) {
      const status = err.response?.status;
      const detail = err.response?.data?.detail;
      setError({ status, message: detail || err.message || 'An error occurred during search.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F3F4F6] font-sans text-[#1F2937]">
      <header className="bg-[#FFCC00] shadow-md py-4 px-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Package size={32} className="text-[#1F2937]" />
          <h1 className="text-2xl font-bold tracking-tight">Yurii's 🔍 Smart finder MVP </h1>
        </div>
        <div className="text-sm font-semibold opacity-80">InPost 2026 Internship</div>
      </header>

      {llmMode === 'mock' && (
        <div className="bg-amber-50 border-b border-amber-200 px-8 py-2 flex items-center gap-2 text-amber-800 text-sm">
          <span className="text-base">⚠️</span>
          <span><strong>No Gemini API key found</strong> — using mock LLM extractor. Entity extraction is keyword-based only. Set <code className="bg-amber-100 px-1 rounded">GEMINI_API_KEY</code> in your <code className="bg-amber-100 px-1 rounded">.env</code> file for full AI extraction.</span>
        </div>
      )}

      <main className="container mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 flex flex-col gap-6">
          <SearchBox
            query={query}
            loading={loading}
            error={error}
            onQueryChange={setQuery}
            onSubmit={handleSearch}
          />
          {results && <ReasoningFeed reasoning={results.reasoning} />}
        </div>

        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden min-h-[600px] flex flex-col relative z-0">
          <LockerMap results={results} loading={loading} />
        </div>
      </main>
    </div>
  );
}

export default App;
