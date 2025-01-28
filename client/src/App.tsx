import React, { useState, useEffect } from 'react';
import { Settings, Users, MessageSquare, LogIn, UserPlus, RefreshCw, Utensils, MapPin, LogOut } from 'lucide-react';
import { CreateUserBody, UpdateUserBody } from './types';
import RestaurantMap from './components/RestaurantMap';
import { useLogin, useLogout } from './hooks/useAuth';
import { useUsers, useCreateUser, useUpdateUser } from './hooks/useUsers';
import { useChatHistory, useSendChat } from './hooks/useChat';

function App() {
  const [activeTab, setActiveTab] = useState<'chat' | 'users' | 'login' | 'map'>('map');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState<{ name: string; email: string } | null>(null);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUserInfo = localStorage.getItem('userInfo');
    
    if (savedToken && savedUserInfo) {
      setIsLoggedIn(true);
      setUserInfo(JSON.parse(savedUserInfo));
    }
  }, []);

  const { mutate: logout } = useLogout();

  const handleLogout = () => {
    logout();
    setIsLoggedIn(false);
    setUserInfo(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Utensils className="h-8 w-8 text-indigo-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">PANGYO HOT PLACE</span>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <button
                  onClick={() => setActiveTab('map')}
                  className={`${
                    activeTab === 'map'
                      ? 'border-indigo-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                >
                  <MapPin className="h-4 w-4 mr-2" />
                  Map
                </button>
                <button
                  onClick={() => setActiveTab('chat')}
                  className={`${
                    activeTab === 'chat'
                      ? 'border-indigo-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                >
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Chat
                </button>
                <button
                  onClick={() => setActiveTab('users')}
                  className={`${
                    activeTab === 'users'
                      ? 'border-indigo-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                >
                  <Users className="h-4 w-4 mr-2" />
                  Users
                </button>
                <div className="flex items-center">
                  {isLoggedIn && userInfo ? (
                    <div className="flex items-center space-x-4">
                      <div className="text-sm">
                        <span className="text-gray-500">안녕하세요,</span>
                        <span className="ml-1 font-medium text-gray-900">{userInfo.name}</span>
                      </div>
                      <button
                        onClick={handleLogout}
                        className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
                      >
                        <LogOut className="h-4 w-4 mr-2" />
                        Logout
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setActiveTab('login')}
                      className={`${
                        activeTab === 'login'
                          ? 'border-indigo-500 text-gray-900'
                          : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                    >
                      <LogIn className="h-4 w-4 mr-2" />
                      Login
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === 'map' && <RestaurantMap />}
        {activeTab === 'chat' && <ChatSection />}
        {activeTab === 'users' && <UsersSection isLoggedIn={isLoggedIn} />}
        {activeTab === 'login' && !isLoggedIn && (
          <LoginSection 
            onLogin={(userData) => {
              setIsLoggedIn(true);
              setUserInfo(userData);
              setActiveTab('map');
            }} 
          />
        )}
      </main>
    </div>
  );
}

function ChatSection() {
  const [question, setQuestion] = useState('');
  const { data: history = [], isLoading: historyLoading, error: historyError } = useChatHistory();
  const { mutate: sendChat, data: response, isError: sendError } = useSendChat();
  const token = localStorage.getItem('token');

  const handleSendChat = () => {
    sendChat(question);
    setQuestion('');
  };

  if (!token) {
    return (
      <div className="bg-white shadow sm:rounded-lg p-6">
        <p className="text-gray-500">Please log in to use the chat feature.</p>
      </div>
    );
  }

  if (historyLoading) {
    return (
      <div className="bg-white shadow sm:rounded-lg p-6">
        <p className="text-gray-500">Loading chat history...</p>
      </div>
    );
  }

  if (historyError || sendError) {
    return (
      <div className="bg-white shadow sm:rounded-lg p-6">
        <p className="text-red-500">Error loading chat. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow sm:rounded-lg p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Chat</h2>
      <div className="space-y-4">
        <div>
          <label htmlFor="question" className="block text-sm font-medium text-gray-700">
            Question
          </label>
          <div className="mt-1 flex rounded-md shadow-sm">
            <input
              type="text"
              name="question"
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="flex-1 min-w-0 block w-full px-3 py-2 rounded-md border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Ask a question..."
            />
            <button
              onClick={handleSendChat}
              className="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Send
            </button>
          </div>
        </div>

        <div>
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-sm font-medium text-gray-700">Chat History</h3>
          </div>
          <div className="bg-gray-50 rounded-md p-4">
            {history.length > 0 ? (
              <ul className="space-y-2">
                {history.map((item: unknown, index: number) => (
                  <li key={index} className="text-sm text-gray-600">
                    {JSON.stringify(item)}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No chat history available</p>
            )}
          </div>
        </div>

        {response && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Response</h3>
            <div className="bg-gray-50 rounded-md p-4">
              <pre className="text-sm text-gray-600">{JSON.stringify(response, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function UsersSection({ isLoggedIn }: { isLoggedIn: boolean }) {
  const [page, setPage] = useState(1);
  const { data: usersData, isLoading, error } = useUsers(page);
  const { mutate: createUser } = useCreateUser();
  const { mutate: updateUser } = useUpdateUser();
  
  const [createUserData, setCreateUserData] = useState<CreateUserBody>({
    name: '',
    email: '',
    password: '',
  });
  const [updateUserData, setUpdateUserData] = useState<UpdateUserBody>({
    name: '',
    password: '',
  });

  const handleCreateUser = () => {
    createUser(createUserData);
    setCreateUserData({ name: '', email: '', password: '' });
  };

  const handleUpdateUser = () => {
    updateUser(updateUserData);
    setUpdateUserData({ name: '', password: '' });
  };

  if (!isLoggedIn) {
    return (
      <div className="bg-white shadow sm:rounded-lg p-6">
        <p className="text-gray-500">Please log in to view and manage users.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="bg-white shadow sm:rounded-lg p-6">
        <p className="text-gray-500">Loading users...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white shadow sm:rounded-lg p-6">
        <p className="text-red-500">Error loading users. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow sm:rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Create User</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor="create-name" className="block text-sm font-medium text-gray-700">
              Name
            </label>
            <input
              type="text"
              id="create-name"
              value={createUserData.name}
              onChange={(e) => setCreateUserData({ ...createUserData, name: e.target.value })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="create-email" className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              type="email"
              id="create-email"
              value={createUserData.email}
              onChange={(e) => setCreateUserData({ ...createUserData, email: e.target.value })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div>
            <label htmlFor="create-password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              id="create-password"
              value={createUserData.password}
              onChange={(e) => setCreateUserData({ ...createUserData, password: e.target.value })}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={handleCreateUser}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <UserPlus className="h-4 w-4 mr-2" />
            Create User
          </button>
        </div>
      </div>

      {isLoggedIn && (
        <>
          <div className="bg-white shadow sm:rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Update User</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label htmlFor="update-name" className="block text-sm font-medium text-gray-700">
                  Name
                </label>
                <input
                  type="text"
                  id="update-name"
                  value={updateUserData.name || ''}
                  onChange={(e) => setUpdateUserData({ ...updateUserData, name: e.target.value })}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
              <div>
                <label htmlFor="update-password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <input
                  type="password"
                  id="update-password"
                  value={updateUserData.password || ''}
                  onChange={(e) => setUpdateUserData({ ...updateUserData, password: e.target.value })}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
              </div>
            </div>
            <div className="mt-4">
              <button
                onClick={handleUpdateUser}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Update User
              </button>
            </div>
          </div>

          <div className="bg-white shadow sm:rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium text-gray-900">Users List</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created At
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Updated At
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {usersData?.users.map((user: { id: string; name: string; email: string; created_at: string; updated_at: string }) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{user.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {user.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.updated_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex justify-between items-center">
              <div className="text-sm text-gray-700">
                Total users: {usersData?.total_count}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={usersData?.users.length < 10}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function LoginSection({ onLogin }: { onLogin: (userData: { name: string; email: string }) => void }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { mutate: login } = useLogin();

  const handleLogin = () => {
    login(
      { username, password },
      {
        onSuccess: (data) => {
          onLogin(data.user);
        },
        onError: (error) => {
          console.error('Login error:', error);
          alert('Login failed. Please check your credentials.');
        },
      }
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleLogin();
  };

  return (
    <div className="bg-white shadow sm:rounded-lg p-6 max-w-md mx-auto">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Login</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            Username
          </label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
        </div>
        <button
          type="submit"
          className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <LogIn className="h-4 w-4 mr-2" />
          Login
        </button>
      </form>
    </div>
  );
}

export default App;