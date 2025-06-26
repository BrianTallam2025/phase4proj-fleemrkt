// frontend/src/pages/Dashboard.jsx
// This component serves as the main user dashboard,
// allowing users to post items, view available items,
// and manage their sent/received item requests.

import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
// Import all necessary API functions from api.js
import { getProtectedData, createItem, getItems, createRequest, getSentRequests, getReceivedRequests, updateRequestStatus } from '../api.js'; 

// IMPORTANT: This file does NOT contain explicit validation logic (like Yup/Zod).
// If you are still seeing "Subject must be a string" or similar validation messages,
// that validation is being applied by an external library or a custom component
// wrapping these inputs, which is not part of this file's code.

function Dashboard() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  // State for item creation form
  const [itemTitle, setItemTitle] = useState('');
  const [itemDescription, setItemDescription] = useState('');
  const [itemCategory, setItemCategory] = useState('');
  const [itemLocation, setItemLocation] = useState('');
  const [itemImage, setItemImage] = useState(''); // Stores the Image URL string

  // State for displaying data
  const [items, setItems] = useState([]);
  const [sentRequests, setSentRequests] = useState([]);
  const [receivedRequests, setReceivedRequests] = useState([]);

  // State for form errors and validation messages
  const [formError, setFormError] = useState('');
  // Note: validationErrors state is here for a pattern, but its display in JSX
  // assumes a validation library injecting specific errors based on field names.
  const [validationErrors, setValidationErrors] = useState({}); 

  // Fetch initial dashboard data (protected data, items, requests)
  useEffect(() => {
    if (!isAuthenticated) {
      // If not authenticated, redirect to login page
      navigate('/login');
      return;
    }

    const fetchData = async () => {
      try {
        // Fetch protected data to confirm authentication and get user details
        const resProtected = await getProtectedData();
        // Assuming resProtected.data.logged_in_as has a username property
        // This is often just for displaying "Logged in as:"
        // setMessage(resProtected.data.logged_in_as.username); 

        // Fetch all available items
        const resItems = await getItems();
        setItems(resItems.data);

        // Fetch requests sent by the current user
        const resSentRequests = await getSentRequests();
        setSentRequests(resSentRequests.data);

        // Fetch requests received for the current user's items
        const resReceivedRequests = await getReceivedRequests();
        setReceivedRequests(resReceivedRequests.data);

      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        // Display user-friendly error message
        setFormError(err.response?.data?.msg || "Failed to load dashboard data. Please refresh.");
        // If the error is due to an invalid/expired token, log out the user
        if (err.response?.status === 401 || err.response?.status === 403) {
          logout(); 
          navigate('/login');
        }
      }
    };

    fetchData();
  }, [isAuthenticated, navigate, logout]); // Re-run effect if auth status changes

  // Handler for user logout
  const handleLogout = () => {
    logout(); // Calls logout from AuthContext, which handles backend and client-side logout
    navigate('/login');
  };

  // Handler for creating a new item
  const handleCreateItem = async (e) => {
    e.preventDefault(); // Prevent default form submission
    setFormError(''); // Clear any previous general form errors
    setValidationErrors({}); // Clear any previous field-specific validation errors

    const newItem = {
      title: itemTitle,
      description: itemDescription,
      category: itemCategory,
      location: itemLocation,
      image_url: itemImage, // Use the state for image URL
    };

    console.log("Attempting to create item with data:", newItem); // Debugging log

    try {
      // Call the API function to create the item
      await createItem(newItem);
      alert('Item created successfully!'); // User feedback

      // Clear form fields after successful submission
      setItemTitle('');
      setItemDescription('');
      setItemCategory('');
      setItemLocation('');
      setItemImage('');

      // Re-fetch items to update the list on the dashboard
      const res = await getItems();
      setItems(res.data);
    } catch (err) {
      console.error("Error creating item:", err);
      // Log full backend error details for debugging
      if (err.response && err.response.data) {
        console.error("Backend 422/Error details:", err.response.data);
        setFormError(err.response.data.msg || JSON.stringify(err.response.data) || 'Failed to create item due to validation.');
      } else {
        setFormError(err.message || 'Failed to create item. Network error or unknown problem.');
      }
    }
  };

  // Handler for sending an item request
  const handleRequestItem = async (itemId, itemOwnerUsername) => {
    // Confirmation dialog before sending request
    if (!window.confirm(`Are you sure you want to request "${items.find(item => item.id === itemId)?.title}" from ${itemOwnerUsername}?`)) {
      return;
    }
    try {
      await createRequest(itemId); // Call API to create request
      alert('Request sent successfully!');

      // Re-fetch sent requests to update the list
      const resSentRequests = await getSentRequests();
      setSentRequests(resSentRequests.data);
    } catch (err) {
      const errorMessage = err.response?.data?.msg || 'Failed to send request.';
      alert(`Error: ${errorMessage}`);
      console.error("Error sending request:", err);
    }
  };

  // Handler for updating a request's status (accept/reject)
  const handleUpdateRequestStatus = async (requestId, status) => {
    // Confirmation dialog
    if (!window.confirm(`Are you sure you want to ${status} this request?`)) {
      return;
    }
    try {
      await updateRequestStatus(requestId, status); // Call API to update request status
      alert(`Request ${status} successfully!`);

      // Re-fetch received requests to update the list
      const resReceivedRequests = await getReceivedRequests();
      setReceivedRequests(resReceivedRequests.data);
      // Optional: If item is accepted, you might want to mark it unavailable
      // This would require another API call to update the item's is_available status.
    } catch (err) {
      const errorMessage = err.response?.data?.msg || 'Failed to update request status.';
      alert(`Error: ${errorMessage}`);
      console.error("Error updating request status:", err);
    }
  };

  // Render loading state or null if not authenticated (AuthContext handles redirection)
  if (!isAuthenticated) {
    return null; 
  }

  return (
    <div className="min-h-screen p-6 bg-gray-50 font-inter">
      <header className="flex flex-wrap justify-between items-center bg-white p-4 rounded-lg shadow-md mb-6 gap-4">
        <h1 className="text-2xl font-bold text-gray-800">User Dashboard</h1>
        <div className="flex items-center space-x-4">
          <span className="text-gray-700">Logged in as: <span className="font-semibold text-blue-600">{user?.username} ({user?.role})</span></span>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition duration-150 ease-in-out"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Post New Item Section */}
        <section className="md:col-span-1 bg-white p-6 rounded-lg shadow-md h-fit">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Post a New Item</h2>
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
              {validationErrors.title && <p className="text-red-600 text-sm">{validationErrors.title}</p>}
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
              {validationErrors.description && <p className="text-red-600 text-sm">{validationErrors.description}</p>}
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
              {validationErrors.category && <p className="text-red-600 text-sm">{validationErrors.category}</p>}
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
              {validationErrors.location && <p className="text-red-600 text-sm">{validationErrors.location}</p>}
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
              {validationErrors.image_url && <p className="text-red-600 text-sm">{validationErrors.image_url}</p>}
            </div>
            {formError && <p className="text-red-600 text-sm">{formError}</p>}
            <button type="submit" className="w-full px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out">
              Post Item
            </button>
          </form>
        </section>

        {/* Available Items Section */}
        <section className="md:col-span-2 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Available Items</h2>
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
                      // Fallback image if the provided URL fails to load
                      onError={(e) => { e.target.onerror = null; e.target.src = `https://placehold.co/150x100/A0AEC0/FFFFFF?text=No+Image`; }}
                    />
                  )}
                  <h3 className="text-lg font-medium text-gray-800">{item.title}</h3>
                  <p className="text-sm text-gray-600 line-clamp-2">{item.description}</p>
                  <p className="text-xs text-gray-500 mt-1">Category: {item.category}</p>
                  {item.location && <p className="text-xs text-gray-500">Location: {item.location}</p>}
                  <p className="text-xs text-gray-500">Posted by: {item.owner_username}</p>
                  {user.id !== item.user_id ? ( // Don't show request button for own items
                    <button
                      onClick={() => handleRequestItem(item.id, item.owner_username)}
                      className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out"
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
        {/* Sent Requests Section */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Your Sent Requests</h2>
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

        {/* Received Requests Section */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Requests for Your Items</h2>
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
                        className="px-3 py-1 bg-green-600 text-white rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-150 ease-in-out text-sm"
                      >
                        Accept
                      </button>
                      <button
                        onClick={() => handleUpdateRequestStatus(req.request_id, 'rejected')}
                        className="px-3 py-1 bg-red-600 text-white rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition duration-150 ease-in-out text-sm"
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
