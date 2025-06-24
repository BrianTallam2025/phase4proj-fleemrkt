import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getAllUsers, createAdminUser, adminGetAllRequests, adminDeleteRequest } from './api';

function Admin() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [allRequests, setAllRequests] = useState([]);
  const [newAdminUsername, setNewAdminUsername] = useState('');
  const [newAdminEmail, setNewAdminEmail] = useState('');
  const [newAdminPassword, setNewAdminPassword] = useState('');
  const [adminCreationMessage, setAdminCreationMessage] = useState('');
  const [adminCreationError, setAdminCreationError] = useState('');

  useEffect(() => {
    if (!isAuthenticated || user?.role !== 'admin') {
      alert('Access Denied: Admins only!');
      navigate('/');
      return;
    }

    const fetchData = async () => {
      try {
        const usersResponse = await getAllUsers();
        setUsers(usersResponse.data);

        const requestsResponse = await adminGetAllRequests();
        setAllRequests(requestsResponse.data);

      } catch (err) {
        console.error("Error fetching admin data:", err);
        alert(err.response?.data?.msg || "Failed to fetch admin data.");
        if (err.response?.status === 401 || err.response?.status === 403) {
          logout();
          navigate('/login');
        }
      }
    };
    fetchData();
  }, [isAuthenticated, user, navigate, logout]);

  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    setAdminCreationMessage('');
    setAdminCreationError('');
    try {
      const response = await createAdminUser({
        username: newAdminUsername,
        email: newAdminEmail,
        password: newAdminPassword,
      });
      setAdminCreationMessage(response.data.msg);
      setNewAdminUsername('');
      setNewAdminEmail('');
      setNewAdminPassword('');
      const updatedUsers = await getAllUsers();
      setUsers(updatedUsers.data);
    } catch (err) {
      console.error("Error creating admin user:", err);
      setAdminCreationError(err.response?.data?.msg || 'Failed to create admin user.');
    }
  };

  const handleDeleteRequest = async (requestId, itemTitle) => {
    if (!window.confirm(`Are you sure you want to delete the request for "${itemTitle}" (ID: ${requestId})? This cannot be undone.`)) {
      return;
    }
    try {
      await adminDeleteRequest(requestId);
      alert('Request deleted successfully!');
      const updatedRequests = await adminGetAllRequests();
      setAllRequests(updatedRequests.data);
    } catch (err) {
      const errorMessage = err.response?.data?.msg || 'Failed to delete request.';
      alert(`Error: ${errorMessage}`);
      console.error("Error deleting request:", err);
    }
  };

  if (!isAuthenticated || user?.role !== 'admin') {
    return null;
  }

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      <header className="flex flex-wrap justify-between items-center bg-white p-4 rounded-lg shadow-md mb-6 gap-4">
        <h1 className="text-2xl font-bold text-gray-800">Admin Panel</h1>
        <div className="flex items-center space-x-4">
          <span className="text-gray-700">Logged in as: <span className="font-semibold text-blue-600">{user?.username} ({user?.role})</span></span>
          <button
            onClick={() => { logout(); navigate('/login'); }}
            className="btn btn-danger"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="lg:col-span-1 card h-fit">
          <h2 className="text-xl font-semibold mb-4">Create New Admin User</h2>
          <form onSubmit={handleCreateAdmin} className="space-y-4">
            <div>
              <label htmlFor="newAdminUsername" className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <input
                type="text"
                id="newAdminUsername"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={newAdminUsername}
                onChange={(e) => setNewAdminUsername(e.target.value)}
                required
              />
            </div>
            <div>
              <label htmlFor="newAdminEmail" className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                id="newAdminEmail"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={newAdminEmail}
                onChange={(e) => setNewAdminEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <label htmlFor="newAdminPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                id="newAdminPassword"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={newAdminPassword}
                onChange={(e) => setNewAdminPassword(e.target.value)}
                required
              />
            </div>
            {adminCreationError && <p className="text-red-600 text-sm">{adminCreationError}</p>}
            {adminCreationMessage && <p className="text-green-600 text-sm">{adminCreationMessage}</p>}
            <button type="submit" className="btn btn-primary w-full">
              Create Admin
            </button>
          </form>
        </section>

        <section className="lg:col-span-2 card">
          <h2 className="text-xl font-semibold mb-4">All Users</h2>
          {users.length === 0 ? (
            <p className="text-gray-600">No users found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-200 rounded-lg">
                <thead>
                  <tr className="bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    <th className="px-4 py-2 border-b-2 border-gray-200">ID</th>
                    <th className="px-4 py-2 border-b-2 border-gray-200">Username</th>
                    <th className="px-4 py-2 border-b-2 border-gray-200">Email</th>
                    <th className="px-4 py-2 border-b-2 border-gray-200">Role</th>
                    <th className="px-4 py-2 border-b-2 border-gray-200">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-gray-50">
                      <td className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">{u.id}</td>
                      <td className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">{u.username}</td>
                      <td className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">{u.email}</td>
                      <td className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">{u.role}</td>
                      <td className="px-4 py-2 border-b border-gray-200 text-sm">
                        <button className="btn btn-secondary btn-sm mr-2">Edit</button>
                        <button className="btn btn-danger btn-sm">Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      <section className="mt-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">All Requests on Platform</h2>
          {allRequests.length === 0 ? (
            <p className="text-gray-600">No requests found on the platform.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-200 rounded-lg">
                <thead>
                  <tr className="bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    <th className="px-4 py-2 border-b-2 border-gray-200">Req ID</th>
                    <th className="px-4 py-2 border-b-2 border-gray-200">Item Title</th>
                    <th className="px-4 py-2 border-b-2 border-gray-200">Requester</th>
                    <th className="px-4 py-2 border-b-2 border-gray-200">Owner</th>
                    <th className="px-4 py-2 border-b-2 border-gray-200">Status</th>
                    <th className="px-4 py-2 border-b-2 border-gray-200">Requested At</th>
                    <th className="px-4 py-2 border-b-2 border-gray-200">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {allRequests.map((req) => (
                    <tr key={req.request_id} className="hover:bg-gray-50">
                      <td className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">{req.request_id}</td>
                      <td className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">{req.item_title}</td>
                      <td className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">{req.requester_username}</td>
                      <td className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">{req.item_owner_username}</td>
                      <td className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">
                        <span className={`font-semibold ${req.status === 'pending' ? 'text-yellow-600' : req.status === 'accepted' ? 'text-green-600' : 'text-red-600'}`}>
                          {req.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-2 border-b border-gray-200 text-sm text-gray-800">{new Date(req.requested_at).toLocaleDateString()}</td>
                      <td className="px-4 py-2 border-b border-gray-200 text-sm">
                        <button
                          onClick={() => handleDeleteRequest(req.request_id, req.item_title)}
                          className="btn btn-danger btn-sm"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default Admin;
