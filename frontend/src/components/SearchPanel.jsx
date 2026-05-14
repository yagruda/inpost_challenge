import React from 'react';
import { Search, Loader2, Info } from 'lucide-react';

export function SearchBox({ query, loading, error, onQueryChange, onSubmit }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
      <h2 className="text-lg font-bold mb-4">Find a Locker</h2>
      <form onSubmit={onSubmit} className="flex flex-col gap-3">
        <div className="relative">
          <input
            type="text"
            placeholder="e.g. Find me a parcel locker near a grocery store in Warsaw"
            className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#FFCC00] focus:border-transparent transition-all"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
          />
          <Search className="absolute left-3 top-3.5 text-gray-400" size={20} />
        </div>
        <button
          type="submit"
          disabled={loading || !query}
          className="bg-[#1F2937] hover:bg-black text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
        >
          {loading ? <Loader2 className="animate-spin" size={20} /> : <Search size={20} />}
          {loading ? 'Analyzing...' : 'Search'}
        </button>
      </form>
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold px-1.5 py-0.5 bg-red-500 text-white rounded">
              {error.status ? `HTTP ${error.status}` : 'Error'}
            </span>
            <span className="text-sm font-semibold text-red-700">Request Failed</span>
          </div>
          <p className="text-sm text-red-600">{error.message}</p>
          <p className="text-xs text-red-400 mt-1">Try including a city and POI type, e.g. "locker near a park in Warsaw"</p>
        </div>
      )}
    </div>
  );
}

export function ReasoningFeed({ reasoning }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 flex-1 overflow-y-auto max-h-[600px]">
      <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
        <Info size={20} className="text-[#FFCC00]" /> AI Reasoning Feed
      </h2>
      <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
        {reasoning.map((step, index) => (
          <div key={index} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-slate-100 group-[.is-active]:bg-[#FFCC00] text-slate-500 group-[.is-active]:text-[#1F2937] shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
              {index + 1}
            </div>
            <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-slate-50 p-4 rounded-xl border border-slate-100 shadow-sm">
              <h3 className="font-bold text-sm mb-2">{step.step}</h3>
              <pre className="text-xs bg-slate-100 p-2 rounded text-slate-600 overflow-x-auto">
                {JSON.stringify(step.details, null, 2)}
              </pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
