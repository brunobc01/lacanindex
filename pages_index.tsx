import { useState } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface SearchResult {
  documentName: string;
  occurrences: number;
  excerpts: string[];
  fileType: 'PDF' | 'WORD';
  lastModified: string;
}

const DocumentSearchIndex = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [expandedDoc, setExpandedDoc] = useState<string | null>(null);

  // Mock data for demonstration
  const mockSearch = (term: string) => {
    setIsLoading(true);
    setTimeout(() => {
      const mockResults: SearchResult[] = [
        {
          documentName: 'Annual_Report_2023.pdf',
          occurrences: 12,
          excerpts: [
            '...the term appears in page 5 showing important metrics...',
            '...another occurrence in the financial section...',
          ],
          fileType: 'PDF',
          lastModified: '2023-12-01',
        },
        {
          documentName: 'Meeting_Minutes.docx',
          occurrences: 8,
          excerpts: [
            '...discussed during the board meeting...',
            '...mentioned in action items...',
          ],
          fileType: 'WORD',
          lastModified: '2024-01-15',
        },
        {
          documentName: 'Technical_Specs.pdf',
          occurrences: 15,
          excerpts: [
            '...detailed in the requirements section...',
            '...specifications include...',
          ],
          fileType: 'PDF',
          lastModified: '2024-02-01',
        },
      ];
      setResults(mockResults);
      setIsLoading(false);
    }, 1000);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      mockSearch(searchTerm);
    }
  };

  const getTotalOccurrences = () => {
    return results.reduce((sum, doc) => sum + doc.occurrences, 0);
  };

  const getFileTypeStats = () => {
    return results.reduce((acc, doc) => {
      acc[doc.fileType] = (acc[doc.fileType] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  };

  const chartData = results.map(result => ({
    name: result.documentName.substring(0, 15) + '...',
    occurrences: result.occurrences,
  }));

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Document Search Index</h1>
        
        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Enter search term..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50"
            >
              <MagnifyingGlassIcon className="w-5 h-5" />
              Search
            </button>
          </div>
        </form>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Searching documents...</p>
          </div>
        )}

        {/* Results Section */}
        {!isLoading && results.length > 0 && (
          <div className="space-y-8">
            {/* Statistics */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Search Statistics</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Total Documents</p>
                  <p className="text-2xl font-bold text-blue-600">{results.length}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Total Occurrences</p>
                  <p className="text-2xl font-bold text-blue-600">{getTotalOccurrences()}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">File Types</p>
                  <div className="text-sm">
                    {Object.entries(getFileTypeStats()).map(([type, count]) => (
                      <p key={type}>
                        {type}: <span className="font-semibold">{count}</span>
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Chart */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Occurrences by Document</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="occurrences" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Document List */}
            <div className="space-y-4">
              {results.map((result) => (
                <div key={result.documentName} className="bg-white p-6 rounded-lg shadow">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">{result.documentName}</h3>
                      <p className="text-sm text-gray-600">
                        Type: {result.fileType} | Last Modified: {result.lastModified}
                      </p>
                      <p className="text-sm text-gray-600">
                        Occurrences: <span className="font-semibold">{result.occurrences}</span>
                      </p>
                    </div>
                    <button
                      onClick={() => setExpandedDoc(expandedDoc === result.documentName ? null : result.documentName)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      {expandedDoc === result.documentName ? 'Hide Excerpts' : 'Show Excerpts'}
                    </button>
                  </div>
                  
                  {expandedDoc === result.documentName && (
                    <div className="mt-4 space-y-2">
                      {result.excerpts.map((excerpt, idx) => (
                        <div key={idx} className="p-3 bg-gray-50 rounded text-sm text-gray-700">
                          {excerpt}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Results State */}
        {!isLoading && searchTerm && results.length === 0 && (
          <div className="text-center py-8 text-gray-600">
            No results found for "{searchTerm}"
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentSearchIndex;