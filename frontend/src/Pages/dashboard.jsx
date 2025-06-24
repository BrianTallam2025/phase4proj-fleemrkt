import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { getProtectedData, createItem, getItems, createRequest, getSentRequests, getReceivedRequests, updateRequestStatus } from './api';

function Dashboard() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [itemTitle, setItemTitle] = useState('');
  const [itemDescription, setItemDescription] = useState('');
  const [itemCategory, setItemCategory] = useState('');
  const [itemLocation, setItemLocation] = useState('');
  const [itemImage, setItemImage] = useState('');
  const [items, setItems] = useState([]);
  const [sentRequests, setSentRequests] = useState([]);
  const [receivedRequests, setReceivedRequests] = useState([]);
  const [formError, setFormError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    const fetchData = async () => {
      try {
        const resProtected = await getProtectedData();
        setMessage(resProtected.data.logged_in_as.username);

        const resItems = await getItems();
        setItems(resItems.data);

        const resSentRequests = await getSentRequests();
        setSentRequests(resSentRequests.data);

        const resReceivedRequests = await getReceivedRequests();
        setReceivedRequests(resReceivedRequests.data);

      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setFormError(err.response?.data?.msg || "Failed to load data.");
        if (err.response?.status === 401 || err.response?.status === 403) {
          logout();
          navigate('/login');
        }
      }
    };
    fetchData();
  }, [isAuthenticated, navigate, logout]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleCreateItem = async (e) => {
    e.preventDefault();
    setFormError('');
    try {
      const newItem = {
        title: itemTitle,
        description: itemDescription,
        category: itemCategory,
        location: itemLocation,
        image_url: itemImage,
      };
      await createItem(newItem);
      alert('Item created successfully!');
      setItemTitle('');
      setItemDescription('');
      setItemCategory('');
      setItemLocation('');
      setItemImage('');
      const res = await getItems();
      setItems(res.data);
    } catch (err) {
      console.error("Error creating item:", err);
      setFormError(err.response?.data?.msg || 'Failed to create item.');
    }
  };

  const handleRequestItem = async (itemId, itemOwnerUsername) => {
    if (!window.confirm(`Are you sure you want to request "${items.find(item => item.id === itemId)?.title}" from ${itemOwnerUsername}?`)) {
      return;
    }
    try {
      await createRequest(itemId);
      alert('Request sent successfully!');
      const resSentRequests = await getSentRequests();
      setSentRequests(resSentRequests.data);
    } catch (err) {
      const errorMessage = err.response?.data?.msg || 'Failed to send request.';
      alert(`Error: ${errorMessage}`);
      console.error("Error sending request:", err);
    }
  };

  const handleUpdateRequestStatus = async (requestId, status) => {
    if (!window.confirm(`Are you sure you want to ${status} this request?`)) {
      return;
    }
    try {
      await updateRequestStatus(requestId, status);
      alert(`Request ${status} successfully!`);
      const resReceivedRequests = await getReceivedRequests();
      setReceivedRequests(resReceivedRequests.data);
    } catch (err) {
      const errorMessage = err.response?.data?.msg || 'Failed to update request status.';
      alert(`Error: ${errorMessage}`);
      console.error("Error updating request status:", err);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      <header className="flex flex-wrap justify-between items-center bg-white p-4 rounded-lg shadow-md mb-6 gap-4">
        <h1 className="text-2xl font-bold">User Dashboard</h1>
        <div className="flex items-center space-x-4">
          <span className="text-gray-700">Logged in as: <span className="font-semibold text-blue-600">{user?.username} ({user?.role})</span></span>
          <button
            onClick={handleLogout}
            className="btn btn-danger"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <section className="md:col-span-1 card h-fit">
          <h2 className="text-xl font-semibold mb-4">Post a New Item</h2>
          <form onSubmit={handleCreateItem} className="space-y-4">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title</label>
              <input
                type="text"
                id="title"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={itemTitle}
                onChange={(e) => setItemTitle(e.target.value)}
                required
              />
            </div>
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                id="description"
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={itemDescription}
                onChange={(e) => setItemDescription(e.target.value)}
                required
              ></textarea>
            </div>
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700">Category</label>
              <input
                type="text"
                id="category"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={itemCategory}
                onChange={(e) => setItemCategory(e.target.value)}
                required
              />
            </div>
            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700">Location (e.g., Neighborhood)</label>
              <input
                type="text"
                id="location"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={itemLocation}
                onChange={(e) => setItemLocation(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="image_url" className="block text-sm font-medium text-gray-700">Image URL (Optional)</label>
              <input
                type="text"
                id="image_url"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={itemImage}
                onChange={(e) => setItemImage(e.target.value)}
              />
            </div>
            {formError && <p className="text-red-600 text-sm">{formError}</p>}
            <button type="submit" className="btn btn-primary w-full">
              Post Item
            </button>
          </form>
        </section>

        <section className="md:col-span-2 card">
          <h2 className="text-xl font-semibold mb-4">Available Items</h2>
          {items.length === 0 ? (
            <p className="text-gray-600">No items available yet. Be the first to post!</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {items.map((item) => (
                <div key={item.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50 flex flex-col items-center text-center">
                  {item.image_url && (
                    <img
                      src={item.image_url}
                      alt={item.title}
                      className="w-full h-32 object-cover rounded-md mb-3"
                      onError={(e) => { e.target.onerror = null; e.target.src = `https://placehold.co/150x100/A0AEC0/FFFFFF?text=No+Image`; }}
                    />
                  )}
                  <h3 className="text-lg font-medium text-gray-800">{item.title}</h3>
                  <p className="text-sm text-gray-600 line-clamp-2">{item.description}</p>
                  <p className="text-xs text-gray-500 mt-1">Category: {item.category}</p>
                  {item.location && <p className="text-xs text-gray-500">Location: {item.location}</p>}
                  <p className="text-xs text-gray-500">Posted by: {item.owner_username}</p>
                  {user.id !== item.user_id ? (
                    <button
                      onClick={() => handleRequestItem(item.id, item.owner_username)}
                      className="btn btn-primary btn-sm mt-3"
                    >
                      Request Item
                    </button>
                  ) : (
                    <span className="text-xs text-blue-500 mt-3">Your Item</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Your Sent Requests</h2>
          {sentRequests.length === 0 ? (
            <p className="text-gray-600">You haven't sent any requests yet.</p>
          ) : (
            <div className="space-y-3">
              {sentRequests.map((req) => (
                <div key={req.request_id} className="border border-blue-200 rounded-lg p-3 bg-blue-50">
                  <p className="font-medium text-blue-800">{req.item_title}</p>
                  <p className="text-sm text-gray-700">To: <span className="font-semibold">{req.item_owner_username}</span></p>
                  <p className="text-sm text-gray-700">Status: <span className={`font-semibold ${req.status === 'pending' ? 'text-yellow-600' : req.status === 'accepted' ? 'text-green-600' : 'text-red-600'}`}>{req.status.toUpperCase()}</span></p>
                  <p className="text-xs text-gray-500">Requested On: {new Date(req.requested_at).toLocaleDateString()}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Requests for Your Items</h2>
          {receivedRequests.length === 0 ? (
            <p className="text-gray-600">No requests for your items yet.</p>
          ) : (
            <div className="space-y-3">
              {receivedRequests.map((req) => (
                <div key={req.request_id} className="border border-green-200 rounded-lg p-3 bg-green-50">
                  <p className="font-medium text-green-800">{req.item_title}</p>
                  <p className="text-sm text-gray-700">From: <span className="font-semibold">{req.requester_username}</span></p>
                  <p className="text-sm text-gray-700">Status: <span className={`font-semibold ${req.status === 'pending' ? 'text-yellow-600' : req.status === 'accepted' ? 'text-green-600' : 'text-red-600'}`}>{req.status.toUpperCase()}</span></p>
                  <p className="text-xs text-gray-500">Requested On: {new Date(req.requested_at).toLocaleDateString()}</p>
                  {req.status === 'pending' && (
                    <div className="flex space-x-2 mt-2">
                      <button
                        onClick={() => handleUpdateRequestStatus(req.request_id, 'accepted')}
                        className="btn btn-primary btn-sm"
                      >
                        Accept
                      </button>
                      <button
                        onClick={() => handleUpdateRequestStatus(req.request_id, 'rejected')}
                        className="btn btn-danger btn-sm"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default Dashboard;