import { useState, useEffect } from 'react';
import Head from 'next/head';

export default function Home() {
  const [workflows, setWorkflows] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    content_type: 'blog_post',
    topic: '',
    target_audience: 'general',
    tone: 'professional',
    length: 'medium',
    keywords: ''
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      const response = await fetch(`${API_URL}/workflows`);
      const data = await response.json();
      setWorkflows(data);
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const keywords = formData.keywords.split(',').map(k => k.trim()).filter(k => k);
      const response = await fetch(`${API_URL}/workflow/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          keywords
        })
      });
      
      if (response.ok) {
        setShowCreateForm(false);
        setFormData({
          content_type: 'blog_post',
          topic: '',
          target_audience: 'general',
          tone: 'professional',
          length: 'medium',
          keywords: ''
        });
        fetchWorkflows();
      }
    } catch (error) {
      console.error('Error creating workflow:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>BrainSait Agentic Workflow Dashboard</title>
      </Head>

      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">BrainSait Agentic Workflow</h1>
            </div>
            <div className="flex items-center">
              <button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
              >
                Create Workflow
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {showCreateForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Create New Workflow</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Content Type</label>
                <select
                  value={formData.content_type}
                  onChange={(e) => setFormData({...formData, content_type: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                >
                  <option value="blog_post">Blog Post</option>
                  <option value="course">Online Course</option>
                  <option value="social_post">Social Media Posts</option>
                  <option value="video_script">Video Script</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Topic</label>
                <input
                  type="text"
                  value={formData.topic}
                  onChange={(e) => setFormData({...formData, topic: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Target Audience</label>
                  <input
                    type="text"
                    value={formData.target_audience}
                    onChange={(e) => setFormData({...formData, target_audience: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Tone</label>
                  <select
                    value={formData.tone}
                    onChange={(e) => setFormData({...formData, tone: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="academic">Academic</option>
                    <option value="conversational">Conversational</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Keywords (comma-separated)</label>
                <input
                  type="text"
                  value={formData.keywords}
                  onChange={(e) => setFormData({...formData, keywords: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"
                  placeholder="AI, machine learning, automation"
                />
              </div>

              <div className="flex gap-4">
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
                >
                  Create Workflow
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Workflows</h2>
          <div className="space-y-4">
            {workflows.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No workflows yet. Create your first one!</p>
            ) : (
              workflows.map((workflow) => (
                <div key={workflow.id} className="border rounded-lg p-4 hover:shadow-md transition">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium">{workflow.topic}</h3>
                      <p className="text-sm text-gray-500 mt-1">
                        Type: {workflow.content_type.replace('_', ' ')}
                      </p>
                      <p className="text-sm text-gray-500">
                        Created: {new Date(workflow.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(workflow.status)}`}>
                      {workflow.status}
                    </span>
                  </div>
                  {workflow.status === 'completed' && (
                    <div className="mt-4 flex gap-2">
                      <button className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm">
                        View Results
                      </button>
                      <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">
                        Publish
                      </button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
